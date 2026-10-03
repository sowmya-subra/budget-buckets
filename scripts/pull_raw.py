"""Pull the last 30 days from SimpleFIN and save the raw JSON locally."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from budget_buckets.config import Settings
from budget_buckets.ingest.simplefin import fetch_accounts


def main() -> None:
    settings = Settings()
    now = datetime.now(UTC)
    data = fetch_accounts(
        settings.simplefin_access_url.get_secret_value(),
        start=now - timedelta(days=30),
    )

    for err in data.get("errlist", []):
        print("SimpleFIN error:", err)

    out = Path("data/raw") / f"accounts_{now:%Y%m%dT%H%M%SZ}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2))
    print(f"Saved {len(data.get('accounts', []))} accounts to {out}")


if __name__ == "__main__":
    main()
