"""Adapt upstream trezorlib's THP sessions to HWI's existing Bitcoin workflows.

This module is loaded only after a device explicitly rejects protocol v1.
Keep the vendored client for older Trezors and KeepKey; use upstream trezorlib
for the THP handshake, pairing, encryption, retransmission, and sessions.
"""

import getpass
import json
import logging
import sys
from contextlib import contextmanager
from typing import Any, Callable, Iterator, List, Optional

import keyring
from trezorlib import device, exceptions, messages
from trezorlib.client import AppManifest, PassphraseSetting
from trezorlib.thp.client import ThpSession, TrezorClientThp
from trezorlib.thp.credentials import Credential, StaticCredential
from trezorlib.thp.pairing import default_pairing_flow
from trezorlib.transport import Transport as NativeTransport
from trezorlib.transport.udp import UdpTransport
from trezorlib.transport.webusb import WebUsbTransport

from ..errors import BadArgumentError, DeviceConnectionError, DeviceNotReadyError
from .trezorlib import mapping as legacy_mapping, messages as legacy_messages
from .trezorlib.client import TrezorClient as LegacyClient
from .trezorlib.exceptions import Cancelled
from .trezorlib.models import TrezorModel
from .trezorlib.protobuf import MessageType
from .trezorlib.transport import Transport
from .trezorlib.transport.udp import UdpTransport as LegacyUdpTransport
from .trezorlib.transport.webusb import WebUsbTransport as LegacyWebUsbTransport


LOG = logging.getLogger(__name__)
KEYRING_SERVICE = "hwi.trezor-thp"
_credentials: Optional[List[Credential]] = None


def _load_credentials() -> List[Credential]:
    global _credentials
    if _credentials is None:
        _credentials = []
        try:
            stored = keyring.get_password(KEYRING_SERVICE, "credentials")
            if stored:
                loaded = [
                    StaticCredential(
                        trezor_pubkey=bytes.fromhex(item["trezor_pubkey"]),
                        host_privkey=bytes.fromhex(item["host_privkey"]),
                        credential=bytes.fromhex(item["credential"]),
                    )
                    for item in json.loads(stored)
                ]
                if any(len(c.trezor_pubkey) != 32 or len(c.host_privkey) != 32 for c in loaded):
                    raise ValueError("Invalid THP credential key length")
                _credentials = loaded
        except Exception:
            # A headless host may have no keyring. Never fall back to plaintext.
            LOG.warning("Cannot load Trezor pairing credentials from the OS keyring; pairing may be required")
    return _credentials[:]


def _save_credential(credential: Credential) -> None:
    global _credentials
    _credentials = [c for c in _load_credentials() if c.trezor_pubkey != credential.trezor_pubkey]
    _credentials.append(credential)
    try:
        stored = [
            {
                "trezor_pubkey": c.trezor_pubkey.hex(),
                "host_privkey": c.host_privkey.hex(),
                "credential": c.credential.hex(),
            }
            for c in _credentials
        ]
        keyring.set_password(KEYRING_SERVICE, "credentials", json.dumps(stored))
    except Exception:
        LOG.warning("Cannot save Trezor pairing credentials to the OS keyring; they will last only for this process")


def _prompt_pairing_code() -> str:
    try:
        code = getpass.getpass("Enter the 6-digit pairing code shown on your Trezor: ", stream=sys.stderr)
    except (EOFError, KeyboardInterrupt):
        raise Cancelled("Trezor pairing canceled") from None
    return code.strip()


@contextmanager
def _thp_errors() -> Iterator[None]:
    try:
        yield
    except exceptions.Cancelled as e:
        raise Cancelled(str(e)) from e
    except (exceptions.DeviceLockedError, exceptions.NotPairedError, exceptions.InvalidSessionError) as e:
        raise DeviceNotReadyError("Trezor connection or wallet session expired; unlock the device and retry") from e
    except exceptions.PassphraseError as e:
        raise BadArgumentError(str(e)) from e
    except exceptions.TrezorException as e:
        raise DeviceConnectionError(str(e)) from e


class TrezorThpClient(LegacyClient):
    """Retain legacy message classes while upstream owns the encrypted connection."""

    def __init__(
        self,
        transport: Transport,
        ui: Any,
        pairing_code_callback: Optional[Callable[[], str]] = None,
    ) -> None:
        native_transport: NativeTransport
        if isinstance(transport, LegacyWebUsbTransport):
            native_transport = WebUsbTransport(transport.device)
        elif isinstance(transport, LegacyUdpTransport):
            native_transport = UdpTransport("{}:{}".format(*transport.device))
        else:
            raise DeviceConnectionError("THP requires a USB or UDP transport")

        self._wallet_session: Optional[ThpSession] = None
        self._closed = False
        self._pairing_code_callback = pairing_code_callback or _prompt_pairing_code
        app = AppManifest(
            app_name="HWI",
            credentials=_load_credentials,
            button_callback=lambda request: ui.button_request(request.code),
        )
        # Keep the physical connection open across multi-message signing workflows.
        # Legacy open()/close() below still delimit upstream interaction contexts.
        with _thp_errors():
            native_transport.open()
            try:
                self._native = TrezorClientThp(app, native_transport, mapping=None, model=None)
                self._pair()
                native_model = self._native.model
                model = TrezorModel(
                    name=native_model.name,
                    internal_name=native_model.internal_name,
                    minimum_version=native_model.minimum_version,
                    vendors=native_model.vendors,
                    usb_ids=native_model.usb_ids,
                    # KeepKey can register overrides in the legacy global mapping.
                    default_mapping=legacy_mapping.ProtobufMapping.from_module(legacy_messages),
                )
                super().__init__(transport, ui, model=model, _init_device=False)
                self._session = self._native.get_session(passphrase=PassphraseSetting.NONE)
                self.refresh_features()
            except BaseException:
                native_transport.close()
                raise

    def _pair(self) -> None:
        self._native.connect()
        if not self._native.pairing.is_paired():
            print("Confirm the HWI connection on your Trezor device", file=sys.stderr)
            credential = default_pairing_flow(
                self._native.pairing,
                code_entry_callback=self._pairing_code_callback,
                request_credential=True,
            )
            if credential is not None:
                _save_credential(credential)
        self._native.pairing.finish()

    def open(self) -> None:
        if self._closed:
            raise DeviceNotReadyError("Trezor connection is closed; reconnect the device")
        with _thp_errors():
            if self.session_counter == 0:
                self._native.__enter__()
            self.session_counter += 1

    def close(self) -> None:
        if self.session_counter == 0:
            return
        self.session_counter -= 1
        if self.session_counter == 0:
            with _thp_errors():
                self._native.__exit__(None, None, None)

    def disconnect(self) -> None:
        if self._closed:
            return
        try:
            if self._wallet_session is not None and self._native.is_connected():
                self._wallet_session.close()
        finally:
            self._wallet_session = None
            self.session_counter = 0
            self._closed = True
            self._native.channel.close()
            self._native.transport.close()

    def refresh_features(self) -> legacy_messages.Features:
        with _thp_errors():
            features = self._native.refresh_features()
            converted = self.mapping.decode(*self._native.mapping.encode(features))
            assert isinstance(converted, legacy_messages.Features)
            self._refresh_features(converted)
            return converted

    def ensure_unlocked(self) -> None:
        with _thp_errors():
            self._native.ensure_unlocked()
            self.refresh_features()

    def ensure_wallet_session(self) -> None:
        if self._wallet_session is None:
            with _thp_errors():
                # Match the legacy Trezor policy: enter passphrases on the device.
                self._wallet_session = self._native.get_session(passphrase=PassphraseSetting.AUTO)
        self._session = self._wallet_session

    def call(self, msg: MessageType, check_fw: bool = True) -> MessageType:
        with _thp_errors():
            if check_fw:
                self._native.check_firmware_version()
            request = self._native.mapping.decode(*self.mapping.encode(msg))
            response = self._session.call(request)
            return self.mapping.decode(*self._native.mapping.encode(response))

    def call_raw(self, msg: MessageType) -> MessageType:
        with _thp_errors():
            request = self._native.mapping.decode(*self.mapping.encode(msg))
            with self._session:
                response = self._session.call_raw(request)
            return self.mapping.decode(*self._native.mapping.encode(response))

    def cancel(self) -> None:
        with _thp_errors():
            with self._session:
                self._session.cancel()

    def setup_device(self, label: str, passphrase_protection: bool) -> None:
        with _thp_errors():
            session = self._native.get_session(passphrase=PassphraseSetting.NONE)
            device.setup(
                session,
                label=label or None,
                passphrase_protection=passphrase_protection,
                pin_protection=True,
                backup_type=messages.BackupType.Bip39,
            )
            self._wallet_session = None
            self._session = session
            self.refresh_features()

    def restore_device(self, label: str, word_count: int, passphrase_protection: bool) -> None:
        with _thp_errors():
            session = self._native.get_session(passphrase=PassphraseSetting.NONE)
            device.recover(
                session,
                label=label or None,
                word_count=word_count,
                passphrase_protection=passphrase_protection,
                pin_protection=True,
            )
            self._wallet_session = None
            self._session = session
            self.refresh_features()

    def wipe_device(self) -> None:
        with _thp_errors():
            session = self._native.get_session(passphrase=PassphraseSetting.NONE)
            device.wipe(session)
            # Upstream invalidates the encrypted channel and sessions after a wipe.
            self._wallet_session = None

    def toggle_passphrase(self) -> None:
        with _thp_errors():
            if self._wallet_session is not None:
                self._wallet_session.close()
                self._wallet_session = None
            self._session = self._native.get_session(passphrase=PassphraseSetting.NONE)
            device.apply_settings(self._session, use_passphrase=not self.features.passphrase_protection)
            self.refresh_features()
