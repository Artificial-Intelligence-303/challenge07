"""Point every test at its own bookings and log, never at yours."""

from pathlib import Path

import pytest

import mail
import server


@pytest.fixture(autouse=True)
def scratch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Give each test a fresh mailbox and an empty log."""
    monkeypatch.setattr(mail, "DATA", tmp_path / "mailbox.json")
    monkeypatch.setattr(server, "LOG", tmp_path / "tool-calls.jsonl")
