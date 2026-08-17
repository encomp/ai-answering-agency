#!/usr/bin/env python3
"""
Niche screener: data-driven brainstorm candidate pool from Census CBP (+NES flags, CBSA columns).

Usage:
  python3 scripts/niche_screener.py                     # curated sectors, defaults
  python3 scripts/niche_screener.py --sectors 238,562   # custom sector prefixes
  python3 scripts/niche_screener.py --all               # wildcard: scan every sector
  python3 scripts/niche_screener.py --include-small     # show sub-5k watchlist too
  python3 scripts/niche_screener.py --skip-nes          # skip NES availability probes
  python3 scripts/niche_screener.py --json

Design decisions (aligned with the operator, 2026-08):
  - Curated "underserved-prone" sectors by default (per-run configurable; --all wildcard).
  - Window 5k-60k employer establishments with BAND FLAGS, not hard cuts:
        <5k      WATCH   burst-model only (shown with --include-small)
        5-8k     ORANGE  lift-dependent (needs published NES, burst case, or slice/MULTI logic)
        8-12.5k  YELLOW  hinge — NES/directory lift decides
        12.5-25k GREEN   GREEN-potential on employer math
        25-60k   GREEN+  strong; watch saturation
        60k+     PURPLE  broad/saturated-risk (soft cap: flagged, not dropped)
  - Owner-operated: size-class share of establishments with <20 employees >= 0.80
    (falls back to EMP/EST <= 12 when size classes are suppressed).
  - Residual buckets ("All Other"/"Other"/"Miscellaneous"/NEC labels) are tagged —
    their ESTAB is a CEILING for any niche inside, never a TAM (SLICE semantics).
  - NES availability probe per candidate (6-digit published vs aggregated) — 1 API call each.
  - CBSA columns: DFW + hail-alley metro sum from the official MSA bulk file.
  - NO hard-coded ranking weights: this script outputs sortable evidence columns;
    the LLM applies the six qualitative criteria and ranks.
"""
import argparse, csv, io, json, os, re, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cbp_lookup import _bulk_text, env_key, _get  # reuse cache + helpers

CURATED = ("238", "562", "5413", "54162", "5617", "811", "621", "3323")
HAIL_METROS = {"19740": "Denver", "36540": "Omaha", "33460": "Minneapolis", "16980": "Chicago",
               "36420": "Oklahoma City", "48620": "Wichita", "28140": "Kansas City",
               "41180": "St. Louis", "26420": "Houston"}
RESIDUAL_RE = re.compile(r"all other|^other |miscellaneous|not elsewhere classified|\bnec\b", re.I)

def labels_from_api():
    """Fetch NAICS2017 + label for all codes in one API call (needs CENSUS_API_KEY)."""
    key = env_key()
    if not key:
        return {}
    url = f"https://api.census.gov/data/2022/cbp?get=NAICS2017,NAICS2017_LABEL&for=us:1&key={key}"
    try:
        data = json.loads(_get(url))
        return {r[0]: r[1] for r in data[1:] if len(r) >= 2}
    except Exception:
        return {}

def parse_state_file():
    """Aggregate 6-digit codes from the cached CBP state file (lfo='-' rows)."""
    text = _bulk_text("cbp_st")
    agg = {}
    for r in csv.DictReader(io.StringIO(text)):
        if (r.get("lfo") or "").strip() != "-":
            continue
        n = (r.get("naics") or "").strip().replace("/", "")
        if len(n) != 6 or not n.isdigit():
            continue
        def gv(k):
            try:
                return int(r.get(k) or 0)
            except (ValueError, TypeError):
                return None
        d = agg.setdefault(n, {"est": 0, "emp": 0, "lt20": 0, "size_sup": False})
        for k in ("est", "emp"):
            v = gv(k)
            if v is not None:
                d[k] += v
        # size classes: <5, 5-9, 10-19
        lt = 0
        for k in ("n<5", "n5_9", "n10_19"):
            v = gv(k)
            if v is None:
                d["size_sup"] = True
            else:
                lt += v
        d["lt20"] += lt
    return agg

def parse_msa_cbsa():
    """code -> {cbsa: estab} for the metro set, from the official MSA bulk file."""
    text = _bulk_text("cbp_msa")
    out = {}
    for r in csv.DictReader(io.StringIO(text)):
        n = (r.get("naics") or "").strip().replace("/", "")
        if len(n) != 6 or not n.isdigit():
            continue
        msa = (r.get("msa") or "").strip()
        if msa not in HAIL_METROS and msa != "19100":
            continue
        try:
            v = int(r.get("est") or 0)
        except (ValueError, TypeError):
            v = None
        out.setdefault(n, {})[msa] = v
    return out

def band(est):
    if est < 5000: return "WATCH"
    if est < 8000: return "ORANGE"
    if est < 12500: return "YELLOW"
    if est < 25000: return "GREEN"
    if est < 60000: return "GREEN+"
    return "PURPLE"

def main():
    ap = argparse.ArgumentParser(description="CBP-based niche candidate screener.")
    ap.add_argument("--sectors", default=None, help="comma-separated NAICS prefixes, e.g. 238,562")
    ap.add_argument("--all", action="store_true", help="scan every sector (wildcard)")
    ap.add_argument("--min-estab", type=int, default=5000)
    ap.add_argument("--max-estab", type=int, default=60000)
    ap.add_argument("--lt20-share", type=float, default=0.80, help="owner-operated threshold")
    ap.add_argument("--include-small", action="store_true", help="also show sub-5k watchlist")
    ap.add_argument("--skip-nes", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    sectors = tuple(args.sectors.split(",")) if args.sectors else (None if args.all else CURATED)
    agg = parse_state_file()
    labels = labels_from_api()
    cbsa = parse_msa_cbsa()
    nes_probe = not args.skip_nes

    rows = []
    for n, d in agg.items():
        est, emp = d["est"], d["emp"]
        if est == 0:
            continue
        if sectors and not n.startswith(sectors):
            continue
        # owner-operated: size-class share, fallback EMP/EST
        share = d["lt20"] / est if est and not d["size_sup"] else None
        emp_est = emp / est if est else 99
        if share is not None:
            if share < args.lt20_share:
                continue
        elif emp_est > 12:
            continue
        b = band(est)
        if b == "WATCH" and not args.include_small:
            continue
        if est > args.max_estab:
            continue
        label = labels.get(n, "")
        residual = bool(label) and bool(RESIDUAL_RE.search(label))
        rows.append({"naics": n, "label": label, "est": est, "band": b,
                     "share": share, "emp_est": emp_est, "residual": residual,
                     "nes": None, "dfw": None, "hail": None})

    # NES availability probes + CBSA columns
    for r in rows:
        m = cbsa.get(r["naics"], {})
        r["dfw"] = m.get("19100")
        r["hail"] = sum(v for k, v in m.items() if k != "19100" and v is not None) or None
        if nes_probe:
            try:
                from cbp_lookup import api_count
                r["nes"] = not api_count("nonemp", r["naics"], "us:1").get("suppressed", True)
            except Exception:
                r["nes"] = None  # unknown — never assume published

    band_order = {"GREEN": 0, "GREEN+": 1, "YELLOW": 2, "ORANGE": 3, "PURPLE": 4, "WATCH": 5}
    rows.sort(key=lambda r: (band_order.get(r["band"], 9), -r["est"]))

    lines = [f"# Niche screener — CBP 2022 (sectors: {sectors or 'ALL'})",
             f"window {args.min_estab:,}-{args.max_estab:,} · owner-op <20emp ≥ {args.lt20_share:.0%} · NES probes: {'on' if nes_probe else 'off'}",
             "",
             "| NAICS | Label | ESTAB | Band | <20emp% | EMP/EST | NES6 | Resid | DFW | Hail10 |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["est"] < args.min_estab:
            continue
        lab = (r["label"] or "?")[:44]
        nes = {True: "✓", False: "✗", None: "?"}[r["nes"]]
        res = "SLICE" if r["residual"] else ""
        dfw = f"{r['dfw']:,}" if r["dfw"] is not None else "–"
        hail = f"{r['hail']:,}" if r["hail"] is not None else "–"
        sh = f"{r['share']:.0%}" if r["share"] is not None else "–"
        lines.append(f"| {r['naics']} | {lab} | {r['est']:,} | {r['band']} | {sh} | {r['emp_est']:.1f} | {nes} | {res} | {dfw} | {hail} |")
    lines += ["", "Legend: Band = tier potential on employer math (ORANGE needs NES/burst/slice lift; YELLOW hinges on lift).",
              "NES6 ✓ = 6-digit nonemployer published (exact TAM possible); ✗ = employer-only floor + directory proxy.",
              "Resid SLICE = residual bucket — ESTAB is a CEILING; name the niche(s) inside and size via directories.",
              "Hail10 = sum of hail-alley metros (DEN, OMA, MSP, CHI, OKC, ICT, MCI, STL, HOU).",
              "No hard-coded ranking: LLM scores six criteria + diversity quota (3/sector + 2 wildcards)."]
    print("\n".join(lines))
    if args.json:
        print("\n" + json.dumps({"year": 2022, "rows": rows}, indent=2))

if __name__ == "__main__":
    main()
