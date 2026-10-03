from datetime import datetime

import httpx


def _split_credentials(access_url: str) -> tuple[str, tuple[str, str]]:
    """Separate the access URL into a clean base URL and (username, password)."""
    url = httpx.URL(access_url)
    base = f"{url.scheme}://{url.host}{url.path}"
    return base, (url.username, url.password)


def fetch_accounts(
    access_url: str,
    start: datetime,
    end: datetime | None = None,
    include_pending: bool = True,
) -> dict:
    """Call SimpleFIN GET /accounts and return the raw JSON."""
    base, auth = _split_credentials(access_url)

    params: dict[str, str | int] = {"version": "2", "start-date": int(start.timestamp())}
    if end is not None:
        params["end-date"] = int(end.timestamp())
    if include_pending:
        params["pending"] = "1"

    resp = httpx.get(f"{base}/accounts", params=params, auth=auth, timeout=60)
    resp.raise_for_status()
    return resp.json()
