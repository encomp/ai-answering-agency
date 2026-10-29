#!/usr/bin/env python3
"""
Validation pipeline orchestrator.

Usage:
    python scripts/run_validation.py --niche fence --step gmaps --metro "Dallas-Fort Worth, TX" --query "fence installation"
    python scripts/run_validation.py --niche fence --step veriphone --input data/validation/fence/*/gmaps-*.csv --output data/validation/fence/veriphone-results.csv --sample 150
    python scripts/run_validation.py --niche fence --step meta --query "fence installation"
"""

import argparse
import csv
import glob
import json
import os
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.scrape_pipeline import run_apify_actor  # type: ignore


def ensure_dirs(niche: str):
    Path(f"data/validation/{niche}").mkdir(parents=True, exist_ok=True)


def write_json_input(path: str, payload: dict):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f)


def step_gmaps(niche: str, metro: str, query: str, max_results: int = 200):
    """Run Google Maps scrape for one metro+query."""
    ensure_dirs(niche)
    metro_slug = metro.replace(",", "").replace(" ", "-")
    query_slug = query.replace(" ", "-")
    out_csv = f"data/validation/{niche}/{metro_slug}/gmaps-{query_slug}.csv"
    inp_json = f"data/validation/{niche}/{metro_slug}/gmaps-{query_slug}-input.json"

    payload = {
        "searchStringsArray": [query],
        "locationQuery": metro,
        "maxCrawledPlacesPerSearch": max_results,
        "language": "en",
    }
    write_json_input(inp_json, payload)
    print(f"Running gmaps step: {query} in {metro}")
    run_apify_actor(inp_json, out_csv, "compass/crawler-google-places")
    _warn_if_capped(out_csv, max_results, "places")
    return out_csv


def step_veriphone(input_glob: str, output_csv: str, sample: int = 150):
    """Run Veriphone lookup on a glob of GMaps CSVs."""
    load_env_from_home()
    api_key = os.environ.get("VERIPHONE_API_KEY", "")
    if not api_key:
        print("VERIPHONE_API_KEY not set; skipping veriphone step")
        return

    import requests  # type: ignore

    files = sorted(glob.glob(input_glob))
    if not files:
        print(f"No input CSVs match: {input_glob}")
        return

    # Read all files, dedupe by normalized phone, then round-robin across
    # files so the sample is metro-balanced (not biased to alphabetically-first CSV).
    seen = set()
    per_file_rows = []
    for fp in files:
        file_rows = []
        with open(fp, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                phone = row.get("phone", "").strip()
                if not phone:
                    continue
                norm = re.sub(r"[^\d]", "", phone)
                if norm in seen:
                    continue
                seen.add(norm)
                file_rows.append(row)
        per_file_rows.append(file_rows)

    # Round-robin: take one from each file until we hit the sample size.
    rows = []
    max_len = max((len(r) for r in per_file_rows), default=0)
    for i in range(max_len):
        for file_rows in per_file_rows:
            if i < len(file_rows):
                rows.append(file_rows[i])
                if len(rows) >= sample:
                    break
        if len(rows) >= sample:
            break

    print(f"Veriphone: sampling {len(rows)} leads (round-robin across {len(files)} files)...")
    mobile = landline = voip = invalid = 0
    fieldnames = None
    out_rows = []

    with open(output_csv, "w", newline="", encoding="utf-8") as outf:
        for i, row in enumerate(rows, 1):
            phone = row.get("phone", "").strip()
            norm = re.sub(r"[^\d]", "", phone)
            info = {"phone_type": "", "carrier": "", "phone_valid": ""}
            try:
                data = _veriphone_lookup(norm, api_key)
                if data.get("status") == "success" or data.get("valid"):
                    info["phone_type"] = data.get("type", data.get("phone_type", ""))
                    info["carrier"] = data.get("carrier", "")
                    info["phone_valid"] = data.get("valid", "")
                    ptype = (info["phone_type"] or "").lower()
                    if "mobile" in ptype:
                        mobile += 1
                    elif "landline" in ptype or "fixed" in ptype:
                        landline += 1
                    elif "voip" in ptype:
                        voip += 1
                    else:
                        invalid += 1
                else:
                    invalid += 1
            except Exception:
                invalid += 1

            out = dict(row)
            out.update(info)
            out_rows.append(out)
            if fieldnames is None:
                fieldnames = list(out.keys())
            if i % 20 == 0:
                print(f"  Processed {i}/{len(rows)}...")
            time.sleep(1.1)

        safe_fields = fieldnames or list(out_rows[0].keys()) if out_rows else []
        writer = csv.DictWriter(outf, fieldnames=safe_fields, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(out_rows)

    total = len(rows)
    textable = mobile + voip
    textable_pct = (textable / total * 100) if total else 0
    print(f"Veriphone summary: total={total} mobile={mobile} landline={landline} voip={voip} invalid={invalid}")
    print(f"Textable %: {textable_pct:.1f}%")
    return {
        "total": total,
        "mobile": mobile,
        "landline": landline,
        "voip": voip,
        "invalid": invalid,
        "textable_percent": round(textable_pct, 1),
    }


def _veriphone_lookup(phone: str, api_key: str) -> dict:
    """Try v2 verify endpoint first, then v1 phone endpoint."""
    import requests
    # Try v2 verify with digits-only or +1 prefixed
    candidates = []
    if phone.startswith("1") and len(phone) == 11:
        candidates.append(phone)
    if len(phone) == 10:
        candidates.append("1" + phone)
    candidates.append(phone)

    for candidate in candidates:
        try:
            resp = requests.get(
                "https://api.veriphone.io/v2/verify",
                params={"phone": candidate, "key": api_key},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success" or data.get("valid"):
                    return data
        except Exception:
            continue

    # Final fallback: v1 path
    try:
        resp = requests.get(
            f"https://api.veriphone.io/v1/phone/{phone}",
            params={"key": api_key},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {}


def step_meta(niche: str, query: str, days: int = 30, media_type: str = "all", max_ads: int = 100):
    """Run Meta Ads Library scrape for one query."""
    ensure_dirs(niche)
    query_slug = query.replace(" ", "-")
    out_csv = f"data/validation/{niche}/meta-ads-{query_slug}.csv"
    inp_json = f"data/validation/{niche}/meta-ads-{query_slug}-input.json"

    payload = {
        "searchQueries": [query],
        "country": "US",
        "activeStatus": "active",
        "mediaType": media_type,
        "onlyAdsNewerThan": f"{days} days",
        "maxAds": max_ads,
    }
    write_json_input(inp_json, payload)
    print(f"Running meta ads step: {query}")
    run_apify_actor(inp_json, out_csv, "automation-lab/facebook-ads-library")
    _warn_if_capped(out_csv, max_ads, "ads")
    return out_csv


def _warn_if_capped(csv_path: str, cap: int, unit: str):
    """If the CSV row count equals the cap, the true count may exceed it (floor)."""
    p = Path(csv_path)
    if not p.exists():
        return
    with open(p, newline="", encoding="utf-8") as f:
        row_count = sum(1 for _ in f) - 1  # minus header
    if row_count >= cap:
        print(f"  ⚠️  {row_count} {unit} returned (== cap {cap}) — true count may be HIGHER; this is a FLOOR")


def load_env_from_home():
    """Load ~/.hermes/.env into os.environ if not already set."""
    env_path = Path.home() / ".hermes" / ".env"
    if not env_path.exists():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("\"'")
            if key and key not in os.environ:
                os.environ[key] = value


def main():
    parser = argparse.ArgumentParser(description="Validation pipeline orchestrator")
    parser.add_argument("--niche", required=True, help="Niche name (e.g. fence)")
    parser.add_argument("--step", choices=["gmaps", "veriphone", "meta"], required=True)
    parser.add_argument("--metro", help="Metro area for gmaps step")
    parser.add_argument("--query", help="Search query for gmaps/meta step")
    parser.add_argument("--input", help="Input CSV glob for veriphone step")
    parser.add_argument("--output", help="Output CSV for veriphone step")
    parser.add_argument("--sample", type=int, default=150, help="Sample size for veriphone step")
    parser.add_argument("--days", type=int, default=30, help="Date range for meta step")
    parser.add_argument("--media-type", default="all", help="Media type for meta step")
    parser.add_argument("--max-results", type=int, default=200,
                        help="GMaps: max places per search (default 200; hitting this cap means count is a FLOOR)")
    parser.add_argument("--max-ads", type=int, default=100,
                        help="Meta Ads: max ads per query (default 100; actor allows up to 500)")
    args = parser.parse_args()

    if args.step == "gmaps" and (not args.metro or not args.query):
        parser.error("--metro and --query are required for gmaps step")
    if args.step == "meta" and not args.query:
        parser.error("--query is required for meta step")
    if args.step == "veriphone" and (not args.input or not args.output):
        parser.error("--input and --output are required for veriphone step")

    if args.step == "gmaps":
        step_gmaps(args.niche, args.metro, args.query, args.max_results)
    elif args.step == "veriphone":
        step_veriphone(args.input, args.output, args.sample)
    elif args.step == "meta":
        step_meta(args.niche, args.query, args.days, args.media_type, args.max_ads)


if __name__ == "__main__":
    main()
