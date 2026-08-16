# Niche Brainstorm — Scorecard & Top 5 (US)

Run: `niche-research` skill, brainstorm mode, SEÑAL_FLOW off, PRICING TARGET $2,500/mo.
**IMPORTANT:** web tools were unavailable during this run (Firecrawl key not configured; browser provider down).
All TAM / textable / margin figures are **[ESTIMATE]** from domain knowledge — none verified live.
The PROOF GAPS section lists the exact queries and tests to run before any final pick.

## Candidates (12) — scored 1-5 per criterion, total /30

| Niche | Underserved | Cash+ (job×margin) | Urgency | TAM | Ad proof | Textable | Total | Tier* |
|---|---|---|---|---|---|---|---|---|
| Foundation repair / structural | 3 | 5 | 5 | 4 | 5 | 4 | **26** | GREEN (~13.7k) |
| Septic service & repair | 5 | 3 | 4 | 3 | 3 | 5 | **23** | RED/YEL (~6.6k) |
| Basement waterproofing / flood | 3 | 4 | 4 | 3 | 4 | 4 | **22** | RED/YEL (~6-9k) |
| Crawlspace encaps. / mold remed. | 4 | 4 | 4 | 3 | 3 | 4 | **22** | RED/YEL (~5.5-8k) |
| Men's health / TRT clinics | 2 | 3 | 4 | 4 | 5 | 3 | **21** | RED/YEL (~7.6k) |
| Water damage restoration | 2 | 4 | 5 | 3 | 4 | 3 | 21 | RED (~4.5k) |
| Fire safety & compliance | 4 | 2 | 4 | 4 | 3 | 2 | 19 | YEL — *dropped: fails cash+* |
| Environmental testing (asbestos/AQ) | 4 | 2 | 4 | 3 | 3 | 3 | 19 | *dropped: fails cash+* |
| Storm shelter / safe rooms | 4 | 3 | 3 | 2 | 3 | 4 | 19 | *dropped: TAM too small* |
| Kitchen hood cleaning / suppression | 4 | 2 | 3 | 4 | 2 | 3 | 18 | *dropped: fails cash+* |
| Specialty waste / disposal | 3 | 2 | 3 | 4 | 3 | 3 | 18 | *dropped: fails cash+* |
| Mobile home / manufactured repair | 4 | 2 | 3 | 3 | 2 | 4 | 18 | *dropped: fails cash+* |

\* Tier from `TAM × textable%` using mid-range [ESTIMATE] values. Most candidates land RED/YELLOW on
estimates — that is the point of the proof phase: TAM verification + the Veriphone sample test can
move them. Foundation repair is the only GREEN on estimates.

## Top 5 + why

1. **Foundation repair / structural stabilization** (26) — the docs' own archetype. $8–15k jobs at
   ~45–50% margin pass the $2.5k test by 2–3×; high urgency (structural damage, safety); large
   owner-operated base with mobile numbers (high textability); strong ad proof already exists.
   Only GREEN tier on estimates (~13.7k reachable).
2. **Septic service & repair** (23) — the most underserved of the set: virtually no agencies market
   it, extreme urgency (sewage backup = call now), owner-operated = best textability profile. Two
   risks: ad proof may be thin (verify — the niche may buy no leads yet), and replacement jobs pass
   the cash+ test but pumping alone fails. Tier RED/YEL on estimates — TAM verification matters most.
3. **Basement waterproofing / flood mitigation** (22) — same family as foundation repair; strong
   trigger after storm events; established advertisers. Slightly smaller TAM on estimates; tier
   borderline RED/YEL — directory counts in DFW/Houston (flood-prone) could flip it.
4. **Crawlspace encapsulation / mold remediation** (22) — high-margin service work, health-triggered,
   low agency presence, owner-operated (high textability). TAM is the open question (~8–12k est);
   needs the directory + Ads Library proof.
5. **Men's health / TRT clinics** (21) — heavy ad proof (the niche demonstrably buys leads), decent
   TAM. Weaknesses: becoming "marketed-to" (underserved score low), front-desk landlines depress
   textability, and the cash+ math runs on per-patient LTV rather than per-job — needs a pricing
   assumption (e.g., $300–800 per qualified lead). Best candidate if the agency ever wants a
   higher-ticket, less seasonal vertical.

Near-misses kept for the coaching call: **water damage restoration** (extreme urgency but competitive +
franchise call centers), **termite/WDI** (borderline cash+), **asphalt/parking lot maintenance** (recurring
contracts; materials-heavy margin).

## Proof checklists (run in order)

For EVERY finalist: ① Meta Ads Library search → count advertisers running 30–90d+ ② Google
`"[niche] marketing agency"` + `"[niche] leads"` → agency competition ③ directory counts in
DFW + 2 metro peers ④ Veriphone sample test (150 leads, one city → % mobile).

1. **Foundation repair** — Ads Library: `foundation repair` (US). Google: `foundation repair marketing agency`,
   `foundation repair leads`, `foundation repair facebook ads`. TAM: IBISWorld "Foundation & Structural
   Repair in the US" (est. ~25k); Google Maps counts DFW / Houston / Phoenix. Veriphone: DFW 150-lead sample.
2. **Septic** — Ads Library: `septic tank service`, `septic repair`, `septic pumping`. Google: `septic marketing
   agency`, `septic leads`. TAM: directory counts (Dun & Bradstreet / Google Maps) — US est. ~10–15k.
3. **Basement waterproofing** — Ads Library: `basement waterproofing`, `flood mitigation`. Google:
   `basement waterproofing marketing agency`. TAM: IBISWorld/industry; DFW + Houston counts (flood-prone).
4. **Crawlspace / mold** — Ads Library: `crawl space encapsulation`, `mold remediation`. Google: `mold
   remediation marketing`. TAM: directory counts; est. ~8–12k.
5. **TRT clinics** — Ads Library: `TRT clinic`, `testosterone therapy`, `men's health clinic`. Google:
   `TRT clinic marketing agency`, `men's health clinic leads`. TAM: clinic directories; est. ~15–20k.

## PROOF GAPS (blocked this run — web tools down)

- Live TAM counts for all five (listed queries above) — [ESTIMATE] until verified.
- Meta Ads Library run dates for all five — a human or browser agent must run these.
- Veriphone line-type samples (150 leads/city each) — Skyline task spec; % mobile feeds the tier.
- Gross-margin sources per niche — [ESTIMATE] until cited.
- Fix web access first: `hermes model` → log in to Nous Portal (managed Firecrawl) or set
  `FIRECRAWL_API_KEY` in `~/.hermes/.env`; browser provider needs a working CDP endpoint.
  Then re-run this skill with `DEPTH: quick` for a verified scorecard.
