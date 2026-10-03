import argparse
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from budget_buckets.config import Settings
from budget_buckets.ingest.models import SFAccountSet
from budget_buckets.ingest.simplefin import fetch_accounts

RAW_DIR = Path("data/raw")
NO_DATE = datetime.max.replace(tzinfo=UTC)


def save_raw(data: dict, now: datetime) -> Path:
    path = RAW_DIR / f"accounts_{now:%Y%m%dT%H%M%SZ}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    return path


def latest_raw() -> Path:
    files = sorted(RAW_DIR.glob("*.json"))
    if not files:
        raise SystemExit("No saved pulls in data/raw. Run `budget-buckets pull` first.")
    return files[-1]


def print_transactions(account_set: SFAccountSet) -> None:
    for err in account_set.errlist:
        print(f"SimpleFIN error [{err.code}]: {err.msg}")

    institutions = {c.conn_id: c.org_name or c.name for c in account_set.connections}
    rows = [
        (txn, acct, institutions.get(acct.conn_id, "?"))
        for acct in account_set.accounts
        for txn in acct.transactions
    ]
    rows.sort(key=lambda r: r[0].posted or r[0].transacted_at or NO_DATE, reverse=True)

    for txn, acct, inst in rows:
        when = txn.posted or txn.transacted_at
        date = when.strftime("%Y-%m-%d") if when else "pending   "
        flag = "P" if txn.is_pending else " "
        label = txn.payee or txn.description
        print(
            f"{date}  {flag}  {txn.amount:>10}  {inst[:12]:<12}  {acct.name[:18]:<18}  {label[:40]}"
        )

    print(f"\n{len(rows)} transactions across {len(account_set.accounts)} accounts")


def cmd_pull(args: argparse.Namespace) -> None:
    settings = Settings()
    now = datetime.now(UTC)
    data = fetch_accounts(
        settings.simplefin_access_url.get_secret_value(),
        start=now - timedelta(days=args.days),
    )
    path = save_raw(data, now)
    print(f"Saved raw pull to {path}\n")
    print_transactions(SFAccountSet.model_validate(data))


def cmd_show(args: argparse.Namespace) -> None:
    path = latest_raw()
    print(f"Showing {path}\n")
    print_transactions(SFAccountSet.model_validate_json(path.read_text()))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="budget-buckets")
    sub = parser.add_subparsers(dest="command", required=True)

    pull = sub.add_parser("pull", help="Fetch from SimpleFIN, save raw JSON, print transactions")
    pull.add_argument("--days", type=int, default=30, help="Days of history to fetch (1-90)")
    pull.set_defaults(func=cmd_pull)

    show = sub.add_parser("show", help="Print the latest saved pull (no network)")
    show.set_defaults(func=cmd_show)

    args = parser.parse_args(argv)
    if args.command == "pull" and not 1 <= args.days <= 90:
        parser.error("--days must be between 1 and 90")
    args.func(args)
