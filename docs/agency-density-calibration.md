# Agency-Density Calibration — the "underserved" probe

Layer 2 of the underserved verification stack (Layer 0 = CBP fragmentation in the screener,
Layer 1 = LLM saturation flag, Layer 3 = Meta Ads Library run dates in deep research).

## The probe

For a candidate niche, run web searches:
- `"[niche] marketing agency"`
- `"[niche] marketing"` / `"[niche] leads"` (secondary)

Then measure: (a) count of DISTINCT dedicated agencies (sites whose business IS marketing
for that niche), (b) presence of aggregation/listicle content ("12 Best X Marketing
Companies", "Top X Agencies"). Generalist agencies do NOT count.

## Calibration anchors (measured 2026-08 via Firecrawl search)

| Niche | Dedicated agencies | Listicles | Density |
|---|---|---|---|
| HVAC | Many (Scorpion + listicles) | "12 Best", "Best Digital Marketing Agencies" | 🔴 SATURATED |
| Roofing | Many ("#1 Roofing Marketing Agency"…) | "7 to Watch", "12 Best" | 🔴 SATURATED |
| Plumbing | Many (Thrive, Plumber Marketing USA…) | "12 Best" | 🔴 SATURATED |
| Tile & stone | 2–4 (Tile Installers Marketing…) | none | 🟡 THIN |
| Septic | 2–3 (Septic Marketing Agency…) | none | 🟡 THIN |
| Paintless dent repair | ~4 (Pushin PDR, Dent Group, PDR Marketing…) | none | 🟢 SPARSE |
| Finish carpentry | ~1 + generalist advice | none | 🟢 SPARSE |
| Site prep / excavation | 2–3 | none | 🟢 SPARSE |

## Scoring (underserved criterion, 1–5 where 5 = most underserved)

| Probe result | Underserved score |
|---|---|
| 10+ dedicated agencies AND listicles | 1 (saturated — reject) |
| 5–10 dedicated agencies | 2 |
| 2–5 dedicated agencies, no listicles | 3–4 (winnable: mediocre players, bad funnels) |
| 0–1 dedicated agencies | 5 (sparse — stand out instantly) |

Calibrate every new probe against the anchors: HVAC/roofing/plumbing = the "high" reference,
PDR/finish carpentry = the "low" reference. A niche scoring 1–2 here fails the
UNDERSERVED criterion regardless of how well it passes the CBP window.

## Notes

- "Underserved" is a spectrum: 2–5 mediocre agencies + bad funnels is still winnable
  (the docs' own logic — they're making money despite bad execution).
- Listicle presence is a strong saturation signal (content-marketing war = many competitors).
- The probe result is [VERIFIED] for the search moment; ad-run-date evidence (Ads Library)
  is the definitive Layer-3 check and stays in deep research.
