"""Ledger policy grouping tests without a device."""

import unittest
from hashlib import sha256
from unittest.mock import Mock

from hwilib.common import Chain
from hwilib.devices.ledger import LedgerClient
from hwilib.devices.ledger_bitcoin.client_base import PartialSignature
from hwilib.key import ExtendedKey, G, H_, KeyOriginInfo, point_mul, point_to_bytes
from hwilib.psbt import PSBT, PartiallySignedInput
from hwilib.tx import CTxOut


class TestLedgerPolicy(unittest.TestCase):
    def setUp(self):
        self.path = [H_(48), H_(0), H_(0), H_(2)]
        self.fingerprints = [bytes([i]) * 4 for i in range(1, 4)]
        self.accounts = [
            ExtendedKey(ExtendedKey.MAINNET_PUBLIC, 4, fp, H_(2),
                        sha256(fp).digest(), None, point_to_bytes(point_mul(G, i)))
            for i, fp in enumerate(self.fingerprints, 1)
        ]
        self.psbt = PSBT()
        self.psbt.version = 2
        self.psbt.xpub = {
            account.serialize(): KeyOriginInfo(fp, self.path)
            for account, fp in zip(self.accounts, self.fingerprints)
        }
        self.client = LedgerClient.__new__(LedgerClient)
        self.client.chain = Chain.MAIN
        self.client.client = Mock()
        self.client.client.get_master_fingerprint.return_value = self.fingerprints[0]
        self.client.client.register_wallet.side_effect = lambda wallet: (wallet.id, bytes(32))
        self.client.client.sign_psbt.side_effect = self.sign_psbt

    def add_input(self, index, threshold=2):
        pubs = [account.derive_pub_path([0, index]).pubkey for account in self.accounts]
        item = PartiallySignedInput(2)
        item.witness_script = (
            bytes([0x50 + threshold])
            + b''.join(b'\x21' + pub for pub in sorted(pubs))
            + b'\x53\xae'
        )
        item.witness_utxo = CTxOut(100_000, b'\x00\x20' + sha256(item.witness_script).digest())
        item.hd_keypaths = {
            pub: KeyOriginInfo(fp, self.path + [0, index])
            for pub, fp in zip(pubs, self.fingerprints)
        }
        self.psbt.inputs.append(item)
        return sorted(range(len(pubs)), key=lambda i: pubs[i])

    def sign_psbt(self, psbt, wallet, wallet_hmac):
        return [
            (i, PartialSignature(pubkey=pub, signature=b'test signature'))
            for i, item in enumerate(psbt.inputs)
            if item.witness_script[0] == 0x50 + wallet.threshold
            for pub, origin in item.hd_keypaths.items()
            if origin.fingerprint == self.fingerprints[0]
        ]

    def test_same_wallet_registers_and_signs_once(self):
        first_order = self.add_input(0)
        second_order = self.add_input(1)
        self.assertNotEqual(first_order, second_order)

        result = self.client.sign_tx(self.psbt)

        self.client.client.register_wallet.assert_called_once()
        self.client.client.sign_psbt.assert_called_once()
        self.assertTrue(all(len(item.partial_sigs) == 1 for item in result.inputs))

    def test_different_wallets_register_and_sign_separately(self):
        self.add_input(0, threshold=2)
        self.add_input(1, threshold=3)

        result = self.client.sign_tx(self.psbt)

        self.assertEqual(self.client.client.register_wallet.call_count, 2)
        self.assertEqual(self.client.client.sign_psbt.call_count, 2)
        self.assertTrue(all(len(item.partial_sigs) == 1 for item in result.inputs))


if __name__ == '__main__':
    unittest.main()
