# Agency Website Spec v2

## Brand

Name validation status:
- Hatch — strong candidate, some AI/brand saturation
- Slate — nice imagery, some construction AI overlap
- Beacon — existing enterprise AI brands
- Rise — cleaner search footprint so far
- Meridian — mostly financial/CRM AI
- Signal — strong AI brand in reputation/monitoring

Working name for copy drafts: Hatch
Tagline direction: "AI answering and quoting for garage door contractors."

Tone: professional SaaS. Clear, confident, no fluff.

## Look and feel

Locked:
- Professional SaaS feel
- Typography: Inter, bold headings, readable body
- Clean surfaces

Color direction:
- Primary dark: slate 900
- Background: white / slate 50
- CTA: warm accent
- Secondary: sky blue for trust/automation
- Success: green

CTAs may also use dark slate with orange hover if that feels more SaaS.

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
Secondary: "Request a pilot slot" → calendar
Tertiary: "Watch a recorded walkthrough" → Loom → nurture

Rules:
- No hard pricing on home.
- Quote demo is the main conversion.
- Demo viewers enter nurture if not booked within 24h.

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
- Step 1: Hand off after-hours/missed calls
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
- Outcome: "See how many missed calls become bookable jobs."
- CTA: "Request a pilot slot"
- Form: name, business name, phone, city, current call volume estimate
- What happens next: "Setup in 24h. No credit card."

### Instant Quote Demo
- Interactive: select issue type, door style, urgency
- Output: formatted quote + estimated job value
- Disclaimer: "Demo prices. Actual quotes vary."

### Proof / Case Studies
- Pattern: "See how [city] garage door shops run after-hours leads through [brand]"
- Include tables: calls answered, quotes created, jobs closed, rev retained
- Per-case note on voice customization and escalation rule used

### Contact
- Purpose: low-friction pilot request, not general inquiry
- Output: helpdesk/CRM ticket
- Optional: direct SMS for warm inquiries only

## Post-pilot positioning
- After pilot: monthly pricing with clear tiers
- Keep open to contract vs pay-per-call
- No surprise fees, cancel anytime

## City / local SEO
- /phoenix/garage-door-ai-answering
- /dallas-fort-worth/garage-door-ai-answering
- Each page: city-specific angle + weather tie-in

## Risk disclosures
- Calls recorded for quality and training
- AI identifies itself as automated assistant
- Compliant with FCC/CTIA voice rules
- No cold outreach without consent

## Success metrics displayed
- Answer rate: 80%+
- Quote completion: 40%+
- Booked job rate: 20%+
- Revenue retained from missed calls: estimated range

## Admin / ops
- Host: Vercel or Cloudflare Pages
- Form: ConvertKit/Loops/Resend
- Demo page: static or Edge Function quote calculator
- Tracking: GA4 + one CTA event per page
- Backlog: simple admin dashboard for call leads and status
