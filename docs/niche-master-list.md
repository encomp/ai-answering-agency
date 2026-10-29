# Niche Master List — All Reviewed (with & without validation)

Last updated: 2026-10-29. Repo: `encomp/ai-answering-agency`.

Legend: ✅ VALIDATED (3-step pipeline complete) · 🟢 STRONG (deep-dive done, awaiting validation) · 🟡 VALIDATE FURTHER · 🟠 MODERATE · ❌ SKIP (rejected) · 💡 BRAINSTORM-ONLY (screened, no deep dive).

---

## ✅ VALIDATED — pipeline complete

| Niche | Verdict | Result |
|---|---|---|
| **Fence construction** | STRONG → **PASS ~93%** | 1,884 contractors (5 metros), 80.7% textable, 249 advertisers / 0 agencies |

---

## 🟢 STRONG — deep dive done, awaiting validation

| Niche | Signal | Next |
|---|---|---|
| **Commercial/industrial machinery repair** | 22,433 employers, $60.3B mkt, 5 OEM-focused agencies, underserved 5/5 | Validation run |
| **Commercial kitchen equipment repair** | 5k–15k contractors, $1.6B → $2.3B by 2030 (7.5% CAGR), zero agencies | Validation run |

---

## 🟡 VALIDATE FURTHER — deep dive done, weaker or unverified on some axis

| Niche | Note |
|---|---|
| Radon mitigation | Emerging (8.1% CAGR); tickets $800–2.5k res / $2k–8k comm |
| Septic | 12k–20k contractors, $4.64B repair mkt, 8+ agencies, ~$2,900 weighted |
| Fire sprinkler | — |
| Elevator repair | — |
| Foundation repair | Prior #1, deep-dive pending re-check |
| Paintless dent repair (PDR) | Burst-demand, seasonal; empty agency lane |
| Gutter replacement | $1.0B service mkt, 5–6 agencies |
| Hardwood flooring | Thin agencies but declining market |
| House painters | Biggest TAM, but 100+ agencies fight over it |

---

## 🟠 MODERATE

| Niche | Note |
|---|---|
| Home security installation | 19,845 contractors, $22.1B mkt, thin agencies, DIY headwind |

---

## ❌ SKIP — rejected

| Niche | Reason |
|---|---|
| Mold/water restoration | Saturated — 21+ dedicated agencies |
| Garage door | Residential ticket below $2,500 floor |
| Deck/patio | Narrow TAM, declining (972 businesses) |
| Driveway/paver | Unclear TAM + agency ownership |
| HVAC | Saturated |
| Roofing | Saturated |
| Windows/siding | Saturated |
| Concrete contractor | Saturated (listicle + 5 agencies) |
| Car wash | Saturated |
| Appliance repair | Saturated (pay-per-call racket) |
| Locksmith | Saturated (lead-gen racket) |
| Mental health practice | Saturated |

---

## 💡 BRAINSTORM-ONLY — screened, no deep dive

| Niche | Signal | Band |
|---|---|---|
| Finish carpentry | Thin dedicated field (1 DFW firm) | 🟢 GREEN+ |
| Auto glass | Storm twin of PDR; "leads too expensive" pain | 🟠 ORANGE |
| Building inspection (home inspectors) | ~80% margins volume model | 🟠 ORANGE |
| Masonry | Small agency field | 🟢 GREEN |
| Siding | Big tickets, storm angle | 🟡 YELLOW |
| Environmental consulting | Regulation-driven B2B | 🟡 YELLOW |
| Psychiatrists | 13,017 + NES, no-show pain | — |

---

## Also reviewed (quick-takes, not advanced)

Commercial painting · pool construction/repair · tree removal/arborist · solar panel cleaning · chimney sweep/masonry · asbestos abatement · epoxy garage floor · basement waterproofing · granite/quartz countertop · bathroom remodeling · tile installation · deck/patio (again, skip).

---

## Validation pipeline (3 steps, Apify + Veriphone)

1. **Google Maps count** — `compass/crawler-google-places`
2. **Veriphone textability** — `/v2/verify` (≥50% mobile = SMS viable)
3. **Meta Ads probe** — `automation-lab/facebook-ads-library` (≤2–3 agencies = underserved)

**Success thresholds per niche** (from `validation/config/niches.md`):
- Fence: ≥500 contractors / ≥50% mobile / ≤3 agencies
- Machinery: ≥300 contractors / ≥50% mobile / ≤2 agencies
- Kitchen equip: ≥200 contractors / ≥60% mobile / 0 agencies
