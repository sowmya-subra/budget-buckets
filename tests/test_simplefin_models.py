import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from budget_buckets.ingest.models import SFAccountSet

FIXTURE = Path(__file__).parent / "fixtures" / "simplefin_sample.json"
RAW_PULLS = sorted(Path("data/raw").glob("*.json"))


@pytest.fixture
def account_set() -> SFAccountSet:
    return SFAccountSet.model_validate(json.loads(FIXTURE.read_text()))


def test_amount_is_exact_decimal(account_set):
    txn = account_set.accounts[0].transactions[0]
    assert isinstance(txn.amount, Decimal)
    assert txn.amount == Decimal("-12.34")


def test_pending_transaction_has_no_posted_date(account_set):
    txn = account_set.accounts[0].transactions[1]
    assert txn.posted is None
    assert txn.is_pending


def test_epoch_becomes_utc_datetime(account_set):
    acct = account_set.accounts[0]
    assert acct.balance_date == datetime.fromtimestamp(1790000000, tz=UTC)
    assert acct.balance_date.tzinfo is UTC


def test_hyphenated_and_missing_fields(account_set):
    acct = account_set.accounts[0]
    assert acct.available_balance == Decimal("1200.00")
    assert acct.transactions[2].payee is None


@pytest.mark.skipif(not RAW_PULLS, reason="no local raw pulls")
def test_latest_real_pull_parses():
    SFAccountSet.model_validate(json.loads(RAW_PULLS[-1].read_text()))
