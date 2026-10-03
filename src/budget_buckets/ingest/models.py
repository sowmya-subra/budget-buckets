from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def epoch_to_datetime(value: Any) -> datetime | None:
    """SimpleFIN sends Unix seconds; 0 or missing means 'no date'."""
    if value in (None, 0, "0"):
        return None
    return datetime.fromtimestamp(int(value), tz=UTC)


EpochDatetime = Annotated[datetime | None, BeforeValidator(epoch_to_datetime)]


class SFError(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: str | None = None
    msg: str | None = None


class SFConnection(BaseModel):
    conn_id: str
    name: str
    org_id: str | None = None
    org_name: str | None = None
    org_url: str | None = None
    sfin_url: str | None = None


class SFTransaction(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)

    id: str
    amount: Decimal
    description: str = ""
    payee: str | None = None
    memo: str | None = None
    mcc: str | None = None
    posted: EpochDatetime = None
    transacted_at: EpochDatetime = None
    pending: bool = False

    @property
    def is_pending(self) -> bool:
        return self.pending or self.posted is None


class SFAccount(BaseModel):
    id: str
    name: str
    conn_id: str
    currency: str
    balance: Decimal
    available_balance: Decimal | None = Field(default=None, alias="available-balance")
    balance_date: EpochDatetime = Field(default=None, alias="balance-date")
    transactions: list[SFTransaction] = []
    holdings: list[dict[str, Any]] = []


class SFAccountSet(BaseModel):
    errlist: list[SFError] = []
    connections: list[SFConnection] = []
    accounts: list[SFAccount] = []
