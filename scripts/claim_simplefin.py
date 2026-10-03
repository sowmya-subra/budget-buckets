"""Exchange a SimpleFIN setup token for an access URL and save it to .env."""

import base64
from getpass import getpass
from pathlib import Path

import httpx

ENV_PATH = Path(".env")
KEY = "SIMPLEFIN_ACCESS_URL"


def main() -> None:
    token = getpass("Paste setup token (hidden): ").strip()
    claim_url = base64.b64decode(token).decode()

    resp = httpx.post(claim_url, timeout=30)
    resp.raise_for_status()
    access_url = resp.text.strip()

    lines = ENV_PATH.read_text().splitlines()
    lines = [f"{KEY}={access_url}" if line.startswith(f"{KEY}=") else line for line in lines]
    ENV_PATH.write_text("\n".join(lines) + "\n")
    print(f"Saved {KEY} to {ENV_PATH}.")


if __name__ == "__main__":
    main()
