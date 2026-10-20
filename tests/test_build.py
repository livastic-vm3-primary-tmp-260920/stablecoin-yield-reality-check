import datetime as dt
import json
import math
import tempfile
import unittest
from pathlib import Path
from scripts.build import qualify, assemble, save_atomic

def pool(**changes):
    obj = dict(pool="62e8d8be-8d65-4e8b-ac89-5993c2906ae9",
               chain="Ethereum", project="aave-v3", symbol="USDC",
               stablecoin=True, exposure="single", ilRisk="no", outlier=False,
               tvlUsd=20000000, apy=6.0, apyBase=4.0, apyReward=2.0,
               apyMean30d=2.5, apyPct7D=5.1)
    obj.update(changes)
    return obj

class FeedTests(unittest.TestCase):
    def test_meaningful_pool(self):
        x = qualify(pool())
        self.assertEqual(x["base_pct"], 4)
        self.assertIn("incentive_heavy", x["flags"])
        self.assertIn("rate_change_large", x["flags"])
        self.assertIn("spot_above_month_average", x["flags"])
        self.assertIn("protocol_and_issuer_risk_not_assessed", x["flags"])
    def test_never_confuse_missing_rewards_with_zero(self):
        x = qualify(pool(apyReward=None))
        self.assertIsNone(x["rewards_pct"])
        self.assertIn("reward_split_unknown", x["flags"])
        self.assertNotIn("incentive_heavy", x["flags"])
    def test_yield_data_is_not_a_security_audit(self):
        self.assertIn("risk_not_assessed", "|".join(qualify(pool())["flags"]))
    def test_excludes_non_stable_or_lp(self):
        for change in [dict(symbol="WETH"), dict(stablecoin=False),
                       dict(exposure="multi"), dict(ilRisk="yes"), dict(outlier=True),
                       dict(project="unknown"), dict(chain="Solana"),
                       dict(tvlUsd=150), dict(apy=120), dict(apyBase=None),
                       dict(apyReward=-2), dict(pool="<script>alert(1)</script>")]:
            with self.subTest(change=change):
                self.assertIsNone(qualify(pool(**change)))
    def test_malformed_values_and_bool_are_rejected(self):
        for val in [math.nan, math.inf, -math.inf, "nonsense", True, None]:
            self.assertIsNone(qualify(pool(apy=val)))
    def test_unknown_week_info_flagged(self):
        self.assertIn("week_change_unavailable", qualify(pool(apyPct7D=None))["flags"])
    def test_id_dedup_and_deterministic(self):
        t = dt.datetime(2026, 10, 20, tzinfo=dt.timezone.utc)
        self.assertEqual(assemble([pool(),pool()], now=t)["displayed"], 1)
        self.assertEqual(assemble([pool()], now=t)["checked_utc"], "2026-10-20T00:00:00Z")
    def test_dump_and_parse(self):
        with tempfile.TemporaryDirectory() as d:
            fp = Path(d) / "data" / "pools.json"
            doc = assemble([pool()])
            save_atomic(fp, doc)
            self.assertEqual(json.loads(fp.read_text())["displayed"], 1)

if __name__ == "__main__":
    unittest.main()
