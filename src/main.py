"""Read the server's log, look in a folder, or reset the mailbox.

Usage:
    uv run python src/main.py log            every call the server received
    uv run python src/main.py show sent      every email in one folder
    uv run python src/main.py reset          the mailbox back to the start
"""

import json
import sys

import mail
from server import LOG


def show_log() -> None:
    """Print each logged call as two lines: the call and its result."""
    if not LOG.exists():
        print("No calls yet: the server has not received any.")
        return
    for line in LOG.read_text().splitlines():
        entry = json.loads(line)
        arguments = json.dumps(entry["arguments"])
        result = str(entry["result"]).replace("\n", "\n" + " " * 30)
        print(f"{entry['time']}  [call]   {entry['tool']} {arguments}")
        print(f"{' ' * 19}  [result] {result}")


def show_folder(folder: str) -> None:
    """Print every email in one folder."""
    for email in mail.load(mail.DATA)["emails"]:
        if email["folder"] == folder:
            print(f"#{email['id']}  to {email['to']}  {email['subject']}")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "reset":
        mail.reset(mail.DATA)
        print("Mailbox reset to the start.")
    elif len(sys.argv) == 3 and sys.argv[1] == "show":
        show_folder(sys.argv[2])
    else:
        show_log()
