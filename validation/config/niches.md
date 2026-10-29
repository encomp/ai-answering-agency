# Validation Pipeline — STRONG Candidates

Run: `niche-research` skill, validation mode. Target niches: fence construction, commercial machinery repair, commercial kitchen equipment repair.
Frame: execute 3-step validation for each niche; output a scored validation brief per niche.
Tags: [VERIFIED] live source · [ESTIMATE] reasoning · [UNVERIFIED] pending execution.

---

## Niche A: Fence Construction & Installation

### Step 1 — Google Maps Directory Count (Skyline / Apify)
**Goal:** count scrape-able fence contractors in launch metros.
**Queries:**
- `fence installation near me`
- `fence contractor near me`
- `privacy fence installation`
- `commercial fence installation`

**Launch metros (priority order):**
1. Dallas, TX
2. Fort Worth, TX
3. Houston, TX
4. Chicago, IL
5. Phoenix, AZ
6. Denver, CO

**Deliverable:** total contractor count per metro; deduplicated business names + phone numbers; CSV exported to `/Users/edgarrico/ai-answering-agency/data/fence-contractors-<metro>.csv`.

**Success criteria:** ≥500 contractors across top 3 metros = TAM validated.

---

### Step 2 — Veriphone Textability Sample
**Goal:** determine % mobile phone numbers among fence contractors.
**Sample size:** 150 leads (DFW first, then HOU/CHI).
**Input:** CSV from Step 1.
**Test:** Veriphone line-type lookup → count mobile vs. landline vs. VoIP.
**Deliverable:** textability % per metro; overall mobile share.

**Success criteria:** ≥50% mobile = SMS viable.

---

### Step 3 — Meta Ads Library Probe
**Goal:** assess ad competition and campaign freshness.
**Search terms:**
- `fence installation`
- `privacy fence`
- `fence contractor`
- `commercial fence`

**Collect:** advertiser names, ad count, first-seen/last-seen dates, landing page domains.
**Deliverable:** Ads competitor list + run-date histogram.

**Success criteria:** ≤3 dedicated fence agencies advertising in Meta = under-digitized confirmed.

---

## Niche B: Commercial & Industrial Machinery Repair

### Step 1 — Google Maps Directory Count (Skyline / Apify)
**Goal:** count scrape-able machinery repair shops in launch metros.
**Queries:**
- `commercial machinery repair near me`
- `industrial equipment repair`
- `factory equipment repair`
- `manufacturing equipment maintenance`

**Launch metros (priority order):**
1. Chicago, IL
2. Dallas, TX
3. Fort Worth, TX
4. Houston, TX
5. Minneapolis, MN
6. Phoenix, AZ

**Deliverable:** total contractor count per metro; deduplicated CSV to `/Users/edgarrico/ai-answering-agency/data/machinery-repair-<metro>.csv`.

**Success criteria:** ≥300 contractors across top 3 metros = TAM validated.

---

### Step 2 — Veriphone Textability Sample
**Goal:** determine % mobile phone numbers among machinery repair shops.
**Sample size:** 150 leads (Chicago first, then DFW/HOU).
**Input:** CSV from Step 1.
**Deliverable:** textability % per metro; overall mobile share.

**Success criteria:** ≥50% mobile = SMS viable.

---

### Step 3 — Meta Ads Library Probe
**Goal:** assess ad competition.
**Search terms:**
- `commercial machinery repair`
- `industrial equipment repair`
- `factory maintenance contractor`
- `manufacturing equipment repair`

**Deliverable:** advertiser list + run-date histogram.

**Success criteria:** ≤2 dedicated machinery repair agencies in Meta = underserved confirmed.

---

## Niche C: Commercial Kitchen Equipment Repair & Maintenance

### Step 1 — Google Maps Directory Count (Skyline / Apify)
**Goal:** count scrape-able kitchen equipment repair contractors in launch metros.
**Queries:**
- `commercial kitchen equipment repair near me`
- `restaurant equipment repair`
- `commercial fryer repair`
- `commercial refrigeration repair`

**Launch metros (priority order):**
1. Dallas, TX
2. Fort Worth, TX
3. Houston, TX
4. Chicago, IL
5. Los Angeles, CA
6. Atlanta, GA

**Deliverable:** total contractor count per metro; deduplicated CSV to `/Users/edgarrico/ai-answering-agency/data/kitchen-equip-repair-<metro>.csv`.

**Success criteria:** ≥200 contractors across top 3 metros = TAM validated.

---

### Step 2 — Veriphone Textability Sample
**Goal:** determine % mobile phone numbers among kitchen equipment repair contractors.
**Sample size:** 150 leads (DFW first, then HOU/CHI).
**Input:** CSV from Step 1.
**Deliverable:** textability % per metro; overall mobile share.

**Success criteria:** ≥60% mobile = SMS viable (B2B field-first crews tend to be mobile-heavy).

---

### Step 3 — Meta Ads Library Probe
**Goal:** assess ad competition.
**Search terms:**
- `commercial kitchen equipment repair`
- `restaurant equipment repair`
- `commercial fryer repair`
- `commercial refrigeration repair`

**Deliverable:** advertiser list + run-date histogram.

**Success criteria:** zero dedicated kitchen equipment repair agencies in Meta = blue ocean confirmed.

---

## Niche D: Commercial Window Cleaning

### Step 1 — Google Maps Directory Count (Apify)
**Goal:** count scrape-able commercial window cleaning companies in launch metros.
**Queries:**
- `commercial window cleaning`
- `window cleaning service`
- `high rise window cleaning`
- `storefront window cleaning`

**Launch metros (priority order):**
1. Dallas, TX
2. Houston, TX
3. Chicago, IL
4. Phoenix, AZ
5. Denver, CO

**Deliverable:** total company count per metro; deduplicated CSV under `data/validation/window-cleaning/`.

**Success criteria:** ≥200 companies across top 3 metros = TAM validated.

---

### Step 2 — Veriphone Textability Sample
**Goal:** determine % mobile phone numbers among window cleaners.
**Sample size:** 150 leads (round-robin across metros).
**Deliverable:** textability % overall.

**Success criteria:** ≥50% mobile = SMS viable.

---

### Step 3 — Meta Ads Library Probe
**Goal:** assess ad competition.
**Search terms:**
- `commercial window cleaning`
- `window cleaning service`
- `high rise window cleaning`
- `storefront window cleaning`

**Deliverable:** advertiser list + run-date histogram.

**Success criteria:** ≤3 dedicated window-cleaning agencies in Meta = under-digitized confirmed.

---

## Scoring Matrix

| Criterion | Weight | Fence | Machinery Repair | Kitchen Equip Repair |
|---|---|---|---|---|
| Google Maps count (≥threshold) | 30% | [ ] | [ ] | [ ] |
| Veriphone mobile % (≥threshold) | 25% | [ ] | [ ] | [ ] |
| Meta Ads agency density (≤threshold) | 25% | [ ] | [ ] | [ ] |
| Deep-dive verdict alignment | 20% | STRONG | STRONG | STRONG |
| **Validation score** | **100%** | **TBD** | **TBD** | **TBD** |

**Pass threshold:** ≥70% weighted score → proceed to pilot. <70% → revisit positioning or deprioritize.

---

## Execution Notes
- Run Steps 1–3 for each niche sequentially; do not batch across niches (different search queries, different metro sets).
- Store all CSVs and probe results under `/Users/edgarrico/ai-answering-agency/data/validation/`.
- After each niche validation, commit results to git and push to remote.
- If a niche fails any step with a wide margin, flag for strategic review rather than automatic deprioritization.
