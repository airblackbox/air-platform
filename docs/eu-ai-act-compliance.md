# AIR Blackbox — EU AI Act Compliance Mapping

## The Problem

The EU AI Act enters enforcement for **high-risk AI systems on August 2, 2026**. Companies deploying AI agents — tool-calling LLMs that take actions autonomously — face mandatory requirements around logging, transparency, human oversight, and data governance.

Most compliance platforms target CISOs with top-down dashboards. **Nobody is giving developers the building blocks to make their agents compliant by default.**

> **Note**: The European Commission's Digital Omnibus proposal (late 2025) could postpone Annex III high-risk obligations to December 2027, but formal adoption is pending. Prudent compliance planning treats August 2, 2026 as the binding deadline. Penalties: up to €35M or 7% of worldwide turnover for prohibited practices, up to €15M or 3% for other infringements.

AIR Blackbox is the compliance infrastructure layer for AI agents. Drop-in SDKs that make your agent stack EU AI Act compliant — the same way Stripe made payments PCI compliant.

---

## Compliance Matrix

### Article 9 — Risk Management System

> *High-risk AI systems shall have a risk management system established, implemented, documented and maintained.*

| Requirement | AIR Blackbox Feature | Component |
|---|---|---|
| Identify and analyze known/foreseeable risks | **ConsentGate** — classifies every tool call by risk level (LOW / MEDIUM / HIGH / CRITICAL) | `air-crewai-trust`, `air-langchain-trust` |
| Estimate and evaluate risks from intended use | **Tool risk registry** — configurable risk levels per tool, per deployment | `AirTrustConfig.tool_risk_levels` |
| Adopt suitable risk management measures | **Blocking policies** — BLOCK_ALL, BLOCK_CRITICAL, BLOCK_HIGH_AND_CRITICAL consent modes | `ConsentGate.intercept()` |
| Residual risk below acceptable level | **Audit trail** proves risk decisions were made and enforced at runtime | `AuditLedger` |

### Article 10 — Data and Data Governance

> *High-risk AI systems which make use of techniques involving the training of AI models with data shall be developed on the basis of training, validation and testing data sets that meet quality criteria.*

| Requirement | AIR Blackbox Feature | Component |
|---|---|---|
| Data governance and management practices | **DataVault** — tokenizes PII before it enters the LLM pipeline | `DataVault.tokenize()` |
| Examination for possible biases | **Audit logs capture every prompt and response** — enables post-hoc bias analysis | `AuditLedger` |
| Appropriate data minimization measures | **PII stripping** — SSNs, credit cards, emails, API keys, phone numbers automatically redacted | `DataVault` default patterns |
| Data sets shall be relevant, sufficiently representative | **Prompt logging** captures what data the agent actually sees at inference time | `on_llm_start` audit entries |

### Article 11 — Technical Documentation

> *Technical documentation shall be drawn up before the AI system is placed on the market and shall be kept up to date.*

| Requirement | AIR Blackbox Feature | Component |
|---|---|---|
| General description of the AI system | **Structured audit log** — every chain, tool call, and LLM invocation documented with timestamps | `AuditLedger.get_entries()` |
| Detailed description of system elements | **Full call graph capture** — chain_start → llm_call → tool_call → tool_result → chain_end | `AirTrustCallbackHandler` |
| Information about training data | **Prompt content logging** — what the model saw, tokenized for privacy | `on_llm_start` entries |
| Monitoring, functioning, control of the AI system | **HMAC-SHA256 tamper-evident chain** — proves logs haven't been altered after the fact | `AuditLedger.verify_chain()` |

### Article 12 — Record-Keeping

> *High-risk AI systems shall technically allow for the automatic recording of events (logs) over the lifetime of the system.*

| Requirement | AIR Blackbox Feature | Component |
|---|---|---|
| Recording of the period of each use | **Timestamped entries** for every operation (ISO 8601) | `AuditLedger.append()` |
| Reference database against which input data is checked | **Consent decisions logged** with tool name, risk level, allow/deny reason | `consent_denied` / `tool_call` entries |
| Input data for which the search has led to a match | **Injection detection results logged** with pattern name and matched text | `injection_blocked` entries |
| Identification of natural persons involved in verification | **Run ID tracking** — every entry linked to the specific agent run | `run_id` in all entries |

**Key differentiator**: AIR Blackbox logs are **tamper-evident** via HMAC-SHA256 chaining. Each log entry's hash includes the previous entry's hash. Break the chain = detectable. This is the Article 12 killer feature — regulators need to trust that logs weren't modified after a compliance incident.

### Article 14 — Human Oversight

> *High-risk AI systems shall be designed and developed in such a way that they can be effectively overseen by natural persons.*

| Requirement | AIR Blackbox Feature | Component |
|---|---|---|
| Enabling the individuals to fully understand the AI system | **Complete audit trail** — humans can review exactly what the agent did and why | `AuditLedger` |
| Enabling the individuals to correctly interpret the output | **Tokenized logging** — sensitive data masked, but decision flow visible | `DataVault` + `AuditLedger` |
| Ability to decide not to use or override the AI system | **Consent gate** — humans define which tools the agent can use and at what risk level | `ConsentGate` |
| Ability to intervene or interrupt the system | **Exception-based blocking** — ConsentDeniedError / InjectionBlockedError halt execution immediately | `errors.py` |

### Article 15 — Accuracy, Robustness, Cybersecurity

> *High-risk AI systems shall be designed and developed in such a way that they achieve an appropriate level of accuracy, robustness and cybersecurity.*

| Requirement | AIR Blackbox Feature | Component |
|---|---|---|
| Resilient against unauthorized third-party attempts to alter use or performance | **InjectionDetector** — scans all prompts for injection attacks before they reach the model | `InjectionDetector.scan()` |
| Technically redundant solutions for safety | **Multi-layer defense** — injection detection + consent gating + PII vault + audit logging all independent | Full trust stack |
| Cybersecurity measures proportionate to risks | **Configurable per deployment** — adjust patterns, risk levels, blocking modes to match your threat model | `AirTrustConfig` |
| AI system resilient against attempts to manipulate | **7 default injection patterns** — instruction override, jailbreak, authority impersonation, system prompt injection | `InjectionDetector` defaults |

---

## Framework Coverage

| Framework | Package | Status |
|---|---|---|
| **LangChain / LangGraph** | `air-langchain-trust` | Published on PyPI |
| **CrewAI** | `air-crewai-trust` | Published on PyPI |
| **OpenTelemetry** | `otel-semantic-normalizer` | Processor built, OTel Contrib proposal pending |
| **Any HTTP-based agent** | `gateway` | Docker image on ghcr.io |
| **TypeScript / Node.js** | `openclaw-air-trust` | Published on npm |

---

## Competitive Landscape

| Vendor | Approach | Gap |
|---|---|---|
| **Credo AI** | Top-down governance platform for CISOs | No developer SDK, no runtime enforcement |
| **Holistic AI** | Risk assessment and audit tooling | Assessment-only, no runtime blocking |
| **Zenity** | AI agent security platform | Closed-source, enterprise-only, no open-source path |
| **Patronus AI** | LLM evaluation and guardrails | Eval-focused, no consent/audit chain |
| **AIR Blackbox** | **Developer-first compliance SDK** | **Runtime enforcement + tamper-evident audit + open source + multi-framework** |

---

## The Moat

1. **Framework-native integration** — not a proxy, not a wrapper. Sits inside LangChain callbacks, CrewAI hooks, OTel pipelines. Zero-latency compliance.

2. **Tamper-evident audit chain** — HMAC-SHA256 linked entries. The only open-source solution that produces logs a regulator can mathematically verify haven't been altered.

3. **Multi-framework from day one** — LangChain, CrewAI, OTel, TypeScript, HTTP gateway. Competitors lock you into one ecosystem.

4. **Open source wedge** — MIT/Apache-2.0 licensed core. Developers adopt freely, then enterprises need the managed platform for SOC 2, audit exports, and compliance dashboards.

5. **August 2, 2026 deadline** — 5 months away. Every company deploying high-risk AI agents needs to be compliant. The infrastructure layer they need doesn't exist yet. We're building it.

---

## Quick Start

```python
# LangChain — 3 lines to EU AI Act compliance
from air_langchain_trust import AirTrustCallbackHandler

handler = AirTrustCallbackHandler()
chain.invoke(input, config={"callbacks": [handler]})
# That's it. Audit logging, PII protection, consent gating, injection detection — all active.
```

```python
# CrewAI — same simplicity
from air_crewai_trust import AirTrustHook

hook = AirTrustHook()
crew = Crew(agents=[...], tasks=[...], trust_hook=hook)
```