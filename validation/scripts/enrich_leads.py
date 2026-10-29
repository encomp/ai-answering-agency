#!/usr/bin/env python3
"""
Lead enrichment and cleanup for garage door AI agency.
Reads a CSV of scraped leads, enriches phone/line metadata when configured,
and outputs a clean CSV ready for outreach.

Usage:
    python scripts/enrich_leads.py input.csv output.csv

    # With carrier lookup API (configure API_KEY below):
    python scripts/enrich_leads.py input.csv output.csv --lookup carrier

Configuration:
    Set VERIPHONE_API_KEY or NUMVERIFY_API_KEY env var to enable lookups.
"""

import argparse
import csv
import os
import re
import sys
from typing import Optional


def normalize_phone(phone: str) -> str:
    return re.sub(r"[^\d]", "", phone or "")


def format_phone(phone: str) -> str:
    """Return (10) format for US numbers, or raw if not US."""
    digits = normalize_phone(phone)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return phone or ""
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"


def is_us_phone(normalized: str) -> bool:
    if len(normalized) == 11 and normalized.startswith("1"):
        normalized = normalized[1:]
    return len(normalized) == 10 and normalized.isdigit()


def twilio_lookup(phone: str, api_key: Optional[str]) -> dict:
    """Placeholder for Twilio Lookup integration."""
    if not api_key:
        return {}
    try:
        from twilio.rest import Client  # type: ignore
    except ImportError:
        return {}
    try:
        client = Client(api_key, api_key)
        number = client.lookups.v1.phone_numbers(phone).fetch(type=["carrier"])
        carrier = number.carrier or {}
        return {
            "carrier": carrier.get("name", ""),
            "line_type": carrier.get("type", ""),
            "lookup_source": "twilio",
        }
    except Exception:
        return {}


def numverify_lookup(phone: str, api_key: Optional[str]) -> dict:
    """Placeholder for NumVerify integration."""
    if not api_key:
        return {}
    import requests  # type: ignore
    try:
        resp = requests.get(
            "http://apilayer.net/api/validate",
            params={"access_key": api_key, "number": phone, "country_code": "US", "format": 1},
            timeout=10,
        )
        data = resp.json()
        if data.get("valid"):
            return {
                "carrier": data.get("carrier", ""),
                "line_type": data.get("line_type", ""),
                "lookup_source": "numverify",
            }
    except Exception:
        pass
    return {}


def veriphone_lookup(phone: str, api_key: Optional[str]) -> dict:
    """Lookup line type via Veriphone API."""
    if not api_key:
        return {}
    import requests  # type: ignore
    try:
        resp = requests.get(
            f"https://api.veriphone.io/v1/phone/{phone}",
            params={"key": api_key},
            timeout=10,
        )
        data = resp.json()
        if data.get("status") == "success" or data.get("valid"):
            return {
                "carrier": data.get("carrier", ""),
                "line_type": data.get("type", data.get("phone_type", "")),
                "lookup_source": "veriphone",
            }
    except Exception:
        pass
    return {}


DEFAULT_FIELDS = [
    "company_name",
    "phone",
    "phone_formatted",
    "line_type",
    "carrier",
    "address",
    "city",
    "website",
    "raw_source",
]


def _pick_lookup_key():
    """Return (lookup_fn, api_key) preferring Veriphone."""
    veriphone_key = os.environ.get("VERIPHONE_API_KEY")
    if veriphone_key:
        return veriphone_lookup, veriphone_key
    twilio_key = os.environ.get("TWILIO_LOOKUP_API_KEY")
    if twilio_key:
        return twilio_lookup, twilio_key
    numverify_key = os.environ.get("NUMVERIFY_API_KEY")
    if numverify_key:
        return numverify_lookup, numverify_key
    return None, None


def enrich_leads(input_path: str, output_path: str, lookup: str = "none") -> dict:
    lookup_fn, api_key = _pick_lookup_key() if lookup == "carrier" else (None, None)
    total = 0
    kept = 0
    seen = set()

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = list(DEFAULT_FIELDS)
        for col in (reader.fieldnames or []):
            if col not in fieldnames:
                fieldnames.append(col)

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            total += 1
            raw_phone = row.get("phone", "")
            norm = normalize_phone(raw_phone)
            phone_formatted = format_phone(raw_phone)

            info = {
                "company_name": row.get("company_name", ""),
                "phone": norm,
                "phone_formatted": phone_formatted,
                "line_type": "valid_us_phone",
                "carrier": "",
                "address": row.get("address", ""),
                "city": row.get("city", ""),
                "website": row.get("website", ""),
                "raw_source": row.get("raw_source", ""),
            }

            if lookup == "carrier" and lookup_fn and api_key:
                info.update(lookup_fn(norm, api_key))

            for col in (reader.fieldnames or []):
                if col not in info:
                    info[col] = row.get(col, "")

            if not norm:
                continue
            if lookup == "mobile" and not is_us_phone(norm):
                continue
            if norm in seen:
                continue

            seen.add(norm)
            writer.writerow(info)
            kept += 1

    return {"total": total, "kept": kept}


def main():
    parser = argparse.ArgumentParser(description="Enrich leads from CSV")
    parser.add_argument("input", help="Input CSV path")
    parser.add_argument("output", help="Output CSV path")
    parser.add_argument(
        "--lookup",
        choices=["none", "mobile", "carrier"],
        default="none",
        help="Enrichment level: none, mobile-only, or carrier lookup if API key configured",
    )
    args = parser.parse_args()
    stats = enrich_leads(args.input, args.output, args.lookup)
    print(stats)


if __name__ == "__main__":
    main()
