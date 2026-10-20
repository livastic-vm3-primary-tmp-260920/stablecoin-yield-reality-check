"""Build a no-wallet public frozen DeFi data QA example from our own timestamped source extract."""
from __future__ import annotations
from decimal import Decimal
from html import escape
from pathlib import Path
from urllib.parse import quote
import json

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/public-qa-example-20261021.json"
OUTPUT = ROOT / "public-qa-example.html"

def dec(v: object) -> Decimal:
    if isinstance(v, bool) or v is None:
        raise ValueError("non-numeric input")
    d = Decimal(str(v))
    if not d.is_finite():
        raise ValueError("non-finite input")
    return d

def model(row: dict, principal: object, days: object, cost: object) -> dict:
    p, d, c = dec(principal), dec(days), dec(cost)
    b, t = dec(row["base_pct"]), dec(row["apy_pct"])
    if p < 0 or d <= 0 or d > 365 or c < 0 or b < 0 or t < 0:
        raise ValueError("invalid financial illustration inputs")
    rewards = row.get("rewards_pct")
    if rewards is not None and dec(rewards) < 0:
        raise ValueError("invalid rewards")
    return {
        "base_gross": p * b * d / Decimal(36500),
        "headline_gross": p * t * d / Decimal(36500),
        "base_after_fees": p * b * d / Decimal(36500) - c,
        "headline_after_fees": p * t * d / Decimal(36500) - c,
        "reward_share": None if rewards is None or t == 0 else dec(rewards)/t * Decimal(100),
        "reward_state": "unknown" if rewards is None else ("reported zero" if dec(rewards) == 0 else "reported nonzero"),
    }

def money(value: Decimal) -> str:
    return ("-" if value < 0 else "") + f"${abs(value):,.2f}"

def html_from_document(doc: dict) -> str:
    example = doc["illustrative"]
    p = dec(example["principal_usd"])
    d = dec(example["days"])
    c = dec(example["assumed_roundtrip_cost_usd"])
    rows = doc["pools"]
    if len(rows) != 3 or len({row['id'] for row in rows}) != 3:
        raise ValueError("must contain exactly 3 distinct public pool IDs")
    line_items = []
    notes = []
    for row in rows:
        m = model(row, p, d, c)
        desc = str(row["case"])
        state = m["reward_state"]
        rewards = "unknown (null)" if row.get("rewards_pct") is None else f'{dec(row["rewards_pct"]):.2f}%'
        share = "unknown" if m["reward_share"] is None else f'{m["reward_share"]:.1f}%'
        poolid = escape(str(row["id"]),quote=True)
        line_items.append(
            f'<tr><td><strong>{escape(desc)}</strong><small>{escape(str(row["protocol"]))} / {escape(str(row["chain"]))} / USDC</small>'
            f'<code>{poolid}</code></td><td>{dec(row["base_pct"]):.2f}%</td><td>{escape(rewards)}</td>'
            f'<td>{dec(row["apy_pct"]):.2f}%</td><td>{share}</td>'
            f'<td>{money(m["base_gross"])}</td><td>{money(m["base_after_fees"])}</td>'
            f'<td>{money(m["headline_after_fees"])}</td></tr>'
        )
        if state == 'unknown':
            explanation = "The source provided no rewards breakdown. Do not infer a zero incentive reward from a null field."
        elif state == 'reported zero':
            explanation = "The source explicitly reports 0% rewards; that is not proof of no future incentive change."
        else:
            explanation = f'{m["reward_share"]:.1f}% of headline APY is reported as rewards; do not confuse incentives with the base component.'
        notes.append(f'<li><strong>{escape(desc)}:</strong> {escape(explanation)}</li>')
    emailbody = (
      "Hello, I would like a quote for one public stablecoin yield data discrepancy.\n"
      "Public pool IDs (up to 3):\nPublic discrepancy and source links:\n"
      "Please confirm the fixed scope, final deliverable, acceptance, price, Base USDC payee, delivery date, privacy, and refund terms before any payment.\n"
      "I will not send keys, seed phrases, portfolio data, or confidential documents."
    )
    mailto = "mailto:onecursor1@gmail.com?subject=" + quote("Request public pool-data QA scope",safe="") + "&amp;body=" + quote(emailbody,safe="")
    checked = escape(str(doc["checked_utc"]))
    source = escape(str(doc["source"]),quote=True)
    snapshot_id = escape(str(doc["source_snapshot_sha256"]))
    table = '\n'.join(line_items)
    observations = '\n'.join(notes)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'">
<meta name="description" content="Free, reproducible, historical three-pool stablecoin APY component QA example: base vs incentive yields, unknown rewards, and hypothetical fee break-even.">
<title>Public stablecoin yield data QA example | One Cursor</title>
<style>
:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{background:#071920;color:#f0f6f8;line-height:1.65;font:16px system-ui,sans-serif;margin:0}}main,header,footer{{max-width:1050px;margin:auto;padding:24px}}h1{{font-size:clamp(27px,4vw,44px);line-height:1.2}}h2{{margin-top:32px}}a{{color:#aee2ff}}p,li,small{{color:#c0d5db}}.card{{background:#112a35;border:1px solid #466573;padding:20px;border-radius:12px;margin:18px 0}}.alert{{border-left:4px solid #f7ca82;background:#32291c;padding:15px}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums;min-width:880px}}th,td{{padding:10px;border-bottom:1px solid #496470;text-align:left;vertical-align:top}}th{{color:#d8f7e9}}td small,td code{{display:block;font-size:12px;overflow-wrap:anywhere;max-width:230px}}td code{{margin-top:8px;color:#95aeb7}}.cta{{display:inline-block;background:#b6f6ce;color:#07281c;padding:12px 16px;border-radius:8px;text-decoration:none;font-weight:bold}}a:focus{{outline:3px solid #b6f6ce}}footer{{border-top:1px solid #466573;font-size:13px}}</style></head>
<body><header><a href="./">← Back to free APY screener</a> · <a href="./data/public-qa-example-20261021.json">Download frozen public evidence JSON</a></header>
<main>
<h1>What a public DeFi yield-data QA report actually checks</h1>
<p>This is an original, <strong>free demonstration</strong> using 3 real publicly reported historical pool IDs. It is NOT a customer commission, a sponsored yield review, an on-chain audit, or a statement that any vault is safe.</p>
<div class="alert"><strong>Fixed historical snapshot:</strong> {checked}. Provider: <a href="{source}">DefiLlama Yields public data</a>. Rates can be stale or change immediately; the free source endpoint is scheduled to change in November 2026. All numbers below are from this exact past snapshot, NOT live yields.</div>
<section class="card"><h2>1. Inspect the source fields before trusting headline APY</h2>
<p>Three deliberately different USDC pool records: reported-zero rewards, a large incentive share, and an unknown reward breakdown. This is not an apples-to-apples risk comparison across protocol versions or chains.</p>
<p><strong>Common illustrative inputs:</strong> principal {money(p)}, holding period {d} days, assumed total deposit + bridge + withdrawal fees {money(c)}. Flat annual rates are applied proportionally, without compounding, yield changes, slippage or principal loss.</p>
<div class="scroll"><table><thead><tr><th>Source record</th><th>Base APY</th><th>Reward APY</th><th>Headline APY</th><th>Rewards share</th><th>30-day base gross</th><th>Base after fees</th><th>Headline after fees</th></tr></thead><tbody>
{table}
</tbody></table></div>
</section>
<section class="card"><h2>2. Findings that change interpretation</h2><ul>{observations}</ul>
<p><strong>Fee break-even:</strong> base-only return becomes positive only after the hypothetical fees are covered. A higher headline APY does not remove risks or guarantee any reward token can be realized at its quoted value.</p>
<p><strong>Missing values:</strong> an omitted reward field remains UNKNOWN; it is never automatically set to zero. Any real audit would need source-level investigation, not an assumption that reported values reflect available withdrawals.</p>
</section>
<section class="card"><h2>3. Reproduce and inspect the evidence</h2>
<p>Read the <a href="./data/public-qa-example-20261021.json">three public records</a> with full pool IDs, timestamp and SHA-256 of the original timestamped JSON extract. The reproducible <a href="https://github.com/livastic-vm3-primary-tmp-260920/stablecoin-yield-reality-check/blob/main/scripts/build_qa_sample.py">Python script</a> uses standard-library Decimal and safely escapes public strings.</p>
<p>Formula: <code>illustrative gross = USD principal × reported APY (%) × days / 36500</code>; hypothetical net = gross - user-assumed total fees. No wallet, client CSV, private transaction data, tracking, smart-contract interaction, signature, payment, or legal/tax advice.</p>
</section>
<section class="card" id="request"><h2>Have a real discrepancy in 1–3 public pool IDs?</h2>
<p>Request a separate manually scoped technical DATA QA quote. Indicative fixed proposal: <strong>19 native Circle USDC on Base</strong>, only if the deliverable, report evidence, recipient wallet control, chain, written acceptance/cancellation/refunds, timeframe and data privacy are agreed <strong>before any payment</strong>. Free public checks remain free. No financial advice or exploit/security certification.</p>
<a class="cta" href="{mailto}">Request a quote by email (no payment now)</a>
<p>Do not send real private account exports, recovery phrases, signed orders or passwords. No independent buyer, delivered paid report or paid revenue is claimed by this demo.</p></section>
</main><footer>ONE CURSOR · publicly attributable, AI-assisted methodology. Source snapshot SHA-256 <code>{snapshot_id}</code>. No endorsements or guaranteed returns.</footer>
</body></html>
'''

def build() -> None:
    doc=json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    content=html_from_document(doc)
    OUTPUT.write_text(content,encoding="utf-8")

if __name__=="__main__":
    build()
