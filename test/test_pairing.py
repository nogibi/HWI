"""Host/GUI pairing protocol tests; no hardware or persistent credentials."""

import io
import json
import unittest
from unittest.mock import patch

from hwilib import _cli
from hwilib._pairing import request_pairing
from hwilib.errors import ActionCanceledError, BadArgumentError, PairingRequiredError, handle_errors


class PairingProtocolTest(unittest.TestCase):
    def exchange(self, method, code, response):
        output = io.StringIO()
        with patch('sys.stdin', io.StringIO(response)), patch('sys.stdout', output):
            result = request_pairing(method, code)
        return result, json.loads(output.getvalue())

    def test_code_entry_preserves_leading_zero(self):
        result, event = self.exchange('enter_code', None, '{"accept":true,"code":"012345"}\n')
        self.assertEqual(result, '012345')
        self.assertEqual(event, {'event': 'pairing_required', 'method': 'enter_code', 'code': None})

    def test_code_comparison_uses_same_envelope(self):
        code = 'ABCDE FGHIJ\nKLMNO PQRST'
        result, event = self.exchange('confirm_code', code, '{"accept":true,"code":null}\n')
        self.assertEqual(result, '')
        self.assertEqual(event, {'event': 'pairing_required', 'method': 'confirm_code', 'code': code})

    def test_cancel_and_closed_input(self):
        for response in ['', '{"accept":false,"code":null}\n']:
            with self.subTest(response=response), self.assertRaises(ActionCanceledError):
                self.exchange('enter_code', None, response)

    def test_malformed_input(self):
        responses = ['{}\n', '[]\n', 'null\n', 'broken\n', '{"accept":1,"code":"123456"}\n',
                     '{"accept":true,"code":"１２３４５６"}\n', '{"accept":true,"code":"12345"}\n',
                     '{"accept":true,"code":123456}\n', '{"accept":true,"code":"123456"}', ' ' * 4097 + '\n']
        for response in responses:
            with self.subTest(response=response[:80]), self.assertRaises(BadArgumentError):
                self.exchange('enter_code', None, response)

    def test_pairing_error_retains_enumeration_metadata(self):
        device = {'type': 'trezor', 'path': 'webusb:example'}
        with handle_errors(result=device):
            raise PairingRequiredError(model='trezor_t3w1')
        self.assertEqual(device['code'], -20)
        self.assertTrue(device['needs_pairing'])
        self.assertEqual(device['model'], 'trezor_t3w1')
        self.assertEqual(device['path'], 'webusb:example')

    def test_cli_uses_one_client_for_request_and_final_result(self):
        class Client:
            closed = False
            def pair_device(self, callback):
                self.answer = callback('enter_code', None)
            def close(self):
                self.closed = True
        for extra_args in ([], ['--stdio']):
            with self.subTest(extra_args=extra_args):
                client = Client()
                output = io.StringIO()
                with patch.object(_cli, 'get_client', return_value=client), \
                     patch('sys.argv', ['hwi', '-t', 'trezor', '-d', 'test device path', 'pair'] + extra_args), \
                     patch('sys.stdin', io.StringIO('{"accept":true,"code":"012345"}\n')), patch('sys.stdout', output):
                    _cli.main()
                messages = [json.loads(line) for line in output.getvalue().splitlines()]
                self.assertEqual(len(messages), 2)
                self.assertEqual(messages[0]['event'], 'pairing_required')
                self.assertEqual(messages[1], {'success': True})
                self.assertEqual(client.answer, '012345')
                self.assertTrue(client.closed)

    def test_cli_closes_client_on_rejection(self):
        from unittest.mock import Mock
        client = Mock()
        client.pair_device.side_effect = lambda callback: callback('confirm_code', 'CODE')
        with patch.object(_cli, 'get_client', return_value=client), \
             patch('sys.stdin', io.StringIO('{"accept":false}\n')), patch('sys.stdout', io.StringIO()):
            result = _cli.process_commands(['-t', 'bitbox02', '-d', 'example', 'pair'])
        self.assertEqual(result['code'], -14)
        client.close.assert_called_once()

    def test_pairing_needs_path_without_auto_enumeration(self):
        with patch.object(_cli, 'find_device') as find:
            result = _cli.process_commands(['-t', 'trezor', 'pair'])
        self.assertEqual(result['code'], -2)
        find.assert_not_called()

    def test_bitbox_requires_gui_and_device_confirmation(self):
        from hwilib.devices.bitbox02 import AppNoiseConfig
        from unittest.mock import Mock
        callback = Mock(return_value='')
        device_response = Mock(return_value=True)
        self.assertTrue(AppNoiseConfig(callback).show_pairing('CODE', device_response))
        callback.assert_called_once_with('confirm_code', 'CODE')
        device_response.assert_called_once()
        with self.assertRaises(ActionCanceledError):
            AppNoiseConfig(callback).show_pairing('CODE', lambda: False)

    def test_bitbox_rejection_does_not_wait_for_device(self):
        from hwilib.devices.bitbox02 import AppNoiseConfig
        from unittest.mock import Mock
        callback = Mock(side_effect=ActionCanceledError('Rejected'))
        device_response = Mock()
        with self.assertRaises(ActionCanceledError):
            AppNoiseConfig(callback).show_pairing('CODE', device_response)
        device_response.assert_not_called()

    def test_cli_already_paired_has_only_final_result(self):
        from unittest.mock import Mock
        client = Mock()
        output = io.StringIO()
        with patch.object(_cli, 'get_client', return_value=client), \
             patch('sys.argv', ['hwi', '-t', 'trezor', '-d', 'example', 'pair']), \
             patch('sys.stdin', None), patch('sys.stdout', output):
            _cli.main()
        self.assertEqual(output.getvalue(), '{"success": true}\n')
        client.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
