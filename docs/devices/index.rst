Supported Devices
*****************

Support Matrix
==============

The table below lists what devices and features are supported for each device.

* ``✓`` - supported by the firmware and implemented in HWI
* ``✗`` - supported by the firmware and not implemented in HWI
* ``―`` - not supported by the firmware

+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Feature \\ Device                  | Ledger Nano X | Ledger Nano S | Trezor One   | Trezor Model T, Safe 3, Safe 5 | BitBox01 | BitBox02 | KeepKey | Coldcard | Blockstream Jade |
+====================================+===============+===============+==============+================================+==========+==========+=========+==========+==================+
| Support Planned                    | ✓             | ✓             | ✓            | ✓                              | ✓        | ✓        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Implemented                        | ✓             | ✓             | ✓            | ✓                              | ✓        | ✓        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| xpub retrieval                     | ✓             | ✓             | ✓            | ✓                              | ✓        | ✓        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Message Signing                    | ✓             | ✓             | ✓            | ✓                              | ✓        | ✓        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Device Setup                       | ―             | ―             | ✓            | ✓                              | ✓        | ✓        | ✓       | ―        | ―                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Device Wipe                        | ―             | ―             | ✓            | ✓                              | ✓        | ✓        | ✓       | ―        | ―                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Device Recovery                    | ―             | ―             | ✓            | ✓                              | ―        | ✓        | ✓       | ―        | ―                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Device Backup                      | ―             | ―             | ―            | ―                              | ✓        | ✓        | ―       | ✓        | ―                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| P2PKH Inputs                       | ✓             | ✓             | ✓            | ✓                              | ✓        | ―        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| P2SH-P2WPKH Inputs                 | ✓             | ✓             | ✓            | ✓                              | ✓        | ✓        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| P2WPKH Inputs                      | ✓             | ✓             | ✓            | ✓                              | ✓        | ✓        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| P2SH Multisig Inputs               | ✓             | ✓             | ✓            | ✓                              | ✓        | ―        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| P2SH-P2WSH Multisig Inputs         | ✓             | ✓             | ✓            | ✓                              | ✓        | ✓        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| P2WSH Multisig Inputs              | ✓             | ✓             | ✓            | ✓                              | ✓        | ✓        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Bare Multisig Inputs               | ✓             | ✓             | ―            | ―                              | ✓        | ―        | ―       | ―        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Taproot Inputs                     | ✓*            | ✓*            | ✓*           | ✓*                             |  ―       | ―        | ―       | ―        | ―                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Arbitrary scriptPubKey Inputs      | ✓             | ✓             | ―            | ―                              | ✓        | ―        | ―       | ―        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Arbitrary redeemScript Inputs      | ✓             | ✓             | ―            | ―                              | ✓        | ―        | ―       | ―        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Arbitrary witnessScript Inputs     | ✓             | ✓             | ―            | ―                              | ✓        | ―        | ―       | ―        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Non-wallet inputs                  | ✓             | ✓             | ✗\ :sup:`1`  | ✗\ :sup:`2`                    | ✓        | ―        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Mixed Segwit and Non-Segwit Inputs | ―             | ―             | ✓            | ✓                              | ✓        | ✓        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+
| Display on device screen           | ✓             | ✓             | ✓            | ✓                              | ―        | ✓        | ✓       | ✓        | ✓                |
+------------------------------------+---------------+---------------+--------------+--------------------------------+----------+----------+---------+----------+------------------+

* 1 - Support removed for devices with firmware 1.10.6 and greater.
* 2 - Support removed for devices with firmware 2.4.4 and greater.

\* There are some caveats. See the `sign_tx` for these devices.

Trezor Safe 7 and THP
====================

Trezor Safe 7 uses Trezor-Host Protocol (THP). HWI selects THP when a device
explicitly rejects the legacy protocol. Older Trezors and KeepKey continue
using the vendored legacy client. THP uses the upstream ``trezor`` Python
dependency included with HWI and supports USB connections and UDP emulators.
Bluetooth transport is not included.

On the first connection, approve HWI on the Trezor and enter its six-digit
pairing code at the terminal prompt. Pairing prompts go to stderr so command
results on stdout remain JSON. Pairing credentials are stored in the OS
keyring under ``hwi.trezor-thp``. Pairing reports an error if credentials cannot
be saved; unlock or configure the OS keyring before retrying. PINs and wallet
passphrases are entered on the device.

Applications using the Python API can supply a ``pairing_code_callback`` to
``hwilib.devices.trezor.TrezorClient``. It takes no arguments and returns the
six-digit code as a string. Without this callback, HWI uses a terminal prompt
only when stdin, stdout, and stderr are terminals. Enumeration never prompts
for a pairing code.

Pairing from a parent application
================================

Unpaired Trezor THP and BitBox02 devices report ``PAIRING_REQUIRED`` (``-20``)
and ``needs_pairing: true``. Enumeration includes their type, path, and model
without requiring a fingerprint. The parent application can then launch::

    hwi -t trezor -d <device-path> pair

Use ``-t bitbox02`` for a BitBox02. An explicit type and path are required;
do not use ``-f`` or the global ``--stdin`` argument-input option for pairing.
Keep this same child process alive until pairing finishes. HWI does not spawn
a helper process or a server.

``pair`` always uses the JSON protocol below. The optional ``--stdio`` flag is
accepted for compatibility and does not change its behavior.

Each message is one newline-terminated JSON object. HWI flushes its request
on stdout before waiting for a response on stdin. Both devices use the same
request shape::

    {"event":"pairing_required","method":"enter_code","code":null}
    {"event":"pairing_required","method":"confirm_code","code":"ABCDE FGHIJ\nKLMNO PQRST"}

``enter_code`` asks the GUI to collect the six digits displayed on Trezor;
``confirm_code`` asks it to display and compare the BitBox02 code. Respond::

    {"accept":true,"code":"012345"}

For BitBox02, use ``{"accept":true,"code":null}``; approval on the device is
also required. Either dialog can reject with ``{"accept":false,"code":null}``.
Closing stdin cancels a pending request. Responses are limited to 4096
characters, including the newline.

HWI then writes its final ``{"success":true}`` or normal ``error``/``code``
response and exits. An already-paired device can return success immediately.
All human-readable diagnostics go to stderr. The parent should provide a
timeout and terminate/reap the child when the user cancels or the app closes.
Do not log pairing responses. Normal HWI commands continue to return one JSON
result per run. Completed credentials are reused by later processes; BitBox02
uses its existing BitBoxApp-compatible storage and Trezor uses the OS keyring.

Support Policy
================

For a device to be supported by HWI, it must:

* Use open source firmware as much as possible

  * Entirely closed source devices will be rejected
  * Devices may have closed source firmware components if required to under a NDA (e.g. a secure element with NDA)

* Publicly documented communication protocol

  * It is preferred to both document the protocol and provide a Python library for using it
  * The library, with its own documentation, can suffice as "publicly documented"

* Either (but preferably both):

  * A simulator/emulator is available for automated tests to be run
  * A promise to maintain and support from the vendor:

Device support may be dropped:

* If promised vendor maintenance and support disappears

  * If there are continuous issues with the device and the vendor has failed to provide support and updates

* If the device no longer receives security updates and there are known vulnerabilities and issues

Device APIs
===========

.. automodule:: hwilib.devices.ledger
   :members:
.. automodule:: hwilib.devices.trezor
   :members:
.. automodule:: hwilib.devices.digitalbitbox
   :members:
.. automodule:: hwilib.devices.bitbox02
   :members:
.. automodule:: hwilib.devices.keepkey
   :members:
.. automodule:: hwilib.devices.coldcard
   :members:
.. automodule:: hwilib.devices.jade
   :members:
