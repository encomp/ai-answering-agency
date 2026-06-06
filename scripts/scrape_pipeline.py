#!/usr/bin/env python3
"""
End-to-end lead pipeline:
  scrape (Outscraper/placeholders) -> cleanup -> enrich -> CSV output

This is a thin orchestrator. Real scraping is left as a placeholder so we
can swap in Outscraper API, Apify, or a Google Places export later without
changing downstream steps.

Usage:
    python scripts/scrape_pipeline.py --source sample \
        --input data/raw/outscraper_export.csv \
        --output data/clean/enriched_leads.csv

    # With carrier enrichment:
    TWILIO_LOOKUP_API_KEY=... python scripts/scrape_pipeline.py \
        --source sample --input raw.csv --output clean.csv --enrich carrier

Sources:
    sample      -> use provided sample CSV
    outscraper  -> call Outscraper Google Places Search API if configured
    apify       -> call Apify Google Maps scraper actor if configured
"""

import argparse
import csv
import os
import sys
from pathlib import Path

# Ensure repo root on path for sibling imports
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.clean_leads import clean_leads  # type: ignore
from scripts.enrich_leads import enrich_leads  # type: ignore


# -------------------------
# Source adapters
# -------------------------

def load_sample(input_path: str) -> str:
    """
    Validate input exists and return path. Intended for quick testing against
    an existing scraper export.
    """
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    return str(p)


def run_outscraper_export(input_path: str, output_path: str) -> str:
    """
    Placeholder for Outscraper API-based scrape. For now, this assumes you
    already exported a CSV from the Outscraper dashboard and saves its path.
    """
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(
            "Outscraper mode expects an existing CSV export. "
            "Export from dashboard and pass as --input."
        )
    return str(p)


def run_apify_actor(input_path: str, output_path: str) -> str:
    """
    Placeholder for Apify actor-based pipeline. In production this would:
      1. Submit actor run with query + location
      2. Poll for dataset
      3. Export dataset to CSV at output_path
      4. Return output_path

    For now we just require --input to exist.
    """
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(
            "Apify mode expects an existing CSV export for now. "
            "Pass the actor dataset export as --input."
        )
    return str(p)


# -------------------------
# Pipeline
# -------------------------

def run_pipeline(source: str, input_path: str, output_path: str, enrich: str) -> dict:
    # Step 1: obtain raw CSV
    if source == "sample":
        raw_path = load_sample(input_path)
    elif source == "outscraper":
        raw_path = run_outscraper_export(input_path, output_path)
    elif source == "apify":
        raw_path = run_apify_actor(input_path, output_path)
    else:
        raise ValueError(f"Unknown source: {source}")

    # Step 2: validate raw file is readable
    with open(raw_path, newline="", encoding="utf-8") as f:
        has_header = bool(next(csv.reader(f), []))
    if not has_header:
        raise ValueError(f"No CSV header found in: {raw_path}")

    # Step 3: cleanup (normalize phones, dedupe)
    intermediate_path = str(Path(output_path).with_suffix(".clean.csv"))
    clean_stats = clean_leads(raw_path, intermediate_path)
    print("Clean:", clean_stats)

    # Step 4: enrich
    enrich_stats = enrich_leads(intermediate_path, output_path, lookup=enrich)
    print("Enrich:", enrich_stats)

    return {
        "source": source,
        "raw_path": raw_path,
        "clean_path": intermediate_path,
        "output_path": output_path,
        "clean_stats": clean_stats,
        "enrich_stats": enrich_stats,
    }


def main():
    parser = argparse.ArgumentParser(description="Lead pipeline: scrape -> cleanup -> enrich")
    parser.add_argument("--source", choices=["sample", "outscraper", "apify"], default="sample")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument(
        "--enrich",
        choices=["none", "mobile", "carrier"],
        default="none",
        help="Enrichment mode passed through to enrich_leads.py",
    )
    args = parser.parse_args()
    stats = run_pipeline(args.source, args.input, args.output, args.enrich)
    print("Pipeline result:", stats)


if __name__ == "__main__":
    main()
