# Pilot Checklist

## Purpose
Run pilots consistently, reduce setup mistakes, and gather the evidence needed to convert to paid or improve the offer.

Default limit: **5 active pilots at once** during validation.

---

## 1. Pre-Pilot Setup

### Tools & Access
- [ ] Voice AI provider account created (Bland / Synthflow / Vapi / Retell)
- [ ] Dedicated phone number provisioned (local area code preferred)
- [ ] CRM / lead-logging configured (HighLevel, Zoho, Sheets, or webhook)
- [ ] Email summary notifications enabled for owner and agency
- [ ] Call recording enabled (verify state consent rules)

### Contract & Payment
- [ ] Send pilot agreement via DocuSign / HelloSign / email
- [ ] Collect signed copy before go-live
- [ ] Set payment method for post-pilot conversion (Stripe / Paddle invoice / ACH)
- [ ] Add pilot end date and auto-reminder 3 days before

### Number Porting (if applicable)
- [ ] Submit port request to carrier / provider
- [ ] Set temporary forwarding from old number to new AI line
- [ ] Confirm port completion date and test inbound call

---

## 2. Go-Live Checklist

### Voice Agent Configuration
- [ ] Business name, voice, timezone set
- [ ] Welcome message recorded/published
- [ ] Working hours set to 24/7
- [ ] Knowledge base / script loaded:
  - [ ] Greeting
  - [ ] Name collection
  - [ ] Address/service issue collection
  - [ ] Urgency detection rules
  - [ ] Forward-to-owner logic for urgent calls
  - [ ] Closing: "we'll call back shortly"
- [ ] Test call completed with personal cell
- [ ] Recording and transcript verified
- [ ] Email summary received and readable

### Quote Tool (Full Stack only)
- [ ] Embedded on contractor website (iframe or subdomain)
- [ ] Demo form tested end-to-end
- [ ] Thank-you / lead-capture flow confirmed
- [ ] Owner can access basic admin view

---

## 3. During Pilot (Daily / Weekly)

### Daily
- [ ] Check call log + transcripts for failures
- [ ] Replay any misrouted or failed calls
- [ ] Reply to owner messages within 24 hours

### Weekly
- [ ] Send weekly recap to owner:
  - [ ] Calls answered vs missed
  - [ ] Closed leads count
  - [ ] Any disputed leads resolved
- [ ] Log feedback in `docs/case-study-template.md` notes section
- [ ] Update script/knowledge base if owner requests wording changes

---

## 4. Pilot End & Conversion

### 3 Days Before End
- [ ] Send reminder: "Pilot ends in 3 days. We'll convert you to [Tier] unless you say otherwise."
- [ ] Include simple button: "Keep it" or "Cancel"

### Final Day
- [ ] Send final pilot report:
  - [ ] Total calls
  - [ ] Closed leads
  - [ ] Urgent calls forwarded
  - [ ] Estimated value of captured work
- [ ] If converting:
  - [ ] Send first invoice / set auto-pay
  - [ ] Confirm plan: pay-per-lead, retainer, or full stack
  - [ ] Request testimonial / case-study permission
  - [ ] Schedule 30-day check-in
- [ ] If not converting:
  - [ ] Send cancellation confirmation
  - [ ] Offer data export (leads CSV, recordings)
  - [ ] Ask reason for leaving (short survey)

---

## 5. Success Criteria

Pilot is considered successful if:
- At least one closed lead was generated, OR
- Owner explicitly states the service reduced their stress / saved them a job, OR
- Owner refers another shop

Pilot is unsuccessful if:
- Zero calls received, OR
 - Technical failures prevented normal operation for >2 days, OR
- Owner did not respond to 2 consecutive check-ins

---

## 6. Data to Capture Per Pilot

| Field | Example |
|---|---|
| Business name | ABC Garage Door |
| Owner name | Chris |
| Location | Dallas, TX |
| Plan tested | Tier 2 Retainer |
| Pilot dates | Jan 1 – Jan 14 |
| Total calls | 18 |
| Missed calls | 0 |
| Closed leads | 2 |
| Urgent forwards | 1 |
| Owner feedback | "Wish the voice sounded more local." |
| Conversion | Yes → Retainer $149/mo |
| Testimonial | [link / quote / video] |

---

## 7. Red Flags During Pilot

- Owner does not respond to 2+ check-ins → escalate with personal call, not email.
- >20% of calls fail or misroute → pause outreach until fixed.
- Owner wants heavy customizations before paying → treat as bad-fit client; end pilot gracefully.
- Owner asks for lead guarantees not defined in `docs/pricing-playbook.md` → redirect to pilot-to-paid terms.

---

## 8. Tools for This Checklist

- Notion / Obsidian task database or simple Sheets tracker
- Calendar reminders for pilot end dates
- Zapier / Make webhook from voice AI to Slack / email for daily summaries
- Loom for recording feedback calls and voice agent demos
