# Data-Driven Brainstorm — screener design (decisions through Q3)

Replace the memory-based brainstorm (model recalls "underserved niches" from training data) with a
CBP-driven screener: the full NAICS universe is the search space; data drives candidates + TAM math;
judgment drives the qualitative criteria (cash+, urgency, ad proof, textability — no Census field
measures these). Pending decisions (Q4–Q7) marked at the end.

## Pipeline
1. **SCREEN** (`scripts/niche_screener.py` — built & tested 2026-08; ~39 candidates live):
   curated sectors × window bands → 25–40 candidates with exact counts + labels + structure
   signals + NES flags + DFW/hail-alley CBSA columns
2. **INTERPRET (LLM)**: NAICS label → human niche framing; flag CLEAN vs SLICE; name niches inside
   residual buckets
3. **SCORE (LLM)**: qualitative criteria (cash+, urgency, ad proof, textability) + underserved via
   the calibrated agency probe (`references/agency-density-calibration.md`)
4. **OUTPUT**: ranked scorecard with VERIFIED TAM column + band flags + top 8–10 + ranked
   appendix + proof checklists

## Confirmed decisions

### Q1 — Curated sectors (hunting ground, not certification)
- Defaults: **238x** specialty trades · **562x** waste/remediation · **5413x** testing labs ·
  **54162x** environmental consulting · **5617x** building services (restoration, pest) ·
  **811x** repair & maintenance (auto body = PDR home) · **621x** health practitioners (TRT-style
  clinics live in 621399) · **3323x** architectural/structural metals (storm shelters)
- Per-run configurable sector list + `--all` wildcard mode (stricter filters) for looking outside
- **Sector ≠ underserved**: HVAC/plumbing are IN 238x yet saturated — each candidate is cleared by
  the 4-layer verification (agency-density-calibration.md), and can be rejected regardless of sector.

### Q2 — Window thresholds
- **Floor = 5,000 employer establishments** (data-driven: an 8k floor would exclude 11 curated
  codes including foundation repair's home 238190 = 6,277 — our #1 candidate; sub-5k is watchlist-only,
  e.g. septic 562991 = 3,996 already dropped on verified TAM)
- **Bands (flag, not hard cut)**:
  - 🟢 12,500+ → GREEN-potential (employer-only can reach GREEN at high textability)
  - 🟡 8,000–12,500 → hinge (NES/directory lift decides)
  - 🟠 5,000–8,000 → lift-dependent (needs published NES, burst-demand case, or MULTI-code slice
    logic — e.g. foundation = 238190+238110+238990 sums to ~29k)
  - <5,000 → watchlist only (burst-model niches like PDR)
- **Owner-operated filter**: size-class share (≥80% of establishments <20 employees) preferred over
  mean EMP/EST ≤ 12 (mean is distorted by a few large firms); show mean as a display column
- **Cap = 60,000, SOFT** (flag-and-include above; above ~60k = residual catch-all or saturated-huge)
- **PAY/EMP = sort key, not filter** (premium-service proxy)

### Q3 — Residual buckets ("All Other…" codes: 238990, 561790, 811198, 621999…)
- **Include as SLICE codes** (they're where invisible niches hide: restoration lives in 561790,
  foundation repair partly in 238990, PDR possibly in 811198)
- Auto-flag by label heuristic ("All Other"/"Other"/"Miscellaneous"/"Not Elsewhere Classified")
- Ceiling semantics: count is a ceiling, never the TAM; tier shown as "ceiling-tier"
- Mandatory niche naming: LLM must name 1–3 specific niches inside + directory count in proof checklist

## Demo evidence (2026-08)
- **Raw full-universe screen fails**: sorted by PAY/EMP it surfaces portfolio management (523920),
  CPAs (541211), film studios (512110) — the opposite of underserved. Pure numerics can't find
  invisible niches; sector curation is required.
- **Curated screen works**: 27 candidates in one API call; cross-validates manual picks
  (238340 tile ✓ 10,710 · 561710 pest ✓ 16,080 · 811121 PDR home ✓ 34,665 · 561790 restoration ✓
  17,574) and surfaces new ones (238910 site prep 39,686 · 238350 finish carpentry 32,169 @5.2 emp/est)
- Side-finding: 541380 testing labs (7,488) fails the owner-operated filter (20.7 emp/est — labs
  have technician staffs) — by design, but confirm before relying on it.

## Confirmed decisions (Q4–Q7)
- **Q4 ranking**: NO hard-coded weights — the screener outputs sortable evidence columns; the LLM
  applies the six qualitative criteria and ranks (weights change per run — burst vs steady-state).
  **Diversity = soft quota**: top 3 per sector guaranteed + up to 2 LLM-judged wildcards.
- **Q5 NES flag**: per-candidate column ✓ published / ✗ unpublished / ? unknown — never assume.
- **Q6 CBSA columns**: DFW (19100) + Hail10 sum (9 hail-alley metros) from the official MSA bulk
  file; per-metro detail in `--json`.
- **Q7 output size**: top 8–10 full scorecards + one-row ranked appendix of the rest (TAM is
  verified at generation, so a bigger shortlist is safe).

## Output columns (target)
NAICS | Label | ESTAB | size-class share (or EMP/EST) | PAY/EMP | band flag | tier (employer-only) |
NES-availability + tier-if-NES-published | residual tag | underserved probe score | DFW | Hail10
