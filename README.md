<p align="center">
  <img src="https://raw.githubusercontent.com/airblackbox/gateway/main/logo.png" alt="AIR Blackbox" width="120" />
</p>

<h1 align="center">AIR Blackbox</h1>
<h3 align="center">The flight recorder for autonomous AI agents</h3>

<p align="center">
  <strong>Record every decision. Replay every incident. Enforce every policy.</strong>
</p>

<p align="center">
  <a href="https://github.com/airblackbox"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License" /></a>
  <a href="https://github.com/airblackbox"><img src="https://img.shields.io/badge/status-alpha-orange" alt="Status" /></a>
  <a href="https://github.com/airblackbox"><img src="https://img.shields.io/badge/go-1.22+-00ADD8" alt="Go" /></a>
  <a href="https://github.com/airblackbox"><img src="https://img.shields.io/badge/python-3.10+-3776AB" alt="Python" /></a>
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

---

## The Problem

AI agents are making real decisions — calling APIs, executing code, moving money, accessing databases. But when something goes wrong, teams cannot reconstruct what happened or why.

There is no audit trail. No replay capability. No policy enforcement layer.

Every team re-invents logging. Secrets leak into trace backends. Runaway agents burn through budgets undetected. And when regulators ask "what did your AI do? — nobody has a good answer.

## What AIR Blackbox Does

AIR Blackbox is the missing infrastructure layer between your AI agents and your observability stack.

```
Your Agent → AIR Blackbox → Safe, Auditable Telemetry
```

It provides four capabilities:

| Capability | What it does |
|---|---|
| **Record** | Captures every LLM call, tool invocation, and decision as a structured trace |
| **Replay** | Groups traces into task-level episodes that can be replayed and investigated |
| **Enforce** | Applies risk-tiered policies, kill switches, and trust scoring in real time |
| **Audit** | Redacts secrets, normalizes metrics, and produces compliance-ready telemetry |

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

### Evaluation & Testing

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

## Why Collector-Side?

Most teams try to add safety at the application level — inside each agent, each framework, each service. This approach fails because:

- Every team re-invents redaction differently
- Secrets leak through cracks between implementations
- Token/cost metrics are scattered and inconsistent
- Runaway agents are caught too late (or never)

AIR Blackbox operates at the **infrastructure level** — in the OTel Collector pipeline, as a reverse proxy, and as a policy engine. One configuration change protects all services. No application code changes required.

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

<p align="center">
  <strong>AIR Blackbox</strong> — Agent Infrastructure Runtime<br/>
  The observability security layer for autonomous AI systems
</p>
