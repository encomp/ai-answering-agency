# Agency Website Spec v2

## Brand

Name options to validate:
- Hatch
- Slate
- Beacon
- Rise
- Meridian
- Signal

Working name for copy drafts: **Hatch**

Tagline direction: "AI answering and quoting for garage door contractors."

Tone: professional SaaS, not construction-bro. Clear, confident, no fluff.

## Look and feel

Locked:
- Professional SaaS feel
- Typography: Inter, bold headings, readable body
- Clean surfaces

Color direction:
- Primary dark: slate 900
- Background: white / slate 50
- CTA: warm accent (to finalize)
- Secondary: sky blue for trust / automation signal
- Success: green

## Pages stack

1. Home
2. How It Works
3. What You Get
4. Pilot
5. Instant Quote Demo
6. Proof / Case Studies
7. Contact

## CTA flow

Primary: "See a live quote demo" → email capture → demo + nurture
Secondary: "Request a pilot slot" → 15-minute calendar
Tertiary: "Watch a walkthrough" → Loom → nurture sequence

Conversion rules:
- No hard pricing on home. Send to Pilot.
- Quote demo is the main content conversion, not a sales pitch.
- Demo viewers enter nurture sequence if they don't book within 24h.

## Copy outline

### Home
- H1: "More repair leads answered while you're on a job."
- Sub: "AI voice agent + instant quote tool for garage door contractors."
- Proof bar: "32% response rate on first touch"
- CTA: "See a live quote demo"
- Bullets:
  - 24/7 answering in a voice that sounds like your shop
  - Instant repair estimate on a simple web form
  - First-call close instead of first-call voicemail

### How It Works
- Step 1: Hand off after-hours and missed calls
- Step 2: AI books estimate or creates quote
- Step 3: Your team closes while traffic is hot
- Visual: 3-column number flow

### What You Get
- New local number or forwarding from existing line
- AI voice script tailored to your shop tone
- Instant quote form with your pricing baseline
- CRM/SMS handoff to your existing tools
- Basic call and quote analytics

This closes the "what am I actually buying?" gap.

### Pilot
- H1: "Try it for one week, risk-free."
- Includes: setup, voice script, quote page, basic analytics
- Outcome line: "See how many missed calls become bookable jobs."
- CTA: "Request a pilot slot"
- Form fields: name, business name, phone, city, current call volume estimate
- What happens next: "We set up your number and script in 24h. No credit card."

### Instant Quote Demo
- Interactive: select issue type, door style, urgency
- Output: formatted quote in browser + estimated job value
- Disclaimer: "Demo prices. Actual quotes vary."

### Proof / Case Studies
- Placeholder pattern: "See how [city] garage door shops run after-hours leads through [brand]"
- Include tables: calls answered, quotes created, jobs closed, rev retained
- Per-case note on voice customization and escalation rule used

### Contact
- Purpose: low-friction pilot request, not general inquiry
- Output: helpdesk / CRM ticket
- Optional: direct SMS link for warm inquiries only

## Post-pilot positioning

Add a row to pilot page or follow-up email:
- After pilot: monthly pricing with clear tiers
- Keep door open for contract vs pay-per-call
- No surprise fees, cancel anytime

## City / local SEO plan

- Phoenix page: summer heat angle, after-hours emergency framing
- DFW page: hail season angle, storm season urgency
- Pattern: /city/garage-door-ai-answering
- Each page: city-specific stat + local phone number mention + weather tie-in

## Risk disclosures

Add brief note on Contact or FAQ:
- All calls recorded for quality and training
- AI reveals itself as automated assistant at start of each call
- Compliant with FCC/CTIA voice rules
- No cold outreach to past customers without consent

## Success metrics displayed

- Call answer rate target: 80%+
- Quote completion rate target: 40%+
- Booked job rate target: 20%+
- Revenue retained from missed calls: shown as estimated range

## Admin / ops

- Host: Vercel or Cloudflare Pages
- Form: ConvertKit / Loops / Resend
- Demo page: static or Edge Function quote calculator
- Tracking: GA4 + one CTA conversion event per page
- Backlog: simple admin dashboard for call leads and status
