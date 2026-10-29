# Validation Brief — Commercial Window Cleaning

Run: `niche-research` validation mode. Niche: commercial window cleaning. Status: VALIDATION COMPLETE.
Tags: [VERIFIED] live source · [ESTIMATE] reasoning · [UNVERIFIED] pending.

---

## Step 1 — Google Maps Directory Count [VERIFIED]

**Actor:** `compass/crawler-google-places` · **Queries:** `commercial window cleaning`, `window cleaning service`, `high rise window cleaning`, `storefront window cleaning`

**Unique companies per metro (deduped by placeId):**

| Metro | Unique companies |
|---|---|
| Houston, TX | 471 |
| Chicago, IL | 419 |
| Phoenix, AZ | 411 |
| Dallas, TX | 406 |
| Denver, CO | 351 |

**Totals:** 3,052 raw rows → **2,058 unique companies** across 5 metros (placeId-deduped).

**Verdict:** ✅ TAM validated. Success criteria was ≥200 across top 3 metros — we have **1,301** across the top 3 (Houston 471 + Chicago 419 + Phoenix 411). Density is strong and evenly distributed.

*Note: 18 of 20 combos hit the 200-place cap → these counts are a FLOOR; true density is higher. `high rise window cleaning` returned fewer (16–29) — it's a genuine sub-slice, not a data gap.*

---

## Step 2 — Veriphone Textability Sample [VERIFIED]

**Sample:** 150 leads (round-robin across 20 files) · **Endpoint:** `v2/verify`

| Line type | Count |
|---|---|
| Mobile | 65 |
| VoIP | 50 |
| Landline | 33 |
| Invalid | 2 |

**Textable % (mobile + VoIP):** **76.7%**

**Verdict:** ✅ SMS viable. Success criteria was ≥50%. Mobile alone is 43.3%; mobile+VoIP is 76.7%. Owner-operator route cleaners are mobile-first, as predicted — though the higher landline count (33 vs fence's 25) reflects a larger share of office-based commercial outfits.

---

## Step 3 — Meta Ads Library Probe [VERIFIED]

**Actor:** `automation-lab/facebook-ads-library` · **Queries:** 4 window-cleaning terms · **maxAds=100/query**

**Raw:** 371 ads, 163 unique advertisers — but keyword search pulled heavy noise (Cesar Millan, novel apps, health clinics). Filtering to window-cleaning-relevant advertisers:

**Genuine window-cleaning advertisers identified (~50+, with these standing out):**
- **Franchise systems running ads:** Fish Window Cleaning, Pink's Windows (multiple franchisee pages), Squeegee Squad (multiple franchisee pages)
- **Independent operators (1–6 ads each):** Duchesney Window Washing (6), Brickell Window Cleaners (4), Patterson Window Cleaning (3), Bright View, Blue Gander, Hartmann, Elite, AMA, 20/20 Window Cleaning, plus ~40 more single-ad independents

**Verdict:** ⚠️ REVISED. This is **NOT** a blue-ocean under-digitized niche. The franchise chains (Fish, Pink's, Squeegee Squad) are already advertising actively with national/franchisee ad presence. The independent operators are largely **self-serve** — but there's meaningful ad activity.

**Interpretation:** demand is real and competitive at the top (franchises), but the **independent owner-operator layer** (the SMS-reachable segment) is still mostly self-serve. No dedicated *window-cleaning marketing agency* emerged as a dominant Meta advertiser — the agencies found earlier (Fannit, Window Pros Digital, SERPWARS) are SEO/PPC shops, not running the advertisers' Meta campaigns visibly.

---

## Scoring

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Google Maps count (≥200 top 3) | 30% | ✅ 100% | 1,301 across top 3 |
| Veriphone mobile % (≥50%) | 25% | ✅ 100% | 76.7% textable |
| Meta Ads agency density | 25% | ⚠️ 60% | franchises active; no dedicated agency dominant |
| Deep-dive verdict alignment | 20% | 🟡 75% | VALIDATE FURTHER — margin strong, recurring, but not empty lane |
| **Weighted** | **100%** | **~85%** | **PASS (lower confidence)** |

---

## Verdict: PASS — but positioned as "independent operator" play, not blue ocean

**Commercial window cleaning clears the bar at ~85%**, but with a materially different competitive picture than fence:

1. **✅ TAM validated** — 2,058 unique companies (floor), evenly distributed
2. **✅ Textable** — 76.7%, strong
3. **⚠️ Franchise competition is real** — Fish/Pink's/Squeegee Squad run active Meta ads; the "empty lane" claim doesn't hold at the franchise tier

**The actual wedge:** the SMS-reachable segment is the **independent owner-operator** (1–5 trucks, mobile-first), and *they* are still largely self-serve — the franchises advertise, but the independent layer they compete with doesn't. A pitch targeting independent commercial route operators (AI answering + instant commercial quotes, "never miss a property-manager call while you're on a ladder") is viable, but it's a *positioning* play against franchise incumbents, not an empty market.

**Reach universe math:** 2,058 unique (floor) × ~77% textable ≈ **~1,580 textable** across 5 metros — GREEN tier, sustainable outbound.

**Proof gaps remaining:**
- [UNVERIFIED] True count (18/20 combos hit the 200 cap — real density is higher)
- [UNVERIFIED] Whether the franchise ad activity is centralized (national) vs franchisee-local — affects how hard the independent layer is to win
- [UNVERIFIED] `high rise window cleaning` is a genuinely small slice (16–29/query) — if that's the premium segment, TAM narrows

**Next 3 actions:**
1. Raise GMaps cap to 500 and re-run top metro to measure true density
2. Deep-dive the franchise vs independent split (Fish/Pink's/Squeegee ad spend + franchisee density)
3. If independent-operator positioning holds, this is a GREEN recurring-revenue niche worth a pilot
