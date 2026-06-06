# Validation Campaign: First 50 Leads

## Goal
Prove that garage door repair owners will respond to an AI answering service offer well enough to book a free 14-day pilot.

Success threshold: **≥ 3 pilot signups from 50 outbound touches** within 14 days.

---

## 1. Target Profile

- **Industry**: Garage door repair / installation
- **Geography**: DFW metro (beachhead)
- **Firm size**: 1–5 trucks, owner-operated
- **Signal**: Google Maps listing, active reviews, has a phone number on the listing
- **Exclude**: large franchises, supply-only stores, obviously inactive listings

---

## 2. Scrape Plan

**Tool**: Outscraper
**Query**: `garage door repair` in Dallas, Fort Worth, McKinney, Allen
**Expected volume**: 500–1,000 results
**Expected cost**: ~$100–$150
**Fields to export**: company name, phone, address, website, rating, reviews count

**Post-scrape cleanup**:
1. Open CSV in Google Sheets
2. Keep only rows with phone numbers that look like US business numbers
3. Conditional-format company name: highlight rows containing `repair`
4. Remove duplicate phone numbers
5. Sort: `repair` rows first, then rest randomized
6. Keep top 50 for outreach
7. Run `scripts/enrich_leads.py` if carrier lookup API key is available

---

## 3. Outreach Mix (Compliance-Safe)

Because cold SMS is legally risky without consent, this validation uses:

- **Cold email** (primary) — 30 emails
- **Facebook / Instagram local groups** (secondary) — 10 engagement touches
- **In-person / Chamber** (tertiary) — 10 touches if available

Total target touches: **50**

---

## 4. Cold Email Sequence

### First Touch (Day 1)
Subject: Quick question about [Company Name]'s after-hours calls

> Hi [First Name],
>
> I'm in Dallas and I came across [Company Name] on Google Maps. Looks like you've been in business for a while.
>
> I'm testing something for local garage door repair shops: an AI receptionist that answers calls 24/7, collects the job details, and either forwards urgent calls to you live or logs them for first-thing callback.
>
> Would it be useful to see a 60-second demo?
>
> If not, no worries at all.
>
> Best,
> [Your Name]

### Follow-Up 1 (Day 3)
Subject: RE: Quick question about [Company Name]'s after-hours calls

> Hi [First Name],
>
> Bumping this in case it got buried.
>
> I made a 45-second recording of the AI answering a fake after-hours garage door call. The caller says the door won't open and they need to leave in 10 minutes. The AI collects name, address, and callback timing.
>
> Want me to send the clip?
>
> Best,
> [Your Name]

### Follow-Up 2 (Day 7)
Subject: Last try: after-hours calls for [Company Name]

> Hi [First Name],
>
> I'll stop after this one.
>
> If after-hours calls aren't a priority right now, just say the word and I'll remove you from my list.
>
> If they are, I'm running a free 14-day pilot for the first three shops that say yes. No contract, no setup fee, no risk.
>
> Best,
> [Your Name]

---

## 5. Social / Group Sequence

**Post** (post once, then engage replies):
> Quick question for garage door owners in DFW:
>
> How many calls go to voicemail after 6 PM?
>
> I built an AI that answers those calls, collects the job details, and either forwards the urgent ones to your cell or logs them for first-thing callback.
>
> Looking for 2–3 shop owners to test it free for 14 days. No cost, no contract. I just want feedback.
>
> Drop a "me" in the comments or DM me. First come, first served.

**DM reply template** (when someone says "me"):
> Thanks! Quick two questions:
> 1. Do you currently send after-hours calls to voicemail?
> 2. Would a 14-day free trial be useful?

If yes → send pilot agreement + onboarding link.

---

## 6. Tracking Sheet

Create a Google Sheet named `Validation Campaign Tracker` with these columns:

| Company | Owner Name | Phone | Email | Source | Email 1 Sent | Follow-Up 1 | Follow-Up 2 | Response | Pilot Booked | Notes |
|---|---|---|---|---|---|---|---|---|---|---|

One row per lead. Update daily.

---

## 7. Tools & Credentials Needed

- [ ] Outscraper account with payment method
- [ ] Email sending tool: Gmail + GMass / Instantly / SmartReach ($0–$50)
- [ ] DocuSign / HelloSign for pilot agreements
- [ ] CRM or Sheets tracker
- [ ] Loom account for demo recording
- [ ] Voice AI provider account (Bland / Synthflow / Vapi) for pilot delivery

---

## 8. Schedule

| Day | Action |
|---|---|
| 1 | Run Outscraper query; export CSV |
| 1 | Clean + randomize; keep top 50 |
| 2–3 | Send first-touch emails in two batches (25 each) |
| 4–5 | Post in 3–5 local contractor Facebook groups |
| 6–7 | Send follow-up 1 to non-responders; engage group DMs |
| 10–11 | Send follow-up 2; send second batch if first batch yields no responses |
| 14 | Review metrics; decide: iterate / scale / pivot |

---

## 9. Metrics to Track

| Metric | Target |
|---|---|
| Emails sent | 30 |
| Group posts | 3 |
| Group DMs | 10 |
| Total touches | 50 |
| Email open rate | ≥ 40% |
| Response rate | ≥ 20% |
| Positive interest (“yes, tell me more”) | ≥ 5 |
| Pilot signups | ≥ 3 |
| Cost per pilot signup | < $100 |

---

## 10. Stop / Go Criteria

**Go**: If ≥ 3 pilots book by Day 14, proceed to pilot checklist and start onboarding.

**Iterate**: If 1–2 pilots book, adjust subject lines / offer / timing and rerun with new copy.

**Pivot**: If 0 pilots book after 50 touches, change one variable:
- Different niche (fence repair, tree service)
- Different channel (partner referral instead of cold outbound)
- Different offer (free quote tool instead of AI voice)

---

## 11. Repo Files Used in This Campaign

- `docs/outreach-templates.md`
- `docs/pricing-playbook.md`
- `docs/compliance.md`
- `docs/pilot-checklist.md`
- `scripts/clean_leads.py`
- `scripts/enrich_leads.py`
- `scripts/scrape_pipeline.py`

---

## 12. Notes
- Do not send SMS until legal review clears cold outreach.
- Reply to every response within 24 hours.
- Record a Loom demo before Day 2 so follow-up emails have media to attach.
