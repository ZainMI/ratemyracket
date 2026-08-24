#!/usr/bin/env python3
"""Send a concise pipeline failure email using SMTP settings from an env file."""

from __future__ import annotations

import argparse
import os
import smtplib
import socket
import ssl
from email.message import EmailMessage
from pathlib import Path


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value

    return values


def tail_text(path: Path, lines: int = 200) -> str:
    if not path.exists():
        return "Log file was not found."
    content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(content[-lines:])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", required=True, type=Path)
    parser.add_argument("--log-file", required=True, type=Path)
    parser.add_argument("--exit-code", required=True, type=int)
    args = parser.parse_args()

    config = {**load_env_file(args.env_file), **os.environ}
    mail_to = config.get("MAIL_TO", "").strip()
    username = config.get("SMTP_USERNAME", "").strip()
    password = config.get("SMTP_PASSWORD", "").strip()

    if not mail_to or not username or not password:
        print(
            "Email notification skipped: configure MAIL_TO, SMTP_USERNAME, "
            "and SMTP_PASSWORD in .env.worker."
        )
        return 0

    host = config.get("SMTP_HOST", "smtp.gmail.com").strip()
    port = int(config.get("SMTP_PORT", "465"))
    mail_from = config.get("SMTP_FROM", username).strip()
    server_name = socket.gethostname()

    message = EmailMessage()
    message["Subject"] = f"RacketRating pipeline failed on {server_name}"
    message["From"] = mail_from
    message["To"] = mail_to
    message.set_content(
        f"The RacketRating pipeline failed on {server_name}.\n"
        f"Exit code: {args.exit_code}\n"
        f"Server log: {args.log_file}\n\n"
        "Last 200 log lines:\n"
        "----------------------------------------\n"
        f"{tail_text(args.log_file)}\n"
    )

    context = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=context, timeout=30) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(message)

    print(f"Failure email sent to {mail_to}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
