# OpenCode Provider Route — AI Army (Task V)

**Built:** 2026-11-16 ~07:42 PST. **Inventory only — no signups, no keys generated, no money.**
**The back end (spreadsheet, per Tony's rule):** [OpenCode Provider Route — AI Army](https://docs.google.com/spreadsheets/d/1_mw40Iye89PuJv4lsGjxdZj50QSdY5CixiPCxtV4odo/edit) — 324 provider rows, columns: Provider | Auth type | Aggregator? | Models reachable | Free tier | Army account held? | Plugs in today? | Notes. This markdown is the abstract of that sheet.

## HEADLINE

- **324 providers** are in OpenCode's out-of-the-box catalog as cached on djdrop itself (`~/.cache/opencode/models.json` in the Kali WSL, read live 2026-11-16; same catalog as models.dev, which OpenCode's docs name as its source). The overwhelming majority auth by **API key**; the exceptions (OAuth / subscription / cloud credential chains) are listed in §1.
- **Plugs in TODAY on djdrop (already connected, measured):** **Google** (API key in `~/.config/opencode/opencode.jsonc`; default model `google/gemini-3.7-flash`), **GitHub Copilot** (device OAuth; auth present), **OpenCode Zen** (auth present). Three routes are live before any new signup.
- **Top aggregator unlocks per single signup:** **OpenRouter** — 377 catalog models, real free tier (`:free` models, 20 RPM / 50 requests/day, no card). **Vercel AI Gateway** — 418 models, and a Vercel account is **already held** (only a gateway key creation stands between it and use — not done here, inventory only). **Requesty** — 185 models, publishes free models. **Poe** — account already registered, 139 models behind one API key, but the API is metered/paid.
- **The honest limit (§4):** an API/aggregator answer is a **model verdict**, not a verdict from the named consumer **program**. It must be labeled by route on the scoreboard and never counted as a native-product answer.

## §0 — djdrop's actual OpenCode state (measured, read-only)

- OpenCode runs in Kali WSL on djdrop (v1.19.4, per TOOLS.md). The Windows-side config dir `~/.config/opencode/` holds `opencode.jsonc` + provider credential stores for **github-copilot**, **google**, **opencode** — i.e., those three are connected accounts on the device.
- `opencode.jsonc` configures the **google** provider with an API key (present on device; value NOT reproduced here) and ~35 Gemini/Gemma model entries; default model `google/gemini-3.7-flash`, small model `google/gemini-3.5-flash-lite`.
- The WSL catalog cache lists **324 providers**. Counts below are models per provider in that catalog.

## §1 — The provider list (from the official catalog)

Full 324-row list = the spreadsheet (link above). Structure of the catalog:

- **Auth = API key (~300 providers):** every long-tail gateway/host (OpenRouter, Together, Fireworks, Groq, Cerebras, DeepInfra, Nebius, Novita, SiliconFlow, Chutes, Baseten, Modal, SambaNova, etc.) plus the direct vendor APIs (OpenAI, Anthropic, Google, xAI, Mistral, DeepSeek, Cohere, AI21, Perplexity…).
- **Auth ≠ plain API key (the exceptions):**
  - **OpenAI** — API key **or** "Sign in with ChatGPT" OAuth (docs: usage counts against a Plus/Pro plan).
  - **GitHub Copilot** — device OAuth; requires Copilot entitlement (Copilot Free qualifies). **Connected on djdrop.**
  - **OpenCode Go** (`opencode-go`, 42 models) — subscription bundle of coding models, connected with its own key.
  - **OpenCode Zen** (`opencode`, 140 models) — OpenCode's own curated pay-as-you-go gateway. **Connected on djdrop.**
  - **Azure / Azure Cognitive Services** (97 models each) — API key or Microsoft Entra ID via Azure CLI; needs a resource name.
  - **Amazon Bedrock** (208 models) — AWS credential chain (profile / keys / SSO / bearer token).
  - **Vertex / Vertex (Anthropic)** (64 / 18 models) — Google ADC (`gcloud auth application-default login` or service-account JSON) + project.
  - **Cloudflare AI Gateway** (77) — API token + account + gateway IDs. **Cloudflare Workers AI** (29) — account ID + key.
  - **Snowflake Cortex** (25) — account + PAT. **Databricks** (31) — host + token. **SAP AI Core** (51) — service-key JSON. **watsonx** (5) — API key + project ID. **GitLab Duo** (31) — token. **Hugging Face** (84) — HF token.
  - **LM Studio** (3) — local server, no account. (Ollama local discovery likewise needs no account per the docs.)
- Any OpenAI-compatible endpoint can also be added as a custom provider in `opencode.jsonc` (docs, "Providers") — so the 324 are a floor, not a ceiling.

## §2 — The aggregators (one login → many models)

"Models reachable" = models listed for that provider in the catalog on djdrop. "Speaks for" = distinct model families/programs an answer could come from — always as a *model* verdict (§4).

| Aggregator | Models | Free tier? | Programmatic use on free tier? | Notes |
|---|---|---|---|---|
| **OpenRouter** (`openrouter`) | 377 | **Yes** — `:free` variants, 20 RPM, 50 req/day with no purchase (1,000/day after a one-time $10 credit buy) | **Yes** — the free tier IS the API; limits are request caps, free roster rotates (~16–28 free chat models at last checks: Nemotron, Gemma, Inkling-class) | Frontier models (Claude/GPT/Gemini flagships) are paid per token. The single best verdict-roundup unlock. |
| **Vercel AI Gateway** (`vercel`) | 418 | **Yes** — $5/month AI Gateway credit per team, "Free Tier eligible" models only; zero markup | Yes, within the credit and eligible-model subset | **Account already held** (Vercel connected). Needs only a gateway API key created — a next step, not done in this inventory. |
| **OpenCode Zen** (`opencode`) | 140 | Partial — pay-as-you-go; some models free/limited-time | Yes (it exists for programmatic use) | **Already connected on djdrop.** Curated by the OpenCode team. |
| **Requesty** (`requesty`) | 185 | **Yes** — free models published per-model with expiry dates | Yes | Strong #2 signup candidate after OpenRouter. |
| **Poe** (`poe`) | 139 | **No** — Poe's API is metered/paid (points); a Poe chat subscription is not API credit | Paid only | **Account already registered** (army registry). One key reaches Poe's whole bot/model catalog, but every call costs. |
| **NanoGPT** (`nano-gpt`) | 623 | No — pay-as-you-go | Paid only | Largest catalog in the set; useless for a $0 roundup. |
| **Kilo Gateway** (`kilo`) | 464 | Not verified | — | Huge catalog; free-tier status not established from primary sources in this run. |
| **LLM Gateway** (`llmgateway-providers` 468 / `llmgateway` 207) | 468 | Not verified | — | Same caveat. |
| **Eden AI** (`edenai`) | 396 | Not verified | — | Same caveat. |
| **AIHubMix** (`aihubmix`) | 160 | Not verified | — | Same caveat. |
| **AI/ML API** (`aimlapi`) | 168 | Not verified | — | Same caveat. |
| **Together AI** (`togetherai`) | 33 | No standing free tier — paid API (trial credits only) | Paid only | Host, not a marketplace: open-weight models only. |
| **Fireworks AI** (`fireworks-ai`) | 27 | No standing free tier — paid API (trial credits only) | Paid only | Host: open-weight models only. |
| **OpenCode Go** (`opencode-go`) | 42 | No — paid subscription (~$10/mo) | Subscription use | A subscription bundle, not a free route. Excluded by the no-money rule. |

## §3 — The map: AI Army Registry × OpenCode

Registry read from the AI ARMY REGISTRY sheet snapshot (read-back verified 2026-11-16 07:26 PST; 48 Registered / 95). "Plugs in" = the held account can drive OpenCode as that provider **today**, with no new signup and no money.

**Plugs in today:**
- **Google / Gemini** — Gemini registered AND the Google provider is already keyed into djdrop's OpenCode (default model). Gemini-family model verdicts are available *right now* through OpenCode, in addition to the native Gemini answer already collected.
- **GitHub Copilot** — connected on djdrop via device OAuth. Copilot's catalog (39 models: OpenAI/Anthropic/Google families as served by Copilot) is reachable today.
- **OpenCode Zen** — connected on djdrop; 140 models, pay-as-you-go (some free). Usable today, metered.
- **Vercel AI Gateway** — account held; $5/mo free credit; **one step away** (create gateway API key). Highest models-per-effort unlock on the board: 418.

**Account held, does NOT plug in (consumer account ≠ API access):**
- **ChatGPT (OpenAI)** — free consumer plan; OpenCode's sign-in route needs Plus/Pro, the API needs a paid key.
- **Grok (xAI)** — free consumer account; XAI_API_KEY is a separate paid developer account.
- **DeepSeek** — chat registered; the API is a separate prepaid balance ($0 balance = no calls). Cheapest paid route on the board, but paid = excluded by the no-money rule.
- **Mistral Le Chat** — chat registered; the API lives in La Plateforme (separate console signup, which *does* have a free tier — one signup away).
- **Perplexity** — registered; Sonar API is paid and separate.
- **Poe** — registered; API key can be created from the account, but calls are metered/paid.
- **Qwen Chat (Alibaba)** — DashScope API is a separate Alibaba Cloud account. **Kimi (Moonshot)** — API platform separate. **Z.ai (GLM)** — API platform separate.

**Not held:** Claude (Anthropic) — BLOCKED in the registry, and the Anthropic API is paid anyway; MiniMax — PENDING TAP; Hugging Face — PENDING TAP (one password step; HF has a free inference quota once in).

**Unlock ranking for the verdict roundup (verdict targets per signup):**
1. **OpenRouter signup** — 1 signup → free API verdicts from the rotating free roster (open-weight families: Meta, Qwen, Mistral, Google Gemma, NVIDIA, DeepSeek-class when offered) at 50 requests/day. The brief + 6 follow-ups ≈ 7+ calls per model — the daily cap, not the catalog, is the bottleneck.
2. **Vercel AI Gateway key** (account already held) → $5 of credit across 418 models incl. frontier families — enough for a handful of full brief runs on paid-tier models at $0 out of pocket.
3. **Requesty signup** → second free-model roster, hedges OpenRouter's rotation.
4. **Mistral La Plateforme signup** → free-tier API for the Mistral family (native Le Chat verdict already collected; this adds the API route).
5. **Hugging Face** (finish the PENDING TAP) → free inference quota across 84 catalog models.

## §4 — The verdict-use caveat (graded, plain)

- An answer from a model reached through OpenCode/an aggregator is the **same underlying model weights** answering — but it is **not the same program** as the consumer product of the same name. The consumer products (ChatGPT, Claude, Grok, Gemini, Perplexity…) wrap the model in their own system prompts, tools (search, memory, browsing), safety layers, and default settings. The API route strips most of that: what answers is the model plus *our* prompt, nothing else.
- **Therefore, for the scoreboard:** an API-route answer counts as a **MODEL verdict, labeled by route** — e.g. "GPT-family model, via OpenRouter — MODEL verdict (API route), not a ChatGPT product verdict." It must never be tallied as, or substituted for, the native program's answer. Where a native answer already exists (Perplexity, Gemini, ChatGPT, Copilot, DeepSeek…), the API answer is a *second, different-kind* data point, not a replacement and not a duplicate.
- **Products that are not models cannot be API'd at all:** Manus, Skywork, the legal AIs (AI.Law, ArkLegal, TheLawGPT, Jarel, GC AI), Perplexity-as-a-search-product, Poe bots. There is no underlying single model to reach; those verdicts exist only through their own front doors (or stay QUEUED, per the speed rule).
- **Free-tier honesty:** aggregator free rosters rotate and are rate-capped (OpenRouter: 50 requests/day). A full brief run (verdict + 6 follow-ups) is a multi-call session; free routes will take days per model family if pushed naively. The route is *faster to start* (no per-service signup queue) but *slower to finish* on free tiers. Both facts belong in any plan built on this inventory.
- **Terms:** OpenRouter's and Vercel's free tiers expressly permit API/programmatic use within their caps (that is what the tiers are). Poe/Together/Fireworks APIs are paid products; using a consumer chat subscription as if it were API credit would violate their terms — this inventory does not propose it.

## Sources

- OpenCode docs, "Providers" (opencode.ai/docs/providers/) — catalog source (models.dev), /connect flow, ChatGPT sign-in, Copilot device OAuth, custom-provider recipe — fetched 2026-11-16.
- models.dev catalog as cached on djdrop (`~/.cache/opencode/models.json`, Kali WSL) — 324 providers with per-provider model counts and credential env vars — read live via the djdrop SSH wrapper, read-only, 2026-11-16.
- djdrop `~/.config/opencode/opencode.jsonc` + auth store listing — read-only, 2026-11-16 (API key value redacted, never reproduced).
- OpenRouter free-tier limits — OpenRouter's published limits as tracked/verified Nov 2026 (20 RPM; 50/day; 1,000/day after $10 lifetime purchases; `:free` roster rotates).
- Vercel AI Gateway pricing (vercel.com/docs/ai-gateway/pricing, via verified summaries) — $5/mo free credit per team, free-tier-eligible model subset, zero markup.
- Requesty, "Free LLM APIs in 2026" (requesty.ai) — Requesty free models listed per model with expiry; Cerebras ~1M tokens/day; Cloudflare Workers AI free allowance.
- AI ARMY REGISTRY (Google Sheet id 1a_0FmQ5ENScrpnFhNDxn5NiQbP2vUCWvaY5B9jY39PA) via its read-back-verified snapshot `~/workspace/ai-army/registry_2026-11-16_after.json`.
