"""THP compatibility tests without a device or persistent credentials."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from trezorlib import mapping, messages

from hwilib.devices._trezor_thp import TrezorThpClient
from hwilib.devices.trezorlib import mapping as legacy_mapping
from hwilib.devices.trezorlib import messages as legacy_messages


class TrezorThpFeaturesTest(unittest.TestCase):
    def test_features_preserve_new_capabilities(self):
        for capabilities in ([1, 17], [1, 17, 28], [1, 17, 28, 29, 999]):
            with self.subTest(capabilities=capabilities):
                native = messages.Features(
                    vendor='trezor.io', model='T3W1', label='Safe 7 emulator',
                    major_version=2, minor_version=13, patch_version=0,
                    initialized=True, unlocked=True, pin_protection=False,
                    passphrase_protection=True, capabilities=capabilities,
                    session_id=b'test session',
                )
                client = TrezorThpClient.__new__(TrezorThpClient)
                client.mapping = legacy_mapping.ProtobufMapping.from_module(legacy_messages)
                client._native = Mock()
                client._native.mapping = mapping.DEFAULT_MAPPING
                client._native.refresh_features.return_value = native
                client.model = SimpleNamespace(vendors=('trezor.io',), minimum_version=(2, 0, 0))

                features = client.refresh_features()

                self.assertIsInstance(features, legacy_messages.Features)
                self.assertIs(features, client.features)
                self.assertEqual(features.capabilities, capabilities)
                self.assertIn(legacy_messages.Capability.PassphraseEntry, features.capabilities)
                self.assertEqual(features.model, 'T3W1')
                self.assertEqual(features.label, 'Safe 7 emulator')
                self.assertTrue(features.initialized)
                self.assertTrue(features.unlocked)
                self.assertFalse(features.pin_protection)
                self.assertTrue(features.passphrase_protection)
                self.assertEqual(client.version, (2, 13, 0))
                self.assertEqual(client.session_id, b'test session')
                self.assertIsNone(features.session_id)
                self.assertEqual(native.session_id, b'test session')


if __name__ == '__main__':
    unittest.main()
