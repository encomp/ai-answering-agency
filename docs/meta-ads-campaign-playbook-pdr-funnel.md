# Meta Ads Campaign Playbook — PDR Lead Funnel (Señal Flow)

**Scope:** how to set up a Meta Ads campaign whose *stated* goal is a booked appointment at the end of the funnel — and what has to be true for that to actually work.
**Funnel under review:** `https://senalflow.com/en/demo/pdr-lead-funnel/` (demo shop, published price bands).
**Date:** 2026-09-23 · **Advertiser context:** US PDR shops, DFW-first.
**Tags:** `[VERIFIED]` read from source this run · `[ESTIMATE]` reasoning from comparable data · `[UNVERIFIED]` could not check (method given).

---

## 0. Executive summary — the five things that decide this campaign

1. **"Optimize for booking" is the right instinct but the wrong *first* setting.** Meta needs ~50 optimization events per ad set per week to exit the learning phase [VERIFIED: Meta Business Help Center, learning phase]. A booking is the rarest event in the funnel. Optimizing for it on day one buys you a permanently unstable ad set at a high CPA.
2. **The funnel's highest-value jobs never see the booking step.** Multi-panel, creased, hail and insurance jobs are deliberately routed to *"have a tech call me"* — no calendar, no booking [VERIFIED: funnel source]. If you optimize only for online bookings, Meta learns to buy you **$195–$415 single-dent tire-kickers** and starves you of the $600–$1,260 jobs. This is the single most important design constraint in this document.
3. **There is no Meta Pixel on the funnel today — only GA4** (`G-9Q1BT4DRCS`) [VERIFIED: page source]. Zero events, zero audiences, zero optimization signal. Nothing can be optimized until this is wired, browser **and** server-side.
4. **The funnel already computes a dollar value per lead** — and that is your biggest unfair advantage. Passing `value` lets Meta optimize for *job value* instead of lead count, which is how you avoid buying cheap work. [VERIFIED: quote engine source]
5. **The demo's booking is not a real booking.** Slots are generated client-side (`daysAhead: 5`, four times/day, weekends skipped) with `simulateTextDelivery: true` and `leadWebhookUrl: null` [VERIFIED: config]. Until a real calendar holds real availability, a `Schedule` event is a claim your business can't honor — and Meta will optimize hard toward whatever you tell it "booking" means.

**Bottom line:** the campaign is buildable and the funnel is a genuine asset, but the correct sequence is *tracking → qualified-lead volume → booking optimization → value optimization → offline revenue*, not *booking optimization → hope*.

---

## 1. What you actually have (funnel teardown)

Astro-built, single-page, white-label by shop: the page reads `?shop=<slug>` and fetches `/tools/configs/<slug>.json` (falls back to `/tools/configs/funnel-default.json`) [VERIFIED].

### 1.1 The question flow

| Step | Question | What it produces | Routing effect |
|---|---|---|---|
| 1 | Dent size (small / medium / large) | `sizeTier` | `large` → **high value** |
| 2 | Dent count (1 / 2-3 / 4-10 / 10+) | `dentCount` | `10+` → **abandon funnel, route to callback** |
| 3 | Panel (hood/roof/door/fender/quarter/trunk/multi) + "sharp crease" checkbox | `panel`, `hasCrease` | `multiple` panel → **high value**; crease → +50% surcharge AND high value |
| 4 | Vehicle year / make / model | aluminum detection | aluminum → +25% surcharge |
| 5 | ZIP + timing (this week / few weeks / just pricing) | `zip`, `timing` | ZIP outside `serviceArea.zipPrefixes` → **dead end** |
| 5b | *(optional)* Insurance status | `insurance` | `filed`/`considering` → **high value** (question disabled by default) |
| 6 | Name + mobile + email | contact | route split below |

Steps 2, 3, 5 and 6 are conditional — the engine recomputes the step list per path [VERIFIED: `pdrFunnel.js`].

### 1.2 Price engine (verified arithmetic)

```
quote = (base[sizeTier] + additionalDents × perDent) × panelMultiplier × surchargeMultiplier
        floored at pricing.minimum
additionalDents: 1→0, 2-3→2, 4-10→6
surchargeMultiplier = 1 + (crease ? 0.50 : 0) + (aluminum ? 0.25 : 0)
```

Default bands [VERIFIED: `funnel-default.json`]:

| Tier | Base range | ×crease | ×multi-panel (1.6) | ×crease+multi-panel |
|---|---|---|---|---|
| Small | $215–$275 | $323–$413 | $344–$440 | $516–$660 |
| Medium | $285–$415 | $428–$623 | $456–$664 | $684–$996 |
| Large | $560–$840 | $840–$1,260 | $896–$1,344 | $1,344–$2,016 |
| Minimum floor | $195 | | | |

Plus `typicalBands` shown as the "published market range" (small $195–295, medium $250–450, large $500–900) and additional dents at $50–100 each.

### 1.3 The three exits — this is the whole ballgame

| Exit | Trigger | What the user sees | Value tier | Booking? |
|---|---|---|---|---|
| **A. Precise quote → calendar** | Standard route | Exact price for their panel/vehicle, then "Pick a time" | $195–$415 typical; up to ~$660 | ✅ **Yes — online booking** |
| **B. Tech callback** | 10+ dents, `multiple` panel, crease, `large`, or insurance filed/considering | "Leave your number and a tech will call you with a real figure" | **$600–$2,016** | ❌ No calendar — manual call |
| **C. Out of area** | ZIP not in `zipPrefixes` | "That's outside the service area" — dead end | $0 | ❌ Wasted click |

**Read that table again.** Route B — the callback route — is where the funnel's *own logic* puts the biggest jobs. Optimization for "booking at the end of the funnel" points Meta at Exit A, i.e. the smallest jobs it can find. That regression is invisible in the ad account (bookings go up, revenue doesn't) and it is the #1 way this project fails quietly.

There is also a **route-completeness bug worth noting**: `routing.highValueSizeTiers` and the insurance flag only influence *routing*; nothing in the funnel changes *which exit* the user sees based on tier beyond `multiple`/`crease`/`many`. Hail ("10+ dents") collapses to the string `"hail"` in the engine and always goes to callback [VERIFIED]. So hail demand — the seasonal money spike — is 100% manual follow-up, 0% bookable online.

---

## 2. The two structural problems you must design around

### Problem 1 — Event volume (the learning-phase tax)

Meta exits the learning phase after ≈**50 results per ad set per 7 days** [VERIFIED], and any significant edit resets it. Run the arithmetic before choosing an optimization event:

| Optimization event | Events needed/wk | Est. cost per event | Weekly spend to exit learning | Daily |
|---|---|---|---|---|
| `Lead` (step 6 submit) | 50 | $20–$45 [ESTIMATE] | **$1,000–$2,250** | $145–$320 |
| `Schedule` (online booking) | 50 | $50–$140 [ESTIMATE] | **$2,500–$7,000** | $360–$1,000 |

If the client's out-of-pocket is ~$2,500/mo (~$580/wk), then **optimizing for `Schedule` from day one means the ad set never leaves learning.** Never. It will spend the budget and report "Learning limited."

*Mitigations, in order of value:*
- **Consolidate: one campaign, one ad set** while budget is under ~$2k/mo. Ad sets split your event count; splitting is what kills you.
- Start on the event you can actually feed (usually `Lead`), then flip.
- Optimize for a **commitment event that both major exits produce** (see §2 Problem 2) rather than only the calendar exit.

### Problem 2 — High-value jobs are unbookable

Fixes, pick one deliberately:

**Option A — Optimize on a "commitment" event (recommended).**
Fire `Schedule` on **both** Exit A (calendar booked) and Exit B (tech callback requested), differentiated by a parameter (`schedule_type: "onsite_booking"` vs `"tech_callback"`). Both are genuine commitments — the customer has given contact details and agreed to a time or a call. You then pass `value` = estimated quote so Meta chases dollars, not volume.

- ✅ Volume roughly doubles → learning phase reachable.
- ✅ Callback jobs carry the $600–$2,016 values, so Meta gets paid to find hail/multi-panel/insurance work.
- ⚠️ Semantics: a callback is a *scheduled* contact — defensible for `Schedule`, but report on it separately and never present it to the client as "online bookings."
- ⚠️ It only works if the callback is actually honored fast. A callback request is a 5-minute-latency promise; if nobody calls, you're paying for high-value leads that rot.

**Option B — Optimize on `Schedule` (calendar only), fix the top of funnel separately.**
Cleanest semantics, lowest volume, and you accept that Meta will systematically hunt small single-dent jobs. Only viable if you also run a parallel callback-gen campaign or the shop's ticket mix is intentionally door-ding/dealer-recon.

**Option C — Optimize on `Lead`, value-weighted.**
Highest volume, fastest learning, no commitment filter. You get tire-kickers, but with `value` passed the algorithm still skews toward bigger estimates. Good Phase-1 default.

**Recommendation: Phase 1 = Option C (`Lead` + value). Phase 2 = Option A (`Schedule` + value). Use Option B only if the shop insists on literal online bookings being the KPI.**

---

## 3. What's missing from the tracking stack (fix before spending $1)

Verified current state: **GA4 via gtag only** (`G-9Q1BT4DRCS`), **no Meta Pixel, no Conversions API, no booking calendar integration** [VERIFIED: page + bundle source]. `leadWebhookUrl` is `null` in the default config — so leads currently go nowhere.

### 3.1 The full event map

Browser events (Pixel) **and** mirrored server events (CAPI) with a shared `event_id` for deduplication [VERIFIED: Meta developer docs — pass `eventID` as the 4th arg to `fbq('track')` when running Pixel + CAPI together].

| # | Funnel moment | Meta event | Why / params |
|---|---|---|---|
| 1 | Page load | `PageView` (base) | Retargeting pool at minimum |
| 2 | Step 1–3 progress | custom `FunnelStep` | Diagnose drop-off per question |
| 3 | Steps 4–5 complete (in-area) | custom `QualifiedStart` | Distinguishes "bounced" from "qualified then abandoned" |
| 4 | **Step 6 submit, precise route** | **`Lead`** | `value` = quote midpoint, `currency` USD, `content_category` = sizeTier |
| 5 | **Slot selected & confirmed** | **`Schedule`** | `value` = quote midpoint, `schedule_type: onsite_booking` |
| 6 | **Callback route confirmed** | **`Schedule`** *(Option A)* or `Contact` *(Option B)* | `value` = high-value estimate, `schedule_type: tech_callback` |
| 7 | Out-of-area rejection | custom `OutOfArea` | **Never optimize on it** — but track it; it's your geo-targeting error meter |
| 8 | Estimate viewed, no contact | custom `EstimateView` | Mid-funnel signal; best retargeting audience you have |

**Parameter notes:** `Lead` and `Schedule` both accept optional `value` + `currency` [VERIFIED: Meta Pixel API reference]. `value` is what unlocks value-based optimization — without it, a $195 dent and a $2,016 hail job count identically.

### 3.2 Event-match quality — the reason this funnel can outperform a lead form

At step 6 you collect **name, mobile, email, ZIP, and vehicle**. CAPI accepts hashed `em`, `ph`, `fn`, `ln`, `zp`, `country` plus `fbp`, `fbc`, `client_ip_address`, `client_user_agent` [VERIFIED: CAPI parameter docs]. Five independent identifiers in one payload puts event-match quality in the top bucket, which directly buys cheaper delivery and better attribution. Most local-service advertisers send nothing but a cookie. **Pass all of it.**

### 3.3 The two implementation requirements nobody remembers

**a) Capture `fbclid` at step 6 and persist it.**
Read `fbclid` from the URL on landing, stash it, submit it with the lead. Convert to `fbc` (`fb.1.<landing_timestamp_ms>.<fbclid>`) and pass in CAPI; store the raw value on the lead record in the CRM. This is what makes **offline** conversion uploads (attended appointment, closed job) match deterministically instead of probabilistically. Without it, Phase 3 is guesswork.

**b) Server-side event must be the source of truth for the deep events.**
The funnel's lead webhook is the natural CAPI transport. Fire `Lead`/`Schedule` from the browser *and* the server with the same `event_id`; Meta dedupes and keeps the richer payload. Browser-only tracking loses a meaningful share of conversions to blockers and ATT — and the deepest events (booking confirmed) are exactly the ones you can least afford to undercount, because they're your optimization target.

### 3.4 Domain, dataset and ownership decisions

- **Domain verification** in Business Manager for the funnel's domain (and the client's domain if the funnel is served on a subdomain of it). Required for event configuration and for clean pixel ownership.
- **AEM note:** the old "prioritise 8 conversion events per domain" requirement **no longer applies** to web conversion optimization [VERIFIED: Meta AEM doc]. Don't let stale 2021 advice drive your setup.
- **Pixel ownership:** for an agency, one **dataset per client** in the agency's Business Manager, with the client granted access — avoids blending clients' data and makes handoff clean. If the client owns their own ad account + pixel, install theirs instead and keep a documented access matrix.
- **One funnel, many shops:** the `?shop=` white-label pattern means every client shares a URL path. Segment by shop ID in *every* event (`content_group` / custom param) or client data will cross-contaminate audiences.

---

## 4. Campaign structure

### 4.1 Objective and settings

| Setting | Recommendation | Why |
|---|---|---|
| Objective | **Sales** (conversion campaign), website conversion location | The funnel exists to qualify and price. Lead Ads can't run the quote engine — you'd be paying to collect unqualified contacts. |
| Buying type | Advantage+ / unified flow (manual+Advantage+ merged, Feb 2026; AI is the default) | Advantage+ sales campaigns reported ~9% better cost per conversion on average [VERIFIED: Meta] |
| Optimization event | Phase 1 `Lead` → Phase 2 `Schedule` | See §2 |
| Attribution | 7-day click, 1-day view | Standard for local services |
| Budget | Consolidated, campaign-level | Concentrate events per ad set |
| Placements | Advantage+ placements (auto) | Feed + Reels carry local service performance; Stories/Reels cheap reach |
| Bid strategy | Highest volume first; **cost cap** once you know real CPA | Cost cap after ~2–3 weeks of stable data |
| Audience | Broad, geo-bound. No interest stacking. | The funnel *is* the targeting. Let the algorithm use the signal. |

### 4.2 Why not Meta Lead Ads (instant forms)

Worth a deliberate decision, because they're cheaper and often pitched for this vertical:

| | Website funnel | Instant form |
|---|---|---|
| CPL | Higher | Lower (typically 30–50% lower) [ESTIMATE] |
| Qualification | 6 questions + price anchor + real routing | Name/phone, maybe 2 custom questions |
| Price anchoring | Yes — user sees a number | None |
| Booking | Native | None (or a link-out) |
| Optimization signal | Rich (steps, value, tiers) | Thin (one `Lead`) |
| Lead quality | Higher, self-selected | Notably worse for high-intent trades |

Instant forms are a legitimate **secondary** arm to test volume and offer/creative angle cheaply. They are not a substitute for the funnel — using them as primary throws away everything the funnel is built to do.

### 4.3 Structure phasing (30-day)

| Days | Phase | Objective / optimization event | Daily budget | Success metric |
|---|---|---|---|---|
| 1–3 | **Blockers** | — | $0 | Pixel + CAPI fire, calendar holds real slots, webhook → CRM verified |
| 4–10 | **Learn** | Sales, optimize `Lead` (value passed) | $30–$50 | CPL, step-6 completion rate, `value` distribution |
| 11–21 | **Qualify** | Flip to `Schedule` (commitment event, Option A) once `Lead` ≥ 50/wk | $50–$80 | Cost per booking, % high-value tier, callback SLA |
| 22–30 | **Value** | Switch bidding to maximize **value**; build lookalikes from high-value leads | $80–$150 | Cost per $1,000 of quoted value; cost per booked appointment |
| 31+ | **Offline loop** | Upload attended/closed jobs with real invoice value | scale winners | Cost per closed job, ROAS on cash collected |

**Discipline rule:** don't touch the ad set during learning. Every significant edit restarts the 50-event clock [VERIFIED]. Change creative *additively*; keep budget changes under ~20% and spaced 3+ days apart.

### 4.4 Geo — the out-of-area leak

The funnel rejects ZIPs outside `serviceArea.zipPrefixes` [VERIFIED], and default config ships an **empty** prefix list (i.e. "accept everything"). Two failure modes:

- **Prefix list empty in production** → you pay for out-of-area leads who hit a dead end at step 5.
- **Ad geo wider than the funnel's service area** → same leak, guaranteed. Meta geo targeting and `zipPrefixes` must be derived from the same source of truth and re-synced quarterly.

Set an **inverse geo** setup for pilots: target the shop's actual radius/service ZIPs, and add `OutOfArea` events as an early-warning metric — a rising rate means your targeting drifted or the shop's coverage shrank.

---

## 5. Budget math and what good looks like

### 5.1 Benchmarks (verified where possible)

| Metric | Benchmark | Source |
|---|---|---|
| CPM (small business, 2026) | $11–$18 | [VERIFIED: M.Wolf Media 2026 data] |
| CPL, small business B2C | $28–$72 | [VERIFIED: M.Wolf Media] |
| CPL, well-optimized local services (HVAC/dental/legal) | $15–$60 | [VERIFIED: Stackmatix] |
| CPL, consumer services via Lead Ads | ~$8–$30 | [VERIFIED: adlibrary.com 2026] |
| Learning phase threshold | ~50 results/ad set/week | [VERIFIED: Meta] |
| **PDR-specific CPL / cost per booked appointment** | **no reliable public benchmark** | [UNVERIFIED] — your own data becomes the benchmark in week 2 |

### 5.2 Planning assumptions for PDR (state them out loud to the client)

| Assumption | Planning value | Note |
|---|---|---|
| CPL at step 6 | $20–$45 [ESTIMATE] | Cosmetic/low-urgency demand prices above emergency trades |
| Step 6 → `Schedule` (commitment) | 35–55% [ESTIMATE] | Price shock at the booking step is the main killer |
| Cost per booked appointment | **$50–$140** [ESTIMATE] | |
| Blended ticket value | $300–$500 consumer dents; $600–$2,016 high-value route | [VERIFIED: funnel bands] |
| Show-up rate | 70–85% [ESTIMATE] | Unverified until the calendar is real |

### 5.3 The honest break-even test

At a $2,500/mo out-of-pocket, an all-in $90 cost per *booked* appointment and a $400 average ticket:

```
~28 booked appointments/mo → ~22 attended → ~$8,800 quoted revenue
```

Against a 60–70% close rate on attended appointments that clears the client's cost several times over — **if** the ticket mix holds at $400. The number to watch is not CPA-booking; it's **average quoted value per booking**. If Meta optimizes count, average ticket slides toward the $195 floor and the same CPA turns unprofitable. Which is exactly why `value` must be in the payload from day one.

### 5.4 Sensitivity — where this breaks

| If CPL is… | And step6→booking is… | Cost/booking | Verdict at $400 ticket |
|---|---|---|---|
| $20 | 50% | $40 | Strong |
| $35 | 40% | $88 | Workable |
| $45 | 30% | $150 | Marginal — fix the booking step or the offer before scaling |
| $60+ | <30% | $200+ | Broken — funnel problem, not an ads problem |

---

## 6. Creative and offer (late-September reality)

**Timing context:** today is 23 Sep 2026. Hail season in the DFW corridor runs roughly May–August [VERIFIED: prior niche research]. You are launching into the **low-urgency window**: consumer hail panic is gone, door-ding demand is slow and price-sensitive, and the reliable volume is *dealership reconditioning* (B2B) plus **unrepaired hail damage from earlier storms** (a real, addressable segment — people with a claim or a dented car who never booked).

### Angles ranked for this window

1. **"Unfixed hail damage from this spring"** — direct, seasonal, high-intent. Point at existing damage, not new storms. Highest-value route into the callback path.
2. **Instant price, no phone tag** — the funnel's literal pitch. "Get a real number in 60 seconds, then pick a time." Strongest hook for the booking exit.
3. **We come to you (mobile PDR)** — removes the biggest friction (dropping the car off).
4. **Before/after, tight crop, daylight, real dent** — PDR is visually satisfying; process video (slow reveal, tool working the metal) outperforms static in Reels.
5. **Insurance / deductible** — high-value route trigger, but the insurance question is **disabled** in the default config [VERIFIED]. Turning it on changes routing *and* the lead's funding source. Decide deliberately, don't enable by accident.
6. **Aluminum panels** (F-150, Tesla, Range Rover) — expertise signal for a specific, affluent, high-surprise-cost audience [VERIFIED: `aluminumVehicles` list].

### Creative structure that suits this funnel

- **Lead with the estimate, not the shop.** The single strongest promise this funnel can make is *a real price before you ever talk to a human.*
- Vertical video 9:16 for Reels/Stories + 1:1/4:5 for Feed. 3–5 genuinely different hooks, not 5 edits of one.
- Keep the funnel link as the CTA (no "call now" — you're buying the funnel, not a phone call; a call-now CTA bypasses the qualification that makes the funnel worth having).
- Add a **storm-response creative set** ready to switch on: storm-path geo + hail-specific angles + budget surge. Hail is a days-to-weeks window; the shops that win it have assets pre-built [VERIFIED: prior niche research].

---

## 7. Weekly optimization loop

Look at exactly six numbers, in this order:

| # | Metric | What "bad" looks like | Action |
|---|---|---|---|
| 1 | **Average quoted value per booking** | Drifting toward $195–275 | You're optimizing count. Switch to value bidding; check high-value routing works |
| 2 | Step-6 completion rate | <25% of step-1 starters | Funnel friction, not ads. Shorten or reorder questions |
| 3 | Step 6 → booking rate | <30% | Price shock or weak slot UX. Test a "from $X" framing, more slot times |
| 4 | Out-of-area rate | >10% | Geo/funnel service-area mismatch. Fix targeting, not creative |
| 5 | Callback SLA (high-value route) | >15 min to first call attempt | You're burning your most valuable leads. Automate the text-back at minimum |
| 6 | Cost per booked appointment | > $150 | Don't scale. Fix 1–5 first |

**Rename the KPI for the client.** Sell "cost per booked appointment," but report "cost per **$1,000 of quoted value**" internally — it's the metric that predicts profit and the one that catches the cheap-job regression early.

---

## 8. Pre-launch checklist (blockers — hard gates)

- [ ] **Real booking calendar wired** with true availability (Google Calendar / Calendly / CRM calendar). Client-side generated slots with no availability source = fake `Schedule` events = Meta optimizing to a fiction.
- [ ] **Meta Pixel installed** (base + all 8 events in §3.1), verified in Events Manager.
- [ ] **Conversions API wired** off the funnel's lead webhook, `event_id` shared with the browser event, `fbclid`/`fbc`/`fbp` + hashed `em`/`ph`/`fn`/`ln`/`zp` included. Target event-match quality ≥ 8/10.
- [ ] **`leadWebhookUrl` set** (currently `null` [VERIFIED]) → CRM with the full quote payload, tier, route, and `fbclid`.
- [ ] **`serviceArea.zipPrefixes` populated** and reconciled with the ad account's geo targeting.
- [ ] **SMS confirmation actually sends** (`simulateTextDelivery` currently `true`) — the funnel's promise is "you'll get a text confirmation." No text = no-shows.
- [ ] **Callback route staffed** with a defined SLA. This route carries your best jobs.
- [ ] **Domain verified**, dataset per client, access matrix documented.
- [ ] **UTM convention** set (`utm_source=facebook&utm_medium=paid&utm_campaign=<shop>_<phase>&utm_content=<creative_id>`) so GA4 and CRM can reconcile against Meta.
- [ ] **Offer, budget, and KPI agreed in writing** with the client — including the phrase "booked appointment," defined precisely.

---

## 9. Pitfalls

1. **Optimizing for the literal last step first.** Guarantees a Learning-Limited ad set and blames Meta for a math problem.
2. **Letting the funnel's routing silently determine your customer mix.** Bookings optimized alone = small jobs. Always pass `value`.
3. **Not passing `value`.** The engine computes it for free; failing to send it is leaving the funnel's main advantage on the table.
4. **Browser-only tracking** on the events you optimize for. Under-counted deep events = under-delivery.
5. **No `fbclid` capture.** Makes every future offline/revenue upload probabilistic.
6. **Fake availability.** Booking without a calendar devalues the `Schedule` event and burns customer trust with double-bookings.
7. **Editing during learning.** Each significant edit restarts the 50-event clock.
8. **Lead Ads as primary.** Cheaper CPL, thinner pipeline, no price anchoring.
9. **Geo drift.** Meta geo and `zipPrefixes` from one source of truth or you pay for dead ends.
10. **Enabling the insurance question by accident.** It silently changes routing tiers and lead funding mix.
11. **Ignoring the low-urgency season.** Sept–Apr consumer dent demand is slow; the offer must carry more weight, and B2B/dealership volume deserves its own campaign.
12. **Measuring bookings, not revenue.** Optimizing for booking trains "people who will pick a slot," not "people who will pay." Close the loop with offline uploads.

---

## 10. Decisions I need from you before implementation

1. **Commitment definition:** do we count a *tech callback request* as a booking-equivalent conversion (Option A — recommended, unlocks volume + high-value) or is the KPI strictly the online calendar booking (Option B)?
2. **Real calendar:** which system holds the shop's real availability? (Determines whether the `Schedule` event can be honest.)
3. **Client vs agency pixel/dataset ownership** for the first pilot.
4. **Insurance question on or off** — it changes routing tiers and lead economics.
5. **Pilot budget ceiling** — this decides Phase 1 optimization event (§2, §5.3).
6. **Is the first campaign consumer-facing, dealership/B2B, or both?** They need different creative, offer, and geo.
7. **Spanish/bilingual variant** — Señal Flow already supports EN/ES; DFW has meaningful Spanish-dense ZIPs. Worth a second creative set from day one?

---

## 11. Sources (this run)

- Meta Pixel API reference — standard events incl. `Schedule` = *"When a person books an appointment to visit one of your locations"*, `Lead`, `Contact`; `eventID` dedup guidance — developers.facebook.com/docs/meta-pixel/reference
- Meta Business Help — About the learning phase (~50 results/ad set/week; edits reset) — facebook.com/business/help/112167992830700
- Meta Business Help — About offline conversions (datasets, real-world bookings) — facebook.com/business/help/1142103235885551
- Meta Business Help — About Advantage+ sales campaigns (~9% cost-per-conversion improvement; connect first-party data) — facebook.com/business/help/1362234537597370
- Meta Business Help — Aggregated Event Measurement (8-event prioritisation no longer required for web optimization) — facebook.com/business/help/721422165168355
- Meta Pixel standard events spec (17 events) — facebook.com/business/help/402791146561655
- Funnel source: page HTML, `pdr-lead-funnel.astro.*.js`, `pdrQuoteEngine.*.js`, `pdrFunnel.*.js`, `/tools/configs/funnel-default.json` — senalflow.com
- Benchmarks: M.Wolf Media (2026 small-business CPM/CPL data), Stackmatix (local services CPL), adlibrary.com (2026 service-business playbook)
- Prior internal research: `docs/niche-research-paintless-dent-repair.md`, `docs/pain-validation-pdr.md` (hail seasonality, DFW market)

**Not verified this run:** Meta Ads Library advertiser/run-date scan for PDR and hail-damage keywords (`hail damage repair`, `paintless dent repair`, `dent removal near me`, by metro) — no PDR-specific CPL or cost-per-booked-appointment benchmark exists publicly; treat internal week-2 data as the baseline.
