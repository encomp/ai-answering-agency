#!/usr/bin/env python3
"""
Extended lead pipeline with real Apify actor execution.

Usage:
    python scripts/scrape_pipeline.py --source apify --actor-id compass/crawler-google-places \
        --input query.json --output places.csv
"""

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.clean_leads import clean_leads  # type: ignore
from scripts.enrich_leads import enrich_leads  # type: ignore


def load_env():
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


def retry_request(fn, max_attempts=3, backoff=2):
    """Retry a callable on 429/5xx with exponential backoff."""
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            resp = fn()
            if resp.status_code in (429, 500, 502, 503, 504):
                wait = backoff ** attempt
                print(f"  Retry {attempt}/{max_attempts} after {resp.status_code}, waiting {wait}s...")
                time.sleep(wait)
                continue
            return resp
        except Exception as exc:
            last_exc = exc
            wait = backoff ** attempt
            print(f"  Retry {attempt}/{max_attempts} after error, waiting {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"Max retries exceeded: {last_exc}")


def run_apify_actor(input_path: str, output_path: str, actor_id: str) -> str:
    """
    Execute an Apify actor and save results as CSV.

    Flow:
      1. Try run-sync-get-dataset-items
      2. On 408/409, fall back to async start/poll/fetch
    """
    load_env()
    api_key = os.environ.get("APIFY_API_KEY", "")
    if not api_key:
        print("Apify auth failed - check APIFY_API_KEY")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        actor_input = json.load(f)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Try sync endpoint first
    actor_path = actor_id.replace("/", "~")
    sync_url = f"https://api.apify.com/v2/acts/{actor_path}/run-sync-get-dataset-items?token={api_key}"
    print(f"Calling Apify sync endpoint for {actor_id}...")

    def sync_call():
        import requests
        return requests.post(sync_url, json=actor_input, headers=headers, timeout=120)

    resp = retry_request(sync_call)

    if resp.status_code in (408, 409):
        print(f"Sync endpoint returned {resp.status_code}, falling back to async...")
        items = _apify_async_fallback(actor_id, actor_input, api_key, headers)
    elif resp.status_code == 401 or resp.status_code == 403:
        print("Apify auth failed - check APIFY_API_KEY")
        sys.exit(1)
    elif resp.status_code >= 400:
        print(f"Apify error {resp.status_code}: {resp.text[:500]}")
        sys.exit(1)
    else:
        items = resp.json()

    if not isinstance(items, list):
        if isinstance(items, dict):
            items = items.get("data", items.get("items", [items]))
        else:
            items = [items]

    _write_csv(items, output_path)
    print(f"Apify actor {actor_id} returned {len(items)} results")
    return output_path


def _apify_async_fallback(actor_id, actor_input, api_key, headers):
    """Async Apify flow: start run, poll, fetch dataset."""
    import requests

    actor_path = actor_id.replace("/", "~")
    run_url = f"https://api.apify.com/v2/acts/{actor_path}/runs?token={api_key}"
    resp = retry_request(lambda: requests.post(run_url, json=actor_input, headers=headers, timeout=30))
    resp.raise_for_status()
    run_data = resp.json().get("data", {})
    run_id = run_data.get("id")
    if not run_id:
        raise RuntimeError(f"No run_id in Apify response: {resp.json()}")

    print(f"  Started run {run_id}, polling...")
    status_url = f"https://api.apify.com/v2/acts/{actor_path}/runs/{run_id}?token={api_key}"
    for _ in range(60):
        time.sleep(5)
        resp = retry_request(lambda: requests.get(status_url, headers=headers, timeout=30))
        status = resp.json().get("data", {}).get("status", "")
        if status == "SUCCEEDED":
            break
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Apify run {run_id} ended with status {status}")
    else:
        raise RuntimeError(f"Apify run {run_id} timed out polling")

    dataset_id = resp.json().get("data", {}).get("defaultDatasetId")
    if not dataset_id:
        raise RuntimeError(f"No defaultDatasetId in run {run_id}")

    items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={api_key}&format=json"
    resp = retry_request(lambda: requests.get(items_url, headers=headers, timeout=60))
    resp.raise_for_status()
    return resp.json()


def _write_csv(items, output_path):
    """Flatten list of dicts into a UTF-8 CSV."""
    if not items:
        items = [{}]

    fieldnames = []
    for item in items:
        for key in item.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for item in items:
            writer.writerow({k: item.get(k, "") for k in fieldnames})


def load_sample(input_path: str) -> str:
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    return str(p)


def run_outscraper_export(input_path: str, output_path: str) -> str:
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(
            "Outscraper mode expects an existing CSV export. "
            "Export from dashboard and pass as --input."
        )
    return str(p)


def run_pipeline(source: str, input_path: str, output_path: str, enrich: str, actor_id: str = "") -> dict:
    if source == "sample":
        raw_path = load_sample(input_path)
    elif source == "outscraper":
        raw_path = run_outscraper_export(input_path, output_path)
    elif source == "apify":
        effective_actor_id = _actor_id_override or actor_id
        if not effective_actor_id:
            raise ValueError("actor_id is required for apify source")
        raw_path = run_apify_actor(input_path, output_path, effective_actor_id)
    else:
        raise ValueError(f"Unknown source: {source}")

    with open(raw_path, newline="", encoding="utf-8") as f:
        has_header = bool(next(csv.reader(f), []))
    if not has_header:
        raise ValueError(f"No CSV header found in: {raw_path}")

    intermediate_path = str(Path(output_path).with_suffix(".clean.csv"))
    clean_stats = clean_leads(raw_path, intermediate_path)
    print("Clean:", clean_stats)

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
    parser.add_argument("--input", required=True, help="Input CSV or JSON path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument("--actor-id", help="Apify actor ID (e.g. compass/crawler-google-places)")
    parser.add_argument(
        "--enrich",
        choices=["none", "mobile", "carrier"],
        default="none",
        help="Enrichment mode passed through to enrich_leads.py",
    )
    args = parser.parse_args()

    if args.source == "apify" and not args.actor_id:
        parser.error("--actor-id is required when --source is apify")

    stats = run_pipeline(args.source, args.input, args.output, args.enrich, actor_id=args.actor_id or "")
    print("Pipeline result:", stats)


if __name__ == "__main__":
    main()
