#!/bin/bash
# Run remaining fence GMaps combos
cd /Users/edgarrico/ai-answering-agency/validation

declare -a combos=(
  "Dallas, TX|commercial fence installation"
  "Houston, TX|fence contractor"
  "Houston, TX|commercial fence installation"
  "Houston, TX|privacy fence"
  "Chicago, IL|fence installation"
  "Chicago, IL|privacy fence"
  "Chicago, IL|fence contractor"
  "Chicago, IL|commercial fence installation"
  "Phoenix, AZ|fence installation"
  "Phoenix, AZ|privacy fence"
  "Phoenix, AZ|fence contractor"
  "Phoenix, AZ|commercial fence installation"
  "Denver, CO|fence installation"
  "Denver, CO|privacy fence"
  "Denver, CO|fence contractor"
  "Denver, CO|commercial fence installation"
)

i=0
for combo in "${combos[@]}"; do
  i=$((i+1))
  metro="${combo%%|*}"
  query="${combo##*|}"
  echo "=== [$i/16] $metro | $query ==="
  python scripts/run_validation.py --niche fence --step gmaps --metro "$metro" --query "$query" 2>&1 | tail -1
  echo ""
done

echo "=== DONE ALL GMAPS ==="
