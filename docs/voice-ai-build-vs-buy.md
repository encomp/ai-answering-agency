# Voice AI: Build vs Buy Cost Model

## Client Count Scenarios

| Scenario | Hosted Provider Cost | Self-Hosted Cost | Break-even Trigger |
|---|---|---|---|
| **5 clients / ~500 min/mo** | $50–$100/mo | $150–$200/mo | Hosted still wins |
| **25 clients / ~2,500 min/mo** | $250–$500/mo | $250–$400/mo | ~ breakeven |
| **100 clients / ~10,000 min/mo** | $1,000–$2,000/mo | $600–$1,000/mo | Self-hosted wins |
| **500 clients / ~50,000 min/mo** | $5,000–$10,000/mo | $2,500–$4,000/mo | Self-hosted wins hard |

## Cost Assumptions

### Hosted (Vapi / Retell / Bland / Synthflow)
- $0.10–$0.20/minute inbound + outbound
- $29–$99/month base platform fee
- Usually includes number, recording, transcript, basic CRM webhooks

### Self-Hosted (Phase 2+)
- **Carrier**: Twilio Elastic SIP Trunking (~$0.0035/min) or Telnyx (~$0.002/min).
- **STT**: Deepgram Nova-2 (~$0.0043/min) or Whisper (~$0.006/min).
- **LLM**: GPT-4o-mini function-calling or GPT-4o Realtime (~$0.015/min if fully realtime; cheaper if batch).
- **TTS**: ElevenLabs (~$0.005/min) or open-source XTTS v2 (~$0 infrastructure).
- **Media server**: LiveKit Cloud or self-hosted (~$50–$150/month).
- **Recording/storage**: S3 or R2 (~$10–$30/month).
- **Total raw API cost**: ~$0.02–$0.05/min at scale.
- **Maintenance burden**: Moderate to high.

## Decision Logic

- **Use hosted** until weekly call volume exceeds ~1,000–2,000 minutes/month.
- **Switch to composable self-hosted** when hosted costs exceed $700/month and engineering bandwidth exists.
- **Never self-host** until the stack is proven and you have a maintainer who understands telephony.

---

## Phase 1 (Validation) — Hosted

Recommended providers:
- **Bland AI**: cheap, simple, inbound + outbound.
- **Synthflow**: best UI for non-technical agency ops.
- **Allo**: lowest cost consumer tier (~$15/month).
- **Vapi**: best DX if you need to debug quickly.
- **Retell**: best if voice quality and clone-style voices matter to your pitch.

Constraints:
- Accept vendor lock-in temporarily.
- Export call transcripts and recordings weekly.
- Keep CRM integration webhook-based so you can move providers later.

## Phase 2 (Growth) — Composable Stack

Reference architecture:
- **Carrier**: Twilio / Telnyx / SIP trunk into LiveKit.
- **Media server**: LiveKit (open-source, agent templates exist).
- **STT**: Deepgram Nova-2 or Whisper API.
- **LLM**: GPT-4o-mini for reasoning + function calling, or GPT-4o Realtime for latency-critical flows.
- **TTS**: ElevenLabs for polish, or Coqui/XTTS for zero marginal cost.
- **Orchestration**: n8n or FastAPI service for transfer logic and CRM sync.
- **Observability**: basic logging + recording storage.

Estimated monthly cost at 10,000 minutes:
- Platform/storage: ~$150–$250
- APIs: ~$200–$400
- Total: ~$350–$650/month

## Phase 3 (Scale) — Fully Self-Hosted

When:
- Clients > 100
- Minutes/month > 20,000
- Engineering bandwidth available

Stack:
- Self-hosted FreeSWITCH / Asterisk or continue with LiveKit self-hosted.
- Local Whisper / Deepgram hybrid.
- Local open-source TTS (XTTS v2 / Piper).
- LLM via self-hosted or GPT-4o-mini API.
- Costs drop to raw compute + bandwidth only.

Warning:
- Self-hosted voice AI is a product, not a weekend project.
- Audio quality, latency, and uptime are your responsibility.
- Plan to dedicate at least one engineer to telephony and media servers.
