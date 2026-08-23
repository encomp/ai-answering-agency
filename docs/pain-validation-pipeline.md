# Niche Pain Validation Pipeline (automated, tiered)

Skill: `niche-pain-validation` (`~/.hermes/skills/research/niche-pain-validation/`) — canonical source. This doc is the repo-facing summary.

## Purpose
Verify a niche's pain points with automated tooling BEFORE human outreach or deep-research spend. Works for any niche — only CONFIG changes (niche, metro, keywords). Companion to `niche-research` (TAM/underserved/cash+); this validates the demand side.

## Tiers (cheap-first, by design)
| Tier | What runs | Cost | Trigger |
|---|---|---|---|
| **1. Quick validation** | Google Maps listings+reviews (1 city, capped) · Firecrawl funnel audit (top 15 sites) · Serper probes (underserved + pain queries) · Reddit miner script | **~$5–15** | Always |
| **2. Deeper validation** | + Indeed/LinkedIn job posts · Meta Ads Library (advertisers + run dates) · BBB complaints · Facebook groups · NOAA (weather niches) | ~$20–55 | Only if Tier 1 shows ≥1 attackable pain |
| **Phase 2 (deferred)** | Retell/VAPI AI voice mystery calls — 20 shops, day + after-hours, scored + transcribed | ~$5–10/run, monthly | Finalist niche only, after Tiers 1+2 pass |

## Pipeline
CONFIG (niche/metro/keywords) → SCRAPE (tier tool set, capped) → CLASSIFY (LLM against the 10-category pain taxonomy, JSON out, optional 2-model drift check) → SCORECARD (per-pain counts + verbatim quotes + attackability) → VERDICT (PAIN CONFIRMED / PARTIAL / WEAK + next action).

## Pain taxonomy (10 categories, any niche)
NO_RESPONSE · SLOW_RESPONSE · AVAILABILITY · PRICE · QUALITY · COMMUNICATION · PAYMENT_CLAIMS · SEASONAL_DEMAND · STAFFING · TRUST.
Attackability: NO_RESPONSE / SLOW_RESPONSE / AVAILABILITY / COMMUNICATION = directly attackable by AI answering + instant quote; PRICE/QUALITY = partial; the rest = outreach context.

## Cost rules
Free-first: Firecrawl (existing key) → Serper (in-stack) → Reddit old.reddit/JSON → NOAA → official free APIs → paid Apify actors. Caps: ≤200 listings, ≤5 reviews/shop, ≤15 probes/sites, one city per Tier-1 run. Monthly re-runs: Tier 1 ≈ $10–15, Tier 2 ≈ $30–50, Phase 2 ≈ $5–10. Recurring research budget for one committed pipeline ≈ $50–80/mo.

## Tools (verified 2026-08)
- Apify: `compass/crawler-google-places` + `compass/google-maps-reviews-scraper` · `curious_coder/indeed-scraper` · `curious_coder/linkedin-jobs-scraper` · `curious_coder/facebook-ads-library-scraper` · `epctex/bbb-scraper` · `apify/facebook-groups-scraper`
- Free: Firecrawl (key in `~/.hermes/.env`) · Serper (Skyline stack) · Reddit JSON/old.reddit · NCEI Storm Events API · official Meta Ad Library API
- Phase 2: Retell AI / VAPI outbound voice agents (~$0.05–0.10/min)
- Full details + task specs: skill `references/tool-map.md` and `references/task-specs.md`

## Output
`docs/pain-validation-<niche>.md` — scorecard with per-pain evidence table, verbatim quotes + URLs, [VERIFIED]/[ESTIMATE]/[UNVERIFIED] tags, verdict, next action. Commit + push to repo.

## Example in action (PDR, manual run 2026-08)
Reddit mining surfaced: no lead system ("following the weather channel and NOAA"), feast-famine ("50% of revenue comes from hail"), payment chasing ("always chasing payments"), tech dependence ("a good year to two years to master"), account concentration ("dealers are loyal to the technician, not the business name"), trust ("every hail chaser has gotten burned"). Next: automated Tier-1 run for PDR/DFW to convert anecdotes into counts.
