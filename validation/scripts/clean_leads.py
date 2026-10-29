#!/usr/bin/env python3
"""
Lead scraping and cleanup template for garage door AI agency.
Works with Outscraper CSV exports or Google Maps scrape results.

Usage:
    python scripts/clean_leads.py input.csv output.csv
"""

import csv
import sys
import re


def normalize_phone(phone: str) -> str:
    """Strip formatting and standardize to digits-only."""
    digits = re.sub(r"[^\d]", "", phone or "")
    return digits


def is_mobile_number(phone: str, normalized: str) -> bool:
    """
    Keep only numbers that look like US cell numbers.
    Very naive: assumes 10-digit NANP starting with a valid mobile prefix.
    Strengthen this by enriching with a telecom API if needed.
    """
    if len(normalized) == 11 and normalized.startswith("1"):
        normalized = normalized[1:]
    if len(normalized) != 10:
        return False
    return normalized.startswith(("2", "3", "4", "5", "6", "7", "8", "9"))


def clean_leads(input_path: str, output_path: str) -> dict:
    kept = 0
    total = 0
    seen = set()

    fieldnames = None

    with open(input_path, newline="", encoding="utf-8") as infile, \
         open(output_path, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames or [
            "company_name", "phone", "address", "city", "website"
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            total += 1
            raw_phone = row.get("phone", "")
            norm = normalize_phone(raw_phone)
            if not norm:
                continue
            if not is_mobile_number(raw_phone, norm):
                continue
            if norm in seen:
                continue
            seen.add(norm)
            out = {k: row.get(k, "") for k in fieldnames}
            out["phone"] = norm
            writer.writerow(out)
            kept += 1

    return {"total": total, "kept_valid_mobile": kept}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_leads.py input.csv output.csv")
        sys.exit(1)
    stats = clean_leads(sys.argv[1], sys.argv[2])
    print(stats)
