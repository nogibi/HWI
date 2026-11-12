"""Pairing callbacks shared by the CLI and device adapters."""

import json
import sys
from typing import Callable, Optional

from .errors import ActionCanceledError, BadArgumentError


PairingCallback = Callable[[str, Optional[str]], str]


def request_pairing(method: str, code: Optional[str]) -> str:
    """Exchange one newline-delimited JSON request/response with a parent app.

    The caller keeps the device connection open until this callback returns.
    Human-readable diagnostics must go to stderr, never stdout.
    """
    print(json.dumps({"event": "pairing_required", "method": method, "code": code}), flush=True)
    try:
        line = sys.stdin.readline(4097) if sys.stdin is not None else ""
    except KeyboardInterrupt:
        raise ActionCanceledError("Pairing canceled") from None
    if not line:
        raise ActionCanceledError("Pairing input closed")
    if len(line) > 4096 or not line.endswith("\n"):
        raise BadArgumentError("Pairing response must be a JSON line of at most 4096 characters")
    try:
        response = json.loads(line)
    except ValueError:
        raise BadArgumentError("Invalid pairing response JSON") from None
    if not isinstance(response, dict) or type(response.get("accept")) is not bool:
        raise BadArgumentError("Pairing response requires a boolean 'accept'")
    if not response["accept"]:
        raise ActionCanceledError("Pairing rejected")
    if method == "enter_code":
        entered = response.get("code")
        if not isinstance(entered, str) or len(entered) != 6 or not entered.isascii() or not entered.isdigit():
            raise BadArgumentError("Pairing code must contain six digits")
        return entered
    if method == "confirm_code":
        if response.get("code") is not None:
            raise BadArgumentError("Code comparison requires 'code' to be null")
        return ""
    raise BadArgumentError("Unknown pairing method")
