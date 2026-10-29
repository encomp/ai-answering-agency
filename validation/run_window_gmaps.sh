#!/bin/bash
# Run window cleaning GMaps combos
cd /Users/edgarrico/ai-answering-agency/validation

declare -a combos=(
  "Dallas, TX|commercial window cleaning"
  "Dallas, TX|window cleaning service"
  "Dallas, TX|high rise window cleaning"
  "Dallas, TX|storefront window cleaning"
  "Houston, TX|commercial window cleaning"
  "Houston, TX|window cleaning service"
  "Houston, TX|high rise window cleaning"
  "Houston, TX|storefront window cleaning"
  "Chicago, IL|commercial window cleaning"
  "Chicago, IL|window cleaning service"
  "Chicago, IL|high rise window cleaning"
  "Chicago, IL|storefront window cleaning"
  "Phoenix, AZ|commercial window cleaning"
  "Phoenix, AZ|window cleaning service"
  "Phoenix, AZ|high rise window cleaning"
  "Phoenix, AZ|storefront window cleaning"
  "Denver, CO|commercial window cleaning"
  "Denver, CO|window cleaning service"
  "Denver, CO|high rise window cleaning"
  "Denver, CO|storefront window cleaning"
)

i=0
for combo in "${combos[@]}"; do
  i=$((i+1))
  metro="${combo%%|*}"
  query="${combo##*|}"
  echo "=== [$i/20] $metro | $query ==="
  python scripts/run_validation.py --niche window-cleaning --step gmaps --metro "$metro" --query "$query" 2>&1 | tail -1
  echo ""
done

echo "=== DONE ALL GMAPS ==="
