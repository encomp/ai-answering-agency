# Scraping Options for Local Lead Generation

## Context
We need phone numbers and basic business info for garage door repair contractors to test outreach. Volume for validation: ~500–2,000 leads. Long-run: 20,000+ nationwide.

---

## 1. Tools Rated for This Use Case

| Tool | Ease of Use | Cost | Best Volume | Compliance Notes |
|---|---|---|---|---|
| **Outscraper** | Very easy | ~$0.10–$0.25/result | 500–10,000 | Google Maps scraping; public data extraction risk remains |
| **Apify Google Maps Scraper** | Medium | ~$0.02–$0.10/result + proxy | 1,000–50,000 | Same TOS risk; highly automatable |
| **Bright Data** | Hard | From $500/month | 10,000–500,000+ | Enterprise-grade; still scraping Google Maps |
| **PhantomBuster** | Easy | ~$30–$80/month + credits | 500–10,000 | Less Maps depth |
| **Clay + Google Maps enrichment** | Medium | $0.01–$0.05/row enriched | 100–10,000 | Enriches after export; easier cleanup |
| **Google Places API** | Medium | $0.017/request + $7/1000 additional | 1–100,000+ | Official, less TOS risk, but rate-limited and missing some fields |
| **Hunter / RocketReach** | Easy | $0.05–$0.20/email found | Email-first, not phone | Good complement for cold email channels |

---

## 2. The Video's Choice: Outscraper

**How it works**
- Web UI + API
- Input: keyword + location(s)
- Output: name, phone, address, website, rating, etc.
- In the video: 513 results, $111 cost for Dallas-area scrape

**Strengths**
- Fastest path from zero to CSV
- No scripting required
- Good phone coverage
- Built-in dedupe and field filtering

**Weaknesses**
- Still a scraper; subject to Google Maps TOS
- Landline detection is not perfect; manual cleanup still required
- Costs add up if you scale to 100k+ leads
- Less pipeline automation than API-first tools

**Verdict for us:** keep Outscraper as the **validation tool** because it's fast and low-friction.

---

## 3. Top Alternatives

### A. Apify Google Maps Scraper
- **What it is**: serverless scraping actor; run from UI or API; supports batch locations and rotations.
- **Pricing**: pay-per-use; can be 2–5x cheaper than Outscraper at scale.
- **Strength**: highly automatable; good if you already use n8n/Make.
- **Weakness**: still needs proxy tuning; steeper initial setup.
- **Best if**: you are running weekly scrapes across multiple metros.

### B. Bright Data
- **What it is**: residential/mobile proxy network + Google Maps dataset/product.
- **Pricing**: starts ~$500/month; pay-per-request options exist.
- **Strength**: most reliable at scale; high deliverability.
- **Weakness**: expensive for early stage; more complex.
- **Best if**: you are at 20k+ leads/month and need consistent data quality.

### C. Google Places API
- **What it is**: official Google API for place search and details.
- **Pricing**: free tier + pay-per-request.
- **Strength**: compliant-ish; stable response schema; worldwide coverage.
- **Weakness**: no guaranteed phone field; returned result set is smaller and grouped by place ID; stricter quota.
- **Best if**: compliance is your #1 concern and you can tolerate incomplete phone coverage.

### D. PhantomBuster
- **What it is**: automation hub for Google Maps, LinkedIn, etc.
- **Pricing**: $30–$80/month + credit packs.
- **Strength**: easy to sequence; good if outreach lives in the same tool.
- **Weakness**: Google Maps dataset is shallower than Outscraper/Apify.
- **Best if**: you want one automation tool for Maps + LinkedIn/IG.

### E. Clay + enrichment
- **What it is**: start with a rough list, then enrich phone/email/tech stack.
- **Pricing**: ~$0.01–$0.05/row enriched.
- **Strength**: excellent cleanup and enrichment; great for email-first outreach.
- **Weakness**: phone enrichment quality varies; sometimes slower.
- **Best if**: cold email is your primary channel.

---

## 4. Phone Quality is the Real Product Risk

Scrapers do not clean this reliably:
- **Landlines vs mobiles**: call attempts fail or get screened.
- **Disconnected numbers**: high after a few months.
- **Numbers tagged "Google Voice"**: may have low response rates.
- **Multi-location chains**: one number serves 10 shops; owner rarely answers.

You need a post-scrape cleanup step no matter which scraper you use.

Our current `scripts/clean_leads.py` handles:
- formatting normalization
- 10-digit US mobile filtering
- duplicate removal

It does **not** yet handle:
- carrier lookup (line type)
- disconnect detection
- VOIP detection

---

## 5. Recommended Scraping Stack by Phase

### Phase 1 — Validation ($0–$200)
- **Tool**: Outscraper
- **Volume**: 500–1,000 leads
- **Output**: CSV → manual Sheets cleanup → `scripts/clean_leads.py`
- **Goal**: prove outreach conversion before scaling spend

### Phase 2 — Repeatable Pipeline ($50–$300/month)
- **Tool**: Apify or PhantomBuster
- **Volume**: 1,000–10,000 leads/month across multiple metros
- **Output**: API → Sheets/CSV → automated cleanup
- **Goal**: predictable lead flow with lower per-lead cost

### Phase 3 — Scale / Compliance ($500+/month)
- **Tool**: Bright Data or Google Places API + enrichment
- **Volume**: 20,000+/month
- **Output**: structured pipeline into CRM
- **Goal**: data quality and lowest per-lead cost at scale

---

## 6. Important: Scraping Is Not Consent

Repeating because this matters:
- Scraped phone numbers are **not consent** under TCPA.
- Bulk texting these numbers is legally risky.
- Cold emailing scraped business emails is generally safer and still effective.
- Consider buying **lead data from compliant providers** if you want to call/text:
  - **ZoomInfo**, **Apollo**, **Lusha**, **D&B Hoovers**
  - More expensive, but expressly licensed for outreach

---

## 7. Repo Additions

I created this as a new file in the repo:
- `docs/scraping-options.md`

Existing related file:
- `scripts/clean_leads.py`

If useful, I can add next:
- `docs/scraping-pipeline.md` — end-to-end workflow: scraper → cleanup → CRM → campaign
- `scripts/enrich_leads.py` — carrier/line-type lookup stub once we pick an enrichment API
