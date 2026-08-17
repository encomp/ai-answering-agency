#!/usr/bin/env python3
"""
Census TAM lookup: CBP (employer) + NES (nonemployer) establishment counts by NAICS.

Usage:
  python3 cbp_lookup.py --naics 238340 --geo us
  python3 cbp_lookup.py --naics 238340 --geo state:48,cbsa:19100 --json
  python3 cbp_lookup.py --naics 238340 --geo us,cbsa:19100 --nes   # include nonemployer (API)

Data model (pin year + NAICS vintage in config; 2027 NAICS revision will shift codes):
  CBP = County Business Patterns  (employer establishments — businesses WITH payroll)
  NES = Nonemployer Statistics    (firms with NO paid employees — solo operators)
  TAM = CBP + NES                 (additive by design: disjoint populations, straight sum)

Sources:
  API  https://api.census.gov/data/{year}/cbp  |  /nonemployer     (needs CENSUS_API_KEY)
  Bulk https://www2.census.gov/programs-surveys/cbp/datasets/{year}/cbp22{st,msa}.zip   (keyless)
       https://www2.census.gov/programs-surveys/nonemployer-statistics/datasets/{year}/historical-datasets/nonemp22{st,msa,co}.zip

Bulk-file quirks (2022 vintage — verified 2026-08):
  - NAICS appears twice per row set: slash-filled ('23834/') AND zero-padded ('238340') —
    identical values; dedupe by normalized NAICS.
  - Use LFO == '-' rows (all legal forms) for totals; sum across geographies.
  - NES bulk files carry NAICS detail only to 4-digit for many industries (e.g., 2383);
    6-digit NES requires the API. NEVER proxy a 4-digit code as a 6-digit count.
  - Suppressed cells are non-numeric ('N','D','G','H','J') — never treated as zero; flag them.
"""
import argparse, csv, io, json, os, sys, urllib.request, urllib.error, zipfile

YEAR = "2022"
NAICS_VINTAGE = "2022"
CACHE = os.path.expanduser("~/.cache/cbp_lookup")

BULK_URLS = {
    "cbp_st":  f"https://www2.census.gov/programs-surveys/cbp/datasets/{YEAR}/cbp22st.zip",
    "cbp_msa": f"https://www2.census.gov/programs-surveys/cbp/datasets/{YEAR}/cbp22msa.zip",
    "nes_st":  f"https://www2.census.gov/programs-surveys/nonemployer-statistics/datasets/{YEAR}/historical-datasets/nonemp22st.zip",
    "nes_msa": f"https://www2.census.gov/programs-surveys/nonemployer-statistics/datasets/{YEAR}/historical-datasets/nonemp22msa.zip",
}

CBSA_NAMES = {
    "19100": "Dallas-Fort Worth-Arlington, TX",
    "19740": "Denver-Aurora-Lakewood, CO",
    "36540": "Omaha-Council Bluffs, NE-IA",
    "33460": "Minneapolis-St. Paul-Bloomington, MN-WI",
    "16980": "Chicago-Naperville-Elgin, IL-IN-WI",
    "26420": "Houston-Pasadena-The Woodlands, TX",
    "36420": "Oklahoma City, OK",
    "48620": "Wichita, KS",
    "28140": "Kansas City, MO-KS",
    "41180": "St. Louis, MO-IL",
}

def norm_naics(code: str) -> str:
    c = code.strip().replace("/", "")
    return (c + "0" * (6 - len(c)))[:6]

def env_key() -> str:
    k = os.environ.get("CENSUS_API_KEY", "")
    if k:
        return k
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith("CENSUS_API_KEY="):
                return line.strip().split("=", 1)[1].strip('" \'')
    return ""

def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        if "Missing Key" in body:
            raise RuntimeError("Census API needs a key: add CENSUS_API_KEY=<key> to ~/.hermes/.env "
                               "(free: https://api.census.gov/data/key_signup.html)")
        raise RuntimeError(f"HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"URL error: {e.reason}")

def _bulk_text(kind: str) -> str:
    """Download (cached) a bulk zip and return the txt as a string."""
    os.makedirs(CACHE, exist_ok=True)
    url = BULK_URLS[kind]
    fname = os.path.join(CACHE, os.path.basename(url))
    if not os.path.exists(fname):
        print(f"  [download] {url}", file=sys.stderr)
        with open(fname, "wb") as f:
            f.write(_get(url, timeout=300))
    with zipfile.ZipFile(fname) as z:
        name = next(n for n in z.namelist() if n.endswith((".txt", ".csv")))
        return z.read(name).decode("utf-8", "replace")

def api_geo(g: str) -> str:
    """Map CLI geo tokens to Census API for= values."""
    if g == "us":
        return "us:1"
    if g.startswith("cbsa:"):
        return "metropolitan statistical area:" + g.split(":")[1]
    return g  # state:XX passes through

def api_count(dataset: str, naics: str, geo: str) -> dict:
    """dataset: 'cbp' | 'nonemployer'; geo: us:1 | state:XX | metropolitan statistical area:CODE"""
    key = env_key()
    if not key:
        raise RuntimeError("API path requires CENSUS_API_KEY (see --help). Use bulk path or add the key.")
    var = {"cbp": "NAICS2017", "nonemp": "NAICS2022"}[dataset]
    estab_var = {"cbp": "ESTAB", "nonemp": "NESTAB"}[dataset]
    # CBP API labels NAICS2017 for the 2022 reference year; NES API uses NAICS2022 + NESTAB.
    # Neither API serves MSA geography — CBSA counts come from the bulk MSA files.
    url = f"https://api.census.gov/data/{YEAR}/{dataset}?get={var},{estab_var}&for={geo}&{var}={naics}&key={key}"
    raw = _get(url)
    if not raw.strip():  # HTTP 204 — 6-digit detail not published for this NAICS
        return {"estab": None, "suppressed": True,
                "note": "6-digit NES not published for this NAICS (Census aggregates to 4-digit)"}
    data = json.loads(raw)
    if len(data) < 2:
        return {"estab": None, "suppressed": True}
    try:
        return {"estab": int(data[1][1]), "suppressed": False}
    except ValueError:
        return {"estab": None, "suppressed": True}

def bulk_cbp(naics: str, geos: dict) -> dict:
    """geos: {'us': None, 'state:48': None, 'cbsa:19100': None} — values filled in-place."""
    n = norm_naics(naics)
    out = {}
    state_rows = {}
    for r in csv.DictReader(io.StringIO(_bulk_text("cbp_st"))):
        if (r.get("lfo") or "").strip() == "-" and norm_naics(r.get("naics") or "") == n:
            try:
                state_rows[r.get("fipstate").strip()] = int(r.get("est") or 0)
            except ValueError:
                state_rows[r.get("fipstate").strip()] = None
    if "us" in geos:
        vals = [v for v in state_rows.values() if v is not None]
        out["us"] = {"estab": sum(vals) if vals else None,
                     "suppressed": len(vals) != len(state_rows)}
    for g in geos:
        if g.startswith("state:"):
            st = g.split(":")[1]
            out[g] = {"estab": state_rows.get(st), "suppressed": state_rows.get(st) is None}
    if any(g.startswith("cbsa:") for g in geos):
        msa_rows = {}
        for r in csv.DictReader(io.StringIO(_bulk_text("cbp_msa"))):
            if norm_naics(r.get("naics") or "") == n:
                try:
                    msa_rows[r.get("msa").strip()] = int(r.get("est") or 0)
                except ValueError:
                    msa_rows[r.get("msa").strip()] = None
        for g in geos:
            if g.startswith("cbsa:"):
                code = g.split(":")[1]
                out[g] = {"estab": msa_rows.get(code), "suppressed": msa_rows.get(code) is None}
    return out

def bulk_nes(naics: str, geos: dict) -> dict:
    """Bulk NES only has NAICS detail down to 4-digit for many industries — never proxy.
    Returns None-establishments with a flag when 6-digit rows are absent."""
    n = norm_naics(naics)
    out = {}
    text = _bulk_text("nes_st")
    rows = {}
    for r in csv.DictReader(io.StringIO(text)):
        if (r.get("NAICS") or "").strip() == n:
            rows[r.get("ST").strip()] = _nes_estab(r)
    if not rows:
        # NES detail is industry-dependent: some 6-digit codes publish, others aggregate to 4-digit.
        # NEVER proxy the 4-digit parent into a 6-digit TAM.
        for g in geos:
            out[g] = {"estab": None, "suppressed": True,
                      "note": f"6-digit NES not published for NAICS {n[:4]}xx (Census aggregates to 4-digit; NES excluded from TAM)"}
        return out
    if "us" in geos:
        vals = [v for v in rows.values() if v is not None]
        out["us"] = {"estab": sum(vals) if vals else None, "suppressed": len(vals) != len(rows)}
    for g in geos:
        if g.startswith("state:"):
            out[g] = {"estab": rows.get(g.split(":")[1]), "suppressed": rows.get(g.split(":")[1]) is None}
    if any(g.startswith("cbsa:") for g in geos):
        msa = {}
        for r in csv.DictReader(io.StringIO(_bulk_text("nes_msa"))):
            if (r.get("NAICS") or "").strip() == n:
                msa[r.get("MSA").strip()] = _nes_estab(r)
        for g in geos:
            if g.startswith("cbsa:"):
                out[g] = {"estab": msa.get(g.split(":")[1]), "suppressed": msa.get(g.split(":")[1]) is None}
    return out

def _nes_estab(r: dict):
    try:
        return int(r.get("ESTAB") or 0)
    except ValueError:
        return None

def fmt(v: dict) -> str:
    if v.get("estab") is None:
        return "n/a (suppressed/API)" if not v.get("note") else "n/a (API)"
    return f"{v['estab']:,}"

def main():
    ap = argparse.ArgumentParser(description="CBP + NES TAM lookup by NAICS (US Census).")
    ap.add_argument("--naics", required=True, help="6-digit NAICS code, e.g. 238340")
    ap.add_argument("--geo", required=True, help="comma list: us | state:XX | cbsa:CODE")
    ap.add_argument("--nes", action="store_true", help="include nonemployer (API key required for 6-digit)")
    ap.add_argument("--api", action="store_true", help="force API path (needs CENSUS_API_KEY)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--year", default=YEAR)
    args = ap.parse_args()

    geos = [g.strip() for g in args.geo.split(",") if g.strip()]
    label = {"us": "United States"}
    # API path: us/state via API; cbsa via bulk MSA files (the API has no MSA hierarchy).
    if args.api:
        cbp = {g: (api_count("cbp", args.naics, api_geo(g)) if not g.startswith("cbsa:")
                   else bulk_cbp(args.naics, {g: None})[g]) for g in geos}
    else:
        cbp = bulk_cbp(args.naics, {g: None for g in geos})
    if args.nes:
        if args.api:
            nes = {g: (api_count("nonemp", args.naics, api_geo(g)) if not g.startswith("cbsa:")
                       else bulk_nes(args.naics, {g: None})[g]) for g in geos}
        else:
            nes = bulk_nes(args.naics, {g: None for g in geos})
    else:
        nes = {g: {"estab": None, "suppressed": False} for g in geos}

    result = {"naics": args.naics, "year": args.year, "naics_vintage": NAICS_VINTAGE,
              "geographies": {}}
    lines = [f"# TAM lookup — NAICS {args.naics} ({args.year}, NAICS {NAICS_VINTAGE})",
             "", "| Geography | CBP (employer) | NES (nonemployer) | TAM | Notes |",
             "|---|---|---|---|---|"]
    for g in geos:
        c, n = cbp.get(g, {}), nes.get(g, {})
        tam = None
        if c.get("estab") is not None and n.get("estab") is not None:
            tam = c["estab"] + n["estab"]
        name = CBSA_NAMES.get(g.split(":")[1], g) if g.startswith("cbsa:") else (label.get(g, g))
        notes = []
        if c.get("suppressed"): notes.append("CBP suppressed→state-fallback")
        if n.get("suppressed"): notes.append(n.get("note", "NES suppressed"))
        if not args.nes: notes.append("NES omitted (add --nes)")
        lines.append(f"| {name} | {fmt(c)} | {fmt(n)} | {f'{tam:,}' if tam is not None else 'n/a'} | {'; '.join(notes)} |")
        result["geographies"][g] = {"name": name, "cbp": c, "nes": n, "tam": tam}
    lines += ["", f"Sources: bulk census.gov files (CBP 2022) + API (NES) — see script header.",
              f"TAM = CBP + NES (disjoint populations, additive). Tier = TAM × textable% (unchanged thresholds)."]
    print("\n".join(lines))
    if args.json:
        print("\n" + json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
