# AIR Blackbox — EU AI Act Compliance Mapping

## The Problem

The EU AI Act enters enforcement for **high-risk AI systems on August 2, 2026**. Companies deploying AI agents — tool-calling LLMs that take actions autonomously — face mandatory requirements around logging, transparency, human oversight, and data governance.

Most compliance platforms target CISOs with top-down dashboards. **Nobody is giving developers the building blocks to make their agents audit-ready by default.**

> **Note**: The European Commission's Digital Omnibus proposal (late 2025) could postpone Annex III high-risk obligations to December 2027, but formal adoption is pending. Prudent compliance planning treats August 2, 2026 as the binding deadline. Penalties: up to €35M or 7% of worldwide turnover for prohibited practices, up to €15M or 3% for other infringements.

AIR Blackbox is the compliance infrastructure layer for AI agents: a gateway proxy, audit chain, scanner, and framework trust layers that produce the technical evidence the Act requires. It checks technical requirements — it is a linter for AI governance, not a legal tool.

---

## Compliance Matrix

### Article 9 — Risk Management System

> *High-risk AI systems shall have a risk management system established, implemented, documented and maintained.*

| Requirement | AIR Blackbox Feature | Component |
|---|---|---|
| Identify and analyze known/foreseeable risks | **Guardrails** — session budgets, loop detection, retry protection, tool allow/blocklists enforced at the proxy | Gateway (`guardrails.yaml`) |
| Estimate and evaluate risks from intended use | **Risk-tiered tool policies** — every tool call classified and checked before execution | [air-gate](https://github.com/airblackbox/air-gate) policy engine |
| Adopt suitable risk management measures | **Runtime blocking** — prevention layer returns 403, detection layer returns 429 instead of forwarding to the LLM | Gateway prevention/detection |
| Residual risk below acceptable level | **Audit chain** proves risk decisions were made and enforced at runtime | Gateway `.air.json` records |

### Article 10 — Data and Data Governance

> *High-risk AI systems which make use of techniques involving the training of AI models with data shall be developed on the basis of training, validation and testing data sets that meet quality criteria.*

| Requirement | AIR Blackbox Feature | Component |
|---|---|---|
| Data governance and management practices | **Prompt vault** — prompt/response bodies offloaded to encrypted storage, replaced with refs in traces | Collector `promptvault` processor |
| Examination for possible biases | **Full capture of every prompt and response** — enables post-hoc bias analysis | Audit chain + prompt vault |
| Appropriate data minimization measures | **PII redaction** — hash-and-preview redaction with denylist patterns (API keys, auth headers, secrets) | Collector `genaisafe` processor |
| Data sets shall be relevant, sufficiently representative | **Trace-level visibility** into what data the agent actually sees at inference time | OTel traces (`gen_ai.*` semconv) |

### Article 11 — Technical Documentation

> *Technical documentation shall be drawn up before the AI system is placed on the market and shall be kept up to date.*

| Requirement | AIR Blackbox Feature | Component |
|---|---|---|
| General description of the AI system | **Live model/provider inventory** — `air-blackbox discover` from observed gateway traffic | `air-blackbox` CLI |
| Detailed description of system elements | **Full call graph** — every LLM call recorded as a normalized OTel trace | Gateway + collector |
| Information about training data | **Gap analysis** — 51+ checks across Articles 9–15, mapped to ISO 42001, NIST AI RMF, Colorado SB 24-205 | `air-blackbox comply --scan` |
| Monitoring, functioning, control of the AI system | **Tamper-evident chain** — proves records haven't been altered after the fact | HMAC-SHA256 chain verification |

### Article 12 — Record-Keeping

> *High-risk AI systems shall technically allow for the automatic recording of events (logs) over the lifetime of the system.*

| Requirement | AIR Blackbox Feature | Component |
|---|---|---|
| Recording of the period of each use | **Timestamped `.air.json` records** for every proxied call, written asynchronously | Gateway recorder |
| Automatic recording over the system lifetime | **Zero-code capture** — one base_url swap, every call recorded | Gateway proxy |
| Logs available for audit | **Evidence bundles** — self-verifying `.air-evidence` ZIP; auditors run `python verify.py`, no pip install needed | `air-blackbox evidence` |
| Integrity of recorded events | **HMAC-SHA256 chain + ML-DSA-65 (FIPS 204) signed checkpoints** — post-quantum secure, Rekor transparency-log anchoring | Gateway trust layer |

**Key differentiator**: AIR Blackbox records are **tamper-evident**. Each record's hash includes the previous record's hash — modify one record and every record after it breaks. Checkpoints are signed with ML-DSA-65 and anchored to a public transparency log. Regulators can mathematically verify the logs weren't modified after an incident.

### Article 14 — Human Oversight

> *High-risk AI systems shall be designed and developed in such a way that they can be effectively overseen by natural persons.*

| Requirement | AIR Blackbox Feature | Component |
|---|---|---|
| Enabling the individuals to fully understand the AI system | **Episode replay** — load any past episode, verify its signature, replay every step with timestamps | `air-blackbox replay` |
| Enabling the individuals to correctly interpret the output | **Redacted-but-visible decision flow** — sensitive content masked, structure preserved | Collector pipeline |
| Ability to decide not to use or override the AI system | **Human-in-the-loop tool gating** — risky actions pause and wait for a human decision (Slack or HTTP API) | [air-gate](https://github.com/airblackbox/air-gate) |
| Ability to intervene or interrupt the system | **Kill switches** — spend/loop thresholds halt the session; guardrail triggers terminate and save a replay | Gateway guardrails + air-gate |

### Article 15 — Accuracy, Robustness, Cybersecurity

> *High-risk AI systems shall be designed and developed in such a way that they achieve an appropriate level of accuracy, robustness and cybersecurity.*

| Requirement | AIR Blackbox Feature | Component |
|---|---|---|
| Resilient against unauthorized third-party attempts to alter use or performance | **Injection detection** — 20 weighted patterns across 5 attack categories, scanned before the prompt reaches the model | Gateway injection scanner |
| Technically redundant solutions for safety | **Multi-layer defense** — injection detection, guardrails, PII redaction, and audit chain operate independently | Full stack |
| Cybersecurity measures proportionate to risks | **Configurable sensitivity** — patterns, thresholds, and blocking modes tuned per deployment | `guardrails.yaml` |
| AI system resilient against attempts to manipulate | **Auto-blocking** — detected injections return a structured error instead of reaching the LLM | Gateway prevention layer |

---

## Framework Coverage

All trust layers ship inside the main [`air-blackbox`](https://pypi.org/project/air-blackbox/) package (`air_blackbox.trust.*`):

| Framework | Integration |
|---|---|
| **LangChain / LangGraph** | `AirTrust().attach(chain)` or `AirLangChainHandler` callback |
| **CrewAI** | `air_blackbox.trust.crewai` |
| **AutoGen** | `air_blackbox.trust.autogen` |
| **OpenAI Agents SDK** | `air_blackbox.trust.openai_agents` |
| **Claude Agent SDK** | `air_blackbox.trust.claude_agent` |
| **Google ADK** | `air_blackbox.trust.adk` |
| **Haystack** | `air_blackbox.trust.haystack` |
| **Any HTTP-based agent** | Gateway proxy — `ghcr.io/airblackbox/airblackbox` |
| **MCP-compatible IDEs/agents** | [air-blackbox-mcp](https://github.com/airblackbox/air-blackbox-mcp) |

---

## Competitive Landscape

| Vendor | Approach | Gap |
|---|---|---|
| **Credo AI** | Top-down governance platform for CISOs | No developer SDK, no runtime enforcement |
| **Holistic AI** | Risk assessment and audit tooling | Assessment-only, no runtime blocking |
| **Zenity** | AI agent security platform | Closed-source, enterprise-only, no open-source path |
| **Patronus AI** | LLM evaluation and guardrails | Eval-focused, no consent/audit chain |
| **AIR Blackbox** | **Developer-first compliance infrastructure** | **Runtime enforcement + tamper-evident audit + open source + every major framework** |

---

## The Moat

1. **One proxy swap** — not weeks of SDK integration. Change `base_url`, done. ~3 ms measured overhead per call.

2. **Tamper-evident audit chain** — HMAC-SHA256 linked records with ML-DSA-65 signed checkpoints anchored to a public transparency log. The only open-source solution producing logs a regulator can mathematically verify.

3. **Local-first** — keys generated locally, records stay on your infrastructure, default collector pipeline exports to your own Jaeger only. Enterprise competitors require sending data to their cloud.

4. **Multi-framework from day one** — seven framework trust layers, an OTel processor pipeline, an HTTP gateway, and an MCP server. Competitors lock you into one ecosystem.

5. **August 2, 2026 deadline** — weeks away. Every company deploying high-risk AI agents needs technical evidence. The infrastructure layer they need is here.

---

## Quick Start

```python
# Gateway — one line to full audit coverage
client = OpenAI(base_url="http://localhost:8080/v1")
```

```bash
# Gap analysis on any Python AI project
pip install air-blackbox
air-blackbox comply --scan . -v
```

```python
# LangChain trust layer — native integration, same audit chain
from air_blackbox import AirTrust

trust = AirTrust()
trust.attach(your_chain)  # auto-detects LangChain
```
