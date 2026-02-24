<p align="center">
  <img src="https://raw.githubusercontent.com/airblackbox/gateway/main/logo.png" alt="AIR Blackbox" width="120" />
</p>

<h1 align="center">AIR Blackbox</h1>
<h3 align="center">Compliance infrastructure for autonomous AI agents</h3>

<p align="center">
  <strong>EU AI Act compliant by default. Tamper-evident audit. Runtime enforcement. Every framework.</strong>
</p>

<p align="center">
  <a href="https://github.com/airblackbox"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License" /></a>
  <a href="https://github.com/airblackbox"><img src="https://img.shields.io/badge/status-alpha-orange" alt="Status" /></a>
  <a href="https://github.com/airblackbox"><img src="https://img.shields.io/badge/go-1.22+-00ADD8" alt="Go" /></a>
  <a href="https://github.com/airblackbox"><img src="https://img.shields.io/badge/python-3.10+-3776AB" alt="Python" /></a>
</p>

<p align="center">
  <a href="https://airblackbox.github.io/air-platform/hosted-demo.html"><strong>🎯 Live Demo</strong></a> · 
  <a href="https://airblackbox.github.io/air-platform/dashboard.html"><strong>📊 Dashboard</strong></a> · 
  <a href="https://airblackbox.github.io/air-platform/compare.html"><strong>🔀 Compare Runs</strong></a>
</p>

---

## Interactive Demos

Explore each core component without installing anything:

| Component | What It Shows | Try It |
|---|---|---|
| **Gateway** | OpenAI-compatible proxy that records every LLM call as an OTel trace | [Launch Demo →](https://htmlpreview.github.io/?https://github.com/airblackbox/gateway/blob/main/demo.html) |
| **Episode Store** | Groups raw traces into replayable task-level episodes | [Launch Demo →](https://htmlpreview.github.io/?https://github.com/airblackbox/agent-episode-store/blob/main/demo.html) |
| **Policy Engine** | Risk-tiered autonomy, kill switches, and trust scoring | [Launch Demo →](https://htmlpreview.github.io/?https://github.com/airblackbox/agent-policy-engine/blob/main/demo.html) |
| **Platform** | Full stack in one command — Docker Compose orchestration | [Launch Demo →](https://htmlpreview.github.io/?https://github.com/airblackbox/air-platform/blob/main/demo.html) |
| **OTel Collector** | Redaction, cost metrics, and loop detection processor | [Launch Demo →](https://htmlpreview.github.io/?https://github.com/airblackbox/otel-collector-genai/blob/main/demo.html) |
| **Hosted Demo** | Full platform walkthrough — 4 scenarios with live traces | [Launch Demo →](https://airblackbox.github.io/air-platform/hosted-demo.html) |
| **Dashboard** | Browse and inspect recorded episodes from the Episode Store | [Launch Dashboard →](https://airblackbox.github.io/air-platform/dashboard.html) |
| **Compare Runs** | Diff two agent runs side-by-side — steps, tokens, cost, policy | [Launch Compare →](https://airblackbox.github.io/air-platform/compare.html) |

---

## The Problem

The EU AI Act enforcement date for high-risk AI systems is **August 2, 2026**. Companies deploying AI agents — tool-calling LLMs that take actions autonomously — face mandatory requirements around logging, transparency, human oversight, and data governance. Penalties: up to €35M or 7% of global turnover.

Most compliance platforms target CISOs with top-down dashboards. Nobody is giving developers the building blocks to make their agents compliant by default.

## What AIR Blackbox Does

AIR Blackbox is the compliance infrastructure layer for AI agents. Drop-in SDKs that make your agent stack EU AI Act compliant — the same way Stripe made payments PCI compliant.

```
Your Agent → AIR Blackbox → Compliant, Auditable, Enforced
```

| EU AI Act Article | Requirement | AIR Feature |
|---|---|---|
| **Art. 9** | Risk management | ConsentGate — risk classification and blocking policies |
| **Art. 10** | Data governance | DataVault — PII tokenization before it reaches the LLM |
| **Art. 11** | Technical documentation | Full call graph audit logging with timestamps |
| **Art. 12** | Record-keeping | HMAC-SHA256 tamper-evident audit chain |
| **Art. 14** | Human oversight | Consent-based tool gating with exception blocking |
| **Art. 15** | Robustness & security | InjectionDetector + multi-layer defense |

See the [full compliance mapping](./docs/eu-ai-act-compliance.md) for article-by-article details.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        YOUR AI AGENTS                            │
│  (OpenAI · LangChain · CrewAI · AutoGen · Any LLM framework)   │
└─────────────────────┬───────────────────────────────────────────┘
                      │ OTLP / HTTP
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INSTRUMENTATION LAYER                       │
│                                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐│
│  │  Python SDK  │ │ Trust Plugins│ │  Framework Connectors    ││
│  │  (pip)       │ │ (4 frameworks│ │  (CrewAI, LangChain,     ││
│  │              │ │  supported)  │ │   AutoGen, OpenAI Agents)││
│  └──────────────┘ └──────────────┘ └──────────────────────────┘│
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CORE RUNTIME                               │
│                                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐│
│  │   Gateway    │ │Episode Store │ │    Policy Engine         ││
│  │  (Go proxy)  │ │ (SQLite +    │ │  (risk tiers, kill       ││
│  │              │ │  S3 vault)   │ │   switches, trust score) ││
│  └──────┬───────┘ └──────────────┘ └──────────────────────────┘│
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐│
│  │ OTel Genai   │ │  Prompt      │ │  Semantic Normalizer     ││
│  │ Processor    │ │  Vault       │ │  (gen_ai.* → standard)   ││
│  │ (redact,     │ │ (encrypted   │ │                          ││
│  │  metrics,    │ │  storage)    │ │                          ││
│  │  loop detect)│ │              │ │                          ││
│  └──────────────┘ └──────────────┘ └──────────────────────────┘│
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY BACKENDS                        │
│          Jaeger · Prometheus · Grafana · Datadog · Any OTLP     │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

**Option 1: Full stack (Docker Compose)**

```bash
git clone https://github.com/airblackbox/air-platform.git
cd air-platform
cp .env.example .env    # add your OPENAI_API_KEY
make up                 # starts Gateway + Episode Store + Policy Engine + Jaeger + Prometheus
```

**Option 2: Python SDK only**

```bash
pip install air-blackbox-sdk
```

```python
from air_blackbox import AIRBlackbox

air = AIRBlackbox()
# Wraps your OpenAI client with automatic tracing
client = air.wrap(openai.OpenAI())
```

**Option 3: OTel Collector processor (no code changes)**

Add to your existing `otelcol-config.yaml`:

```yaml
processors:
  genaisafe:
    redact:
      mode: hash_and_preview
      preview_chars: 48
    metrics:
      enable: true
    loop_detection:
      enable: true
      repeat_threshold: 6
```

## Components

### Core Runtime

| Repository | Description | Demo |
|---|---|---|
| [**gateway**](https://github.com/airblackbox/gateway) | OpenAI-compatible reverse proxy — records every LLM call as an OpenTelemetry trace | [View Demo](https://htmlpreview.github.io/?https://github.com/airblackbox/gateway/blob/main/demo.html) |
| [**agent-episode-store**](https://github.com/airblackbox/agent-episode-store) | Groups raw traces into replayable task-level episodes (SQLite + S3) | [View Demo](https://htmlpreview.github.io/?https://github.com/airblackbox/agent-episode-store/blob/main/demo.html) |
| [**agent-policy-engine**](https://github.com/airblackbox/agent-policy-engine) | Risk-tiered autonomy, kill switches, and trust scoring | [View Demo](https://htmlpreview.github.io/?https://github.com/airblackbox/agent-policy-engine/blob/main/demo.html) |
| [**air-platform**](https://github.com/airblackbox/air-platform) | Docker Compose orchestration — one command to run the full stack | [View Demo](https://htmlpreview.github.io/?https://github.com/airblackbox/air-platform/blob/main/demo.html) |

### Instrumentation

| Repository | Description |
|---|---|
| [**python-sdk**](https://github.com/airblackbox/python-sdk) | Python SDK — wraps OpenAI, Anthropic, and other LLM clients |
| [**trust-crewai**](https://github.com/airblackbox/trust-crewai) | Trust plugin for CrewAI multi-agent framework |
| [**trust-langchain**](https://github.com/airblackbox/trust-langchain) | Trust plugin for LangChain / LangGraph |
| [**trust-autogen**](https://github.com/airblackbox/trust-autogen) | Trust plugin for Microsoft AutoGen |
| [**trust-openai-agents**](https://github.com/airblackbox/trust-openai-agents) | Trust plugin for OpenAI Agents SDK |

### Safety & Governance

| Repository | Description | Demo |
|---|---|---|
| [**otel-collector-genai**](https://github.com/airblackbox/otel-collector-genai) | OTel Collector processor — redaction, cost metrics, loop detection | [View Demo](https://htmlpreview.github.io/?https://github.com/airblackbox/otel-collector-genai/blob/main/demo.html) |
| [**otel-prompt-vault**](https://github.com/airblackbox/otel-prompt-vault) | Encrypted prompt/completion storage with pre-signed URL retrieval | — |
| [**otel-semantic-normalizer**](https://github.com/airblackbox/otel-semantic-normalizer) | Normalizes gen_ai.* and llm.* attributes to a standard schema | — |
| [**agent-tool-sandbox**](https://github.com/airblackbox/agent-tool-sandbox) | Sandboxed execution environment for agent tool calls | — |
| [**runtime-aibom-emitter**](https://github.com/airblackbox/runtime-aibom-emitter) | Generates AI Bill of Materials at runtime | — |

#**Compliance**
| Component | What It Does |
|---|---|
| [air-compliance](https://github.com/airblackbox/air-compliance-checker) | CLI scanner — checks your project for EU AI Act compliance coverage |

## Evaluation & Testing

| Repository | Description |
|---|---|
| [**eval-harness**](https://github.com/airblackbox/eval-harness) | CLI tool for replaying and scoring episodes against policies |
| [**trace-regression-harness**](https://github.com/airblackbox/trace-regression-harness) | Detects behavioral regressions across agent versions |
| [**agent-vcr**](https://github.com/airblackbox/agent-vcr) | Record and replay agent interactions for deterministic testing |

### Security

| Repository | Description |
|---|---|
| [**mcp-security-scanner**](https://github.com/airblackbox/mcp-security-scanner) | Scans MCP server configurations for security vulnerabilities |
| [**mcp-policy-gateway**](https://github.com/airblackbox/mcp-policy-gateway) | Policy enforcement gateway for Model Context Protocol |

## Why Infrastructure-Level Compliance?

Most teams try to add compliance at the application level — inside each agent, each framework, each service. This approach fails because:

- Every team re-invents audit logging differently (and none are tamper-evident)
- PII leaks through cracks between implementations
- No single chain of custody across framework boundaries
- When regulators ask "prove it" — nobody has mathematically verifiable logs

AIR Blackbox operates at the **infrastructure level** — as framework-native SDKs, an OTel Collector processor, a reverse proxy, and a policy engine. Three lines of code activates compliance across your entire agent stack.

## Threat Model

AIR Blackbox addresses four attack vectors in GenAI observability:

| Threat | Risk | Mitigation |
|---|---|---|
| **Prompt Data Leakage** | PII, proprietary data exposed in traces | SHA-256 redaction with configurable preview |
| **Secret Exposure** | API keys, bearer tokens in span attributes | Denylist regex patterns, automatic detection |
| **Runaway Loops** | Infinite tool-calling burning budget | Repeat threshold detection, span flagging |
| **Cost Blind Spots** | No normalized token/cost visibility | Unified metrics extraction from any format |

## License

All AIR Blackbox components are released under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.


---

## Support the Project

If AIR Blackbox is useful to you, a star helps others find it.

[![Star on GitHub](https://img.shields.io/github/stars/airblackbox/air-platform?style=social)](https://github.com/airblackbox/air-platform)

Questions or feedback? Start a [Discussion](https://github.com/airblackbox/air-platform/discussions).

---

<p align="center">
  <strong>AIR Blackbox</strong> — Agent Infrastructure Runtime<br/>
  Compliance infrastructure for autonomous AI agents
</p>
