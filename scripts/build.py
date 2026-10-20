#!/usr/bin/env python3
"""Build a static, strictly read-only stablecoin APY *metadata* report.
No investment advice, wallets, orders, keys, customer files or secrets.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import math
import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE = "https://yields.llama.fi/pools"
ROOT = Path(__file__).resolve().parent.parent
CHAINS = frozenset(("Ethereum", "Base", "Arbitrum", "Optimism", "Polygon"))
ASSETS = frozenset(("USDC", "USDT", "DAI", "USDS", "PYUSD", "RLUSD", "USDG", "GHO", "EURC"))
PROJECTS = frozenset(("aave-v3", "aave-v4", "compound-v3", "morpho-blue",
                      "spark-savings", "sparklend", "sky-lending",
                      "fluid-lending", "fluid-lite", "euler-v2"))
POOL_ID = re.compile(r"^[0-9a-f]{8}-[0-9a-f-]{27,40}$", re.I)
MIN_TVL = 10_000_000
MAX_APY = 15.0
LIMIT = 100

def numeric(x):
    if x is None or isinstance(x, bool):
        return None
    try:
        val = float(x)
        return val if math.isfinite(val) else None
    except (TypeError, ValueError, OverflowError):
        return None

def qualify(raw: dict) -> dict | None:
    if not isinstance(raw, dict):
        return None
    if raw.get("chain") not in CHAINS or raw.get("project") not in PROJECTS:
        return None
    if raw.get("symbol") not in ASSETS:
        return None
    if raw.get("stablecoin") is not True or raw.get("exposure") != "single":
        return None
    if raw.get("ilRisk") != "no" or raw.get("outlier") is True:
        return None
    pool = raw.get("pool")
    if not isinstance(pool, str) or not POOL_ID.fullmatch(pool):
        return None
    tvl, total, base, reward, avg, d7 = [numeric(raw.get(key)) for key in (
        "tvlUsd", "apy", "apyBase", "apyReward", "apyMean30d", "apyPct7D")]
    if tvl is None or tvl < MIN_TVL or total is None or not (.01 <= total <= MAX_APY):
        return None
    if base is None or not (0 <= base <= MAX_APY):
        return None
    if reward is not None and reward < 0:
        return None
    flags = []
    # Source may omit reward APR. Do not label missing data as zero yield.
    if reward is None:
        flags.append("reward_split_unknown")
    elif reward >= total * .30 and reward > 0:
        flags.append("incentive_heavy")
    if d7 is None:
        flags.append("week_change_unavailable")
    elif abs(d7) >= max(3.0, total * .60):
        flags.append("rate_change_large")
    if avg is None:
        flags.append("history_unavailable")
    elif avg < total * .6:
        flags.append("spot_above_month_average")
    flags.append("protocol_and_issuer_risk_not_assessed")
    return {
        "id": pool, "protocol": raw["project"], "chain": raw["chain"],
        "asset": raw["symbol"], "tvl_usd": round(tvl),
        "apy_pct": round(total, 4), "base_pct": round(base, 4),
        "rewards_pct": round(reward, 4) if reward is not None else None,
        "mean30_pct": round(avg, 4) if avg is not None else None,
        "delta7_pctpoints": round(d7, 4) if d7 is not None else None,
        "flags": flags,
    }

def assemble(data, now=None):
    if not isinstance(data, list):
        raise ValueError("Expected data array")
    accepted = [q for p in data if (q := qualify(p))]
    accepted.sort(key=lambda p: (-p["base_pct"], -p["tvl_usd"], p["id"]))
    counts, chosen, seen = Counter(), [], set()
    for p in accepted:
        if p["id"] in seen or counts[p["protocol"]] >= 15:
            continue
        seen.add(p["id"])
        counts[p["protocol"]] += 1
        chosen.append(p)
        if len(chosen) >= LIMIT:
            break
    now = now or dt.datetime.now(dt.timezone.utc)
    return {
        "schema": 1, "checked_utc": now.isoformat().replace("+00:00", "Z"),
        "source": SOURCE, "total_pools_inspected": len(data),
        "matched_filters": len(accepted),
        "displayed": len(chosen),
        "criteria": {"min_tvl_usd": MIN_TVL, "max_apy_pct": MAX_APY,
                     "exposure": "single", "stablecoin": True,
                     "chains": sorted(CHAINS), "protocols": sorted(PROJECTS)},
        "warnings": ["Neither listing nor filter is an audit, safety score or endorsement.",
                     "Reward components can be missing; absence is not zero.",
                     "APY, TVL and redemptions can change or fail; smart contract and token issuer risks are not measured.",
                     "The data source has announced a free-yields API transition on 2026-11-13."],
        "pools": chosen,
    }

def fetch_pools():
    req = Request(SOURCE, headers={"User-Agent": "OneCursor-ReadOnly-Yield-Reality/1.0",
                                   "Accept": "application/json"})
    with urlopen(req, timeout=30) as res:
        if res.status != 200:
            raise RuntimeError(f"Source HTTP {res.status}")
        obj = json.load(res)
    if not isinstance(obj, dict) or not isinstance(obj.get("data"), list):
        raise ValueError("Unexpected provider schema; refusing to publish")
    return obj["data"]

def save_atomic(path: Path, document: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".yield-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(document, file, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            file.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", help="Optional *local* JSON array input for offline tests")
    parser.add_argument("--output", default=str(ROOT / "data" / "pools.json"))
    args = parser.parse_args()
    if args.fixture:
        with open(args.fixture, encoding="utf-8") as f:
            raw = json.load(f)
    else:
        raw = fetch_pools()
    final = assemble(raw)
    save_atomic(Path(args.output), final)
    print("built", final["checked_utc"], "source", len(raw),
          "filtered", final["matched_filters"], "public", final["displayed"],
          "bytes", Path(args.output).stat().st_size)

if __name__ == "__main__":
    main()
