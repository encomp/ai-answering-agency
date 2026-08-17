# NAICS Mapping — Candidate Niches → Census Codes

Method: CBP+NES TAM lookup via `scripts/cbp_lookup.py` (see script header for data model
and bulk-file quirks). Map each niche to the NARROWEST 6-digit NAICS code.

| Status | Meaning |
|---|---|
| **CLEAN** | Niche ≈ the full 6-digit code — CBP+NES is an exact TAM |
| **SLICE** | Niche ⊂ code — code total is a CEILING; directory counts (Google Maps) are the FLOOR; report both |
| **MULTI** | Sum of codes — only where overlap is minimal; flag overlap risk |

## Candidate niches (from brainstorm + deep dives)

| Niche | NAICS | Status | Notes |
|---|---|---|---|
| Tile & stone installation | 238340 | **CLEAN** ✓ | Verified: 10,710 employer (US 2022); 144 in DFW CBSA |
| Septic tank service | 562991 | **CLEAN** | Septic Tank and Related Services — verify at runtime |
| Termite / WDI pest control | 561710 | **CLEAN** | Exterminating & Pest Control — inspections + treatment in one code |
| Environmental testing (asbestos/AQ) | 541380 | **CLEAN** | Testing Laboratories and Services |
| Paintless dent repair (PDR) | 811121 | **SLICE** | Auto Body, Paint & Interior Repair = 34,665 employer (ceiling); PDR is a small slice — directory count is the floor |
| Foundation repair | 238190 | **SLICE** | Other Foundation/Structure/Exterior — 6,277 employer ceiling; 238110 (poured concrete) is mostly new-build, exclude |
| Basement waterproofing | 238190 / 238990 | **SLICE** | Split across codes; use 238190 ceiling + directory floor |
| Crawlspace encapsulation | 238990 | **SLICE** | All Other Specialty Trades = 40,302 — huge, slice factor matters |
| Mold remediation | 561790 | **SLICE** | Other Services to Buildings & Dwellings (restoration) — also partially 562910 |
| Water damage restoration | 561790 | **SLICE** | Same restoration code; IBISWorld 6278 maps here |
| Kitchen hood cleaning | 561790 | **SLICE** | Same code — restaurant-adjacent services |
| Fire safety inspection | 541350 | **SLICE** | Building Inspection Services (commercial compliance) |
| Specialty waste | 562211/562219 | **SLICE** | Hazardous vs other waste — split |
| Storm shelters / safe rooms | 332311 | **SLICE** | Prefabricated metal buildings — weak fit |
| Asphalt / parking lot maint. | 237310 | **SLICE** | Highway/street construction — includes paving |
| Men's health / TRT clinics | 621111/621112 | **SLICE** | Physicians' offices — poor fit; use directory counts instead |
| Mobile home repair | 236118 | **SLICE** | Residential remodelers — weak fit |

## Rules

1. **Prefer the narrowest code that fits.** CLEAN → exact. SLICE → ceiling + directory floor.
2. **Never proxy 4-digit for 6-digit NES** — NES 6-digit publication is INDUSTRY-DEPENDENT: many
   trade codes (2383xx tile, 562991 septic, 561710 pest, 81112x auto body) are unpublished at
   6-digit (aggregated to 4-digit for disclosure); others publish fully (e.g., 812113 = 280,875).
   When 6-digit NES is unpublished: TAM = employer-only (a FLOOR) + flag it; use directory counts
   (Google Maps) as the nonemployer proxy. Never mix the 4-digit parent into a 6-digit TAM.
3. **TAM = CBP + NES** — disjoint populations (employer vs no-employees), additive. Report the split.
4. **Pin year + NAICS vintage** (2022). The 2027 NAICS revision will shift codes — re-verify mappings then.
5. **Suppressed cells** ('N','D','G','H','J') → state-level fallback with provenance flag; never silent zero.
6. **CBSA, not hand-picked counties** — the script embeds official OMB county lists per metro.
7. **Tiers unchanged** (8k/12.5k/25k): they were calibrated on directory-style populations
   (employer + nonemployer); CBP+NES restores that population.
