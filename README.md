# Stablecoin Yield Reality Check

Public launch: https://livastic-vm3-primary-tmp-260920.github.io/stablecoin-yield-reality-check/

Original read-only application by One Cursor (one human beneficial owner, AI-assisted). Designed around concrete public DeFi user questions about comparing Aave/Morpho rates, temporary incentive emissions and deposit/exit fees. Not a guarantee of demand, paid customers, income, safety, tax accuracy or future profit.

## What real users can do

1. Compare source-reported base APY, reward APY, headline APY, trailing 30-day average and 7-day change for a restricted set of stablecoin pools.
2. Filter by stablecoin, EVM chain and simple data-quality flags.
3. Enter a hypothetical principal, days and estimated round-trip fee to see if constant reported base yield would even cover fees. This is a straight-line illustration, NOT a profit forecast.
4. Export the on-screen third-party public metadata as CSV.
5. Optionally request separately quoted technical DATA QA for up to three public pool IDs (indicative 19 native Circle USDC on Base), after written buyer consent and terms. Not a public direct-pay invoice, not a security audit or investment advice.

Privacy: no MetaMask, signatures, fees, approving/depositing tokens, password, email, user files, cookies, analytics, server account or KYC. Static front-end fetches only same-origin data/pools.json and never transmits typed hypothetical values. CSP restricts network to same-origin.

## Data source and integrity

Original public source: https://yields.llama.fi/pools, the DefiLlama Yields endpoint. Copyright/licensing remains with provider; use is attribution-only in this free product, not resale of the underlying full feed. The free endpoint transition has been announced for 2026-11-13. The GitHub Action refreshes 4x/day UNTIL the announced transition, then fails closed. An update failure leaves a timestamped snapshot. The UI prominently labels feeds older than 24h as STALE. No safety ratings.

Filters are intentionally narrow: selected major protocols and EVM chains only, single exposure, exact listed stablecoin symbols and source stablecoin=true, source ilRisk=no, not outlier, min USD10M TVL and 0.01–15% total APY with a valid source base rate. Missing apyReward is unknown, never quietly zero. Metadata filters are NOT due diligence; smart-contract, oracle, chain, token depeg, liquidity/withdrawal, curator and legal risks are unassessed.

## Offline tests, build and preview

    python3 -m unittest discover -s tests -v
    node --test tests/*.test.mjs
    python3 scripts/build.py
    python3 -m http.server 8111

Publication/update is automated via GitHub Actions branch data commit; build uses only Python standard library and a public API. No keys or external user data.

## Public evidence of a problem, not a paid client

- User confusion and fragmented yield tools (Oct 2, 2026): https://www.reddit.com/r/defi/comments/1wvsxvf/defi_stablecoin_platforms/
- Withdrawal/bridge friction makes rates misleading (May 2, 2026): https://www.reddit.com/r/defi/comments/1t217lv/is_defi_yield_even_worth_the_hassle_anymore/
- Incentives vs base rate (Mar 4, 2026): https://www.reddit.com/r/defi/comments/1rk65mq/how_are_people_actually_getting_doubledigit/
- Official DefiLlama reference rates: https://defillama.com/yields/rates

At publication: independently verified paying users 0; signed buyer orders 0; revenue newly earned from this application 0 USDC.
