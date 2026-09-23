# Implementation Spec — Meta Ads Tracking for the PDR Lead Funnel

**Purpose:** exactly what must be built for the campaign to optimize on the **commitment event (Option A)**, decided 2026-09-23.
**Audience:** whoever edits the funnel code (dev, you, or a Skyline task).
**Prereq reading:** `docs/meta-ads-campaign-playbook-pdr-funnel.md` §2–§3.
**Tags:** `[VERIFIED]` read from source this run · `[ESTIMATE]` reasoned · `[UNVERIFIED]` confirm before relying on it.

---

## 1. Architecture

```
                       ┌──────────────────────────────────────────┐
   Meta ads ──click──► │  Funnel (senalflow.com/?shop=<slug>)     │
   (?fbclid=…)         │  Astro page + pdrFunnel + quote engine   │
                       └───────────┬──────────────────┬───────────┘
                                   │                  │
                    browser events │                  │ step-6 submit
                      (Pixel/fbq)  │                  │ (fetch → leadWebhookUrl)
                                   ▼                  ▼
                       ┌──────────────────┐  ┌──────────────────────┐
                       │ Meta Pixel       │  │ Your server endpoint │
                       │  + event_id      │  │  → CAPI (server)     │
                       └────────┬─────────┘  │  → CRM (lead record) │
                                │            └──────────┬───────────┘
                        dedupe on event_id             │
                                ▼                       ▼
                       ┌────────────────────────────────────────────┐
                       │ Meta Events Manager — one dataset/shop     │
                       └───────────────┬────────────────────────────┘
                                       ▲
                        Phase 3 offline upload (attended / closed job,
                        real invoice value, matched on fbc + hashed PII)
                                       │
                                ┌──────┴──────┐
                                │  CRM / ops  │  ← callback SLA lives here
                                └─────────────┘
```

Three transports, one identity model. Everything below exists to make the same event, from any transport, land as **one** conversion with the **right value**.

---

## 2. Identity, deduplication and click attribution

This is the part that silently ruins campaigns when skipped. Four identifiers, four jobs:

| Identifier | Created where | Purpose | Lifetime |
|---|---|---|---|
| `fbclid` | URL on landing (`?fbclid=…`) | **Deterministic** ad-click attribution. The single most valuable field in the whole build. | Store on the lead record permanently |
| `_fbc` | Derived: `fb.1.<landing_ts_ms>.<fbclid>` | CAPI `fbc` field — Meta's click identifier | Session, persist 90d |
| `_fbp` | Pixel cookie `_fbp` (read `document.cookie`) | Browser identity for CAPI matching | 90d |
| `lead_id` | UUID v4 at step-6 submit | **Your** primary key. Ties browser + server + CRM + offline events together. | Permanent |

### 2.1 `event_id` scheme (use this exact pattern)

```
event_id = `<shop_id>.<lead_id>.<event_name>`
# e.g. dentco-dallas.7f3a91c4-…-a2.Schedule
```

Why deterministic rather than a random UUID: if the server retries a webhook — or CAPI returns a transient error — replaying the *same* `event_id` is idempotent and cannot double-count. Random IDs silently inflate conversions on every retry.

**Rules:**
- Same `event_name` + same `event_id` across Pixel and CAPI → Meta dedupes (dedup window is measured in hours; keep retries under 48h).
- Do **not** reuse an `event_id` across different event names.
- Send `eventID` as the **4th argument** to `fbq('track', …)` [VERIFIED: Meta Pixel API reference].
- Events fired **before** step-6 submit (steps 1–5) have no `lead_id` yet — use `` `<shop_id>.anon.<session_uuid>.<event_name>` `` for those; they're reporting-only events and are never optimization events, so dedup precision there is not critical.

### 2.2 `fbc` construction — get the timestamp right

```
fbc = "fb.1." + <epoch_ms of the LANDING, when fbclid was first seen> + "." + fbclid
```

Use the **landing** timestamp, not the submit timestamp. If you build it at submit time, the click-to-event gap Meta infers is wrong and attribution quality degrades. Persist `fbclid` and its landing timestamp together (sessionStorage is enough; the CRM copy is what survives).

---

## 3. Event map (locked)

| # | Event | Type | Fires when | Transport | Optimization? |
|---|---|---|---|---|---|
| 1 | `PageView` | standard | Funnel page load | Pixel | No (base) |
| 2 | `ViewContent` | standard | Intent step 1 rendered | Pixel | No |
| 3 | `FunnelStep` | custom | Each step completed (1–5) | Pixel | No — drop-off diagnosis |
| 4 | `QualifiedStart` | custom | Step 5 passed: ZIP in area **and** timing answered | Pixel | No |
| 5 | `OutOfArea` | custom | Step 5 ZIP rejected | Pixel + server | No — **geo-error meter** |
| 6 | `EstimateView` | custom | Estimate rendered, no contact submitted | Pixel | No — best retargeting pool |
| 7 | `Lead` | standard | Step-6 submit, **precise route** | Pixel + CAPI | **Phase 1 optimization** |
| 8 | `Schedule` | standard | Slot picked & confirmed — `schedule_type: onsite_booking` | Pixel + CAPI | **Phase 2 optimization** |
| 9 | `Schedule` | standard | Callback requested — `schedule_type: tech_callback` | Pixel + CAPI | **Phase 2 optimization** |

**Why 8 and 9 are the same event name:** the decision was to make both exits reward the algorithm. Differentiating with `schedule_type` keeps reporting honest while presenting Meta a single, larger, value-weighted objective. Build two **custom conversions** off `schedule_type` for client reporting — never present callback volume to the client as "online bookings."

**Why `OutOfArea` matters:** it is the only early-warning signal that your Meta geo targeting has drifted wider than the funnel's `serviceArea.zipPrefixes`. Target: <10% of qualified starts.

---

## 4. Browser layer (Pixel)

Load once, before the funnel island mounts:

```html
<script>
!function(f,b,e,v,n,t,s){/* standard Meta Pixel base snippet */}
fbq('init', '<PIXEL_ID>');
fbq('track', 'PageView');
</script>
```

Then, from the funnel's state machine:

```js
// step 6 submit — precise route (has a computed quote)
const quoteValue = Math.round((quote.low + quote.high) / 2);
const eid = `${shopId}.${leadId}.Lead`;

fbq('track', 'Lead', {
  value: quoteValue,
  currency: 'USD',
  content_name: 'pdr_estimate',
  content_category: inputs.sizeTier,          // small | medium | large
  content_ids: [shopId]
}, { eventID: eid });

// slot confirmed — online booking  (§3 row 8)
fbq('track', 'Schedule', {
  value: quoteValue,
  currency: 'USD',
  content_name: 'pdr_onsite_booking',
  content_ids: [shopId]
}, { eventID: `${shopId}.${leadId}.Schedule.onsite` });

// callback requested — §3 row 9
fbq('track', 'Schedule', {
  value: callbackEstimate,                    // see §5 — must be configured
  currency: 'USD',
  content_name: 'pdr_tech_callback',
  content_ids: [shopId]
}, { eventID: `${shopId}.${leadId}.Schedule.callback` });
```

> ⚠️ Note the two `Schedule` variants use **distinct `event_id`s**. Same event name, different IDs, different server calls. If you reuse one ID across both, one will be deduped away and you will lose half your conversions.

Also capture on landing, before anything else fires:

```js
const p = new URLSearchParams(location.search);
const fbclid = p.get('fbclid');
if (fbclid) {
  sessionStorage.setItem('fbclid', fbclid);
  sessionStorage.setItem('fbclid_ts', String(Date.now()));   // landing time, not submit time
}
// _fbp is set by the Pixel; read it at step 6:
const fbp = (document.cookie.match(/_fbp=([^;]+)/) || [])[1] || null;
```

Stash all UTM params too — they reconcile GA4 against Meta when numbers disagree (they will).

---

## 5. The callback-route value gap (blocking)

**The problem, verified in source:** for `dentCount === "many"` (and any high-value-routed path the funnel sends to callback), the quote engine returns `{ routeToCallback: true }` and **no price at all** [VERIFIED: `pdrQuoteEngine.BgTNzsfx.js`]. The `quote` object in the lead payload is therefore empty for precisely the jobs Option A exists to capture.

So today, under Option A, the callback route would fire `Schedule` with `value: undefined` → it counts as a conversion with no value → Meta has no reason to prefer the $1,344 hail truck over the $195 callback. **This must be fixed before launch.**

**Required config addition** (`/tools/configs/<shop>.json`):

```json
"pricing": {
  "callbackEstimate": { "low": 600, "high": 1200 }
}
```

**Implementation:** in the payload builder, when the route resolves to `callback`, set

```js
value = Math.round((cfg.pricing.callbackEstimate.low + cfg.pricing.callbackEstimate.high) / 2)
```

**Calibrating the number is a business decision, not a code decision.** Set it from the shop's own history — *average invoice of jobs that required an in-person quote*. Too low and Meta ignores the callback route; too high and Meta floods it with junk and you burn ops capacity. Start conservative and revisit at day 30 against real closed-job data. If the shop has no history, use the funnel's own arithmetic as the anchor: `large` with a crease is $840–$1,260 [VERIFIED: config bands].

---

## 6. Server layer (Conversions API)

**Endpoint:** `POST https://graph.facebook.com/{API_VERSION}/{PIXEL_ID}/events?access_token={TOKEN}`
Use the current Graph API version from the app dashboard at build time — do not hardcode a version you found in an old blog post.

### 6.1 Payload — `Schedule` (online booking)

```json
{
  "data": [{
    "event_name": "Schedule",
    "event_time": 1789000000,
    "event_id": "dentco-dallas.7f3a91c4-8b2e-4d1a-9c33-5e6f7a8b9c0d.Schedule.onsite",
    "event_source_url": "https://senalflow.com/en/demo/pdr-lead-funnel/?shop=dentco-dallas",
    "action_source": "website",
    "user_data": {
      "em": ["<sha256(lowercase(trim(email)))>"],
      "ph": ["<sha256(E.164 phone, digits only)>"],
      "fn": ["<sha256(lowercase(trim(first_name)))>"],
      "ln": ["<sha256(lowercase(trim(last_name)))>"],
      "zp": ["<sha256(zip5)>"],
      "country": ["<sha256('us')>"],
      "fbc": "fb.1.1788999800123.IwAR1234abcd...",
      "fbp": "fb.1.1788999800123.987654321",
      "client_ip_address": "203.0.113.42",
      "client_user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X)…"
    },
    "custom_data": {
      "value": 512,
      "currency": "USD",
      "content_name": "pdr_onsite_booking",
      "content_category": "medium",
      "schedule_type": "onsite_booking",
      "shop_id": "dentco-dallas",
      "lead_id": "7f3a91c4-8b2e-4d1a-9c33-5e6f7a8b9c0d"
    }
  }]
}
```

`em`/`ph`/`fn`/`ln`/`zp`/`country` are **SHA-256, lowercase, trimmed** before hashing. `country` is the 2-letter ISO code. Send `client_ip_address` and `client_user_agent` raw — they are not hashed. `fbc`/`fbp` are **never** hashed.

### 6.2 Payload — `Schedule` (tech callback)

Same shape, with:
```json
"event_id": "…​.Schedule.callback",
"content_name": "pdr_tech_callback",
"schedule_type": "tech_callback",
"value": 900
```
`value` = the configured `callbackEstimate` midpoint (§5).

### 6.3 Payload — `Lead`

Same shape, `event_name: "Lead"`, `event_id: "….Lead"`, `value` = quote midpoint (precise route only), `content_category` = `sizeTier`.

### 6.4 Event-match quality is the point

The funnel captures name, mobile, email, ZIP and vehicle at step 6. Send all of it, plus `fbp`, `fbc`, IP and UA. Target **event-match quality ≥ 8/10** in Events Manager (per-dataset score). A high EMQ score is what makes cheap delivery possible; most local advertisers send a cookie and nothing else.

**Privacy:** hashing is not a substitute for a lawful basis. The step-6 form must carry a visible consent line covering (a) the estimate text/follow-up and (b) sharing of contact data with advertising platforms for measurement. Add the data-sharing disclosure to the shop's privacy policy before the first dollar is spent.

---

## 7. Webhook contract (`leadWebhookUrl`)

Currently `null` [VERIFIED: config]. The existing payload builder emits `{shopId, timestamp, inputs, quote, contact}` [VERIFIED: quote engine source]. **It is not sufficient** for Option A. Extended contract:

```json
{
  "shop_id": "dentco-dallas",
  "lead_id": "7f3a91c4-8b2e-4d1a-9c33-5e6f7a8b9c0d",
  "timestamp": "2026-09-23T18:22:31.114Z",
  "route": "standard",
  "tier": "high",
  "schedule_type": "onsite_booking",
  "value": 512,
  "currency": "USD",
  "inputs": {
    "sizeTier": "medium", "dentCount": "2-3", "panel": "door",
    "hasCrease": false, "hasAluminum": false
  },
  "quote": { "routeToCallback": false, "low": 385, "high": 640, "breakdown": {} },
  "contact": {
    "name": "…", "phone": "+1…", "email": "…", "zip": "75201",
    "timing": "asap", "insurance": null
  },
  "appointment": { "date": "2026-09-25", "time": "1:00 PM" },
  "attribution": {
    "fbclid": "IwAR1234abcd…",
    "fbclid_ts": 1788999800123,
    "fbc": "fb.1.1788999800123.IwAR1234abcd…",
    "fbp": "fb.1.1788999800123.987654321",
    "client_ip": "203.0.113.42",
    "user_agent": "Mozilla/5.0 (iPhone; …)",
    "utm": { "source": "facebook", "medium": "paid", "campaign": "…", "content": "…" }
  }
}
```

**New fields vs today:** `lead_id`, `route`, `tier`, `schedule_type`, `value`, `appointment`, the entire `attribution` block. **`route` and `tier` come from the existing router function** (`pdrFunnel.js` already computes `"callback" | "high" | "standard"` [VERIFIED]) — they just aren't in the payload being sent. Wiring them through is trivial and gives ops the signal it needs for the callback SLA.

**Server-side behaviour on receipt:**
1. Persist the lead to CRM (idempotent on `lead_id`).
2. Fire the matching CAPI event (`Lead` / `Schedule.onsite` / `Schedule.callback`) with the shared `event_id`.
3. Send the SMS confirmation (`simulateTextDelivery` must be `false` in production — [VERIFIED: currently `true`]).
4. **Callback route only:** notify the shop immediately (SMS/Slack/push). This is the high-value lane; latency is revenue.
5. Return 200 fast; queue CAPI retries with the *same* `event_id`.

---

## 8. Calendar contract (hard gate)

The demo generates slots client-side: `daysAhead: 5`, four times/day, weekends skipped [VERIFIED: config]. There is no availability source and no booking persistence. **A `Schedule` event must describe a real appointment or you are training Meta on fiction.**

Required:

| Requirement | Why |
|---|---|
| Availability from a real source (Google Calendar / Calendly / CRM) | Slots shown must be genuinely open |
| **Hold/lock on slot selection** + re-check before confirm | Two buyers, one 1:00 PM slot = double-booking, which is worse than no booking |
| Persist the appointment (date, time, lead_id) | Required for offline loop (§9) and no-show analysis |
| Send the confirmation SMS for real | The funnel *promises* it ("you'll get a text confirmation") |
| Write-back webhook for attended / no-show / cancelled | This is the Phase-3 trigger |
| Callback SLA enforced (target ≤ 15 min, first attempt) | Under Option A your media performance now depends on it |

**Acceptance test:** book from the funnel, verify the slot disappears from the calendar, the CRM holds the appointment, the SMS arrives, and exactly **one** `Schedule` event appears in Events Manager (not two).

---

## 9. Offline conversion loop (Phase 3 — plan now, ship later)

Bookings are a proxy. Revenue is the target. Once the calendar writes back:

| Real-world outcome | Event | `action_source` | Value |
|---|---|---|---|
| Appointment **attended** | `Schedule` (offline) | `physical_store` | quote midpoint |
| Job **closed / invoiced** | `Purchase` (offline) | `physical_store` | **actual invoice amount** |
| No-show / cancelled | *(no event)* | — | — |

Match on `fbc` + hashed `em`/`ph` where available — this is why §2 exists. Upload via the dataset's Conversions API (preferred) using the **same `lead_id`-derived `event_id`** so the offline event supersedes rather than duplicates the online one.

**Timing:** Meta's guidance is to send offline events as close to real time as possible; do not batch at month-end. Treat any published maximum lookback window as something to confirm in current docs rather than assume [UNVERIFIED].

**This is the only step that turns "cost per booked appointment" into "cost per dollar collected."** Budget for it before launch; retrofitting attribution after 90 days of spend is not possible.

---

## 10. Assets to create in Events Manager

| Asset | Definition | Used for |
|---|---|---|
| Custom conversion: **High-value lead** | `Lead` where `content_category = large` OR `schedule_type = tech_callback` | Reporting the mix that actually pays |
| Custom conversion: **Online booking** | `Schedule` where `schedule_type = onsite_booking` | Honest client-facing booking count |
| Custom conversion: **Tech callback** | `Schedule` where `schedule_type = tech_callback` | Ops + client reporting separation |
| Audience: **Estimators (no contact)** | `EstimateView` in 30d, excluding `Lead` | Cheapest, warmest retargeting pool |
| Audience: **Step-3 droppers** | `FunnelStep` step=3 in 14d, excluding step 6 | Creative/friction iteration |
| Audience: **High-value engagers** | high-value lead + lookalike seed | Scaled value-chasing |
| **OutOfArea suppression list** | `OutOfArea` in 90d | Exclude from future spend |

---

## 11. Environment & config checklist

- [ ] `META_PIXEL_ID` — one dataset per shop (agency BM, client granted access) or the client's own pixel
- [ ] `META_CAPI_TOKEN` — system-user token, server-only, **never** in client-side code
- [ ] `META_DATASET_ID`
- [ ] Graph API version pinned and documented
- [ ] `leadWebhookUrl` set (currently `null`)
- [ ] `simulateTextDelivery: false` (currently `true`)
- [ ] `pricing.callbackEstimate` added (§5)
- [ ] `serviceArea.zipPrefixes` populated and reconciled with ad-account geo
- [ ] `routing.highValueSizeTiers` confirmed per shop
- [ ] `questions.insurance.enabled` — **explicit decision required**, changes routing tiers
- [ ] Domain verified in Business Manager
- [ ] Consent copy + privacy policy updated
- [ ] SMS consent language present at step 6 (the number is collected for a text confirmation — capture express consent for it)
- [ ] UTM convention live: `utm_source=facebook&utm_medium=paid&utm_campaign=<shop>_<phase>&utm_content=<creative_id>`

---

## 12. Test & acceptance plan

| # | Test | Pass condition |
|---|---|---|
| 1 | Pixel fires on load | `PageView` visible in Events Manager → Test Events |
| 2 | Full happy path (precise route) | `Lead` **then** `Schedule` (onsite) — one each |
| 3 | Callback path (10+ dents) | `Schedule` with `schedule_type: tech_callback`, **non-null value** |
| 4 | Out-of-area ZIP | `OutOfArea` fires, no `Lead`, no `Schedule` |
| 5 | Dedup | Each event appears **exactly once** in Events Manager; browser + server share `event_id` |
| 6 | `fbc` correctness | `fbc` contains the *landing* timestamp + the URL's `fbclid` |
| 7 | Event match quality | Dataset EMQ ≥ 8/10 |
| 8 | Calendar integrity | Booked slot disappears; CRM record holds appointment; exactly one SMS |
| 9 | Idempotency | Replay the webhook → no duplicate lead, no duplicate conversion |
| 10 | GA4 reconciliation | GA4 conversions within ~±20% of Events Manager (never expect exact parity) |
| 11 | Value sanity | `value` on every `Schedule`; callback values match configured estimate |

**Do not launch ads until 1–11 pass.** Every one of these is cheaper to fix now than after $2,000 of learning-phase spend trained on bad signal.

---

## 13. Open decisions (blocking or near-term)

| # | Decision | Blocks |
|---|---|---|
| 1 | Which system holds real availability? (Google Calendar / Calendly / CRM) | §8 — and therefore the campaign |
| 2 | Pixel/dataset ownership: agency BM vs client ad account | §11 |
| 3 | `callbackEstimate` value + written callback SLA | §5 — Option A is unusable without it |
| 4 | Insurance question on/off | Lead funding mix, routing tiers |
| 5 | Pilot budget ceiling | Phase-1 optimization event (§4.3 of the playbook) |
| 6 | Consumer vs dealership/B2B first | Creative, offer, geo |
| 7 | EN/ES bilingual creative from day one? | Creative volume; DFW has Spanish-dense ZIPs |
| 8 | Who owns the offline loop operationally (who marks attended/closed)? | §9 |
