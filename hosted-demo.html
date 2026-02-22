<p align="center">
  <img src="https://raw.githubusercontent.com/airblackbox/gateway/main/logo.png" alt="AIR Blackbox" width="100" />
</p>

<h1 align="center">AIR Blackbox</h1>

<h3 align="center">Open-source infrastructure for safe deployment of autonomous AI agents.</h3>

<p align="center">
  <em>The flight recorder for AI — record every decision, replay every incident, enforce every policy.</em>
</p>

<p align="center">
  <a href="https://github.com/airblackbox/air-platform"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License" /></a>
  <a href="https://github.com/airblackbox/air-platform"><img src="https://img.shields.io/badge/status-alpha-orange" alt="Status" /></a>
  <a href="https://github.com/airblackbox/air-platform"><img src="https://img.shields.io/badge/OTel-native-4B0082" alt="OTel" /></a>
</p>

---

## The Problem

AI agents are making real decisions — calling APIs, executing code, moving money, accessing databases. But there is no standard infrastructure for:

- **Auditing** what an agent actually did
- **Enforcing** policies before an action executes
- **Shutting down** a runaway agent in real time
- **Replaying** an incident after something goes wrong
- **Redacting** secrets before they hit your logging stack

Every team re-invents this differently. Secrets leak. Budgets burn. Regulators ask questions nobody can answer.

**AIR Blackbox is the missing layer between your AI agents and your infrastructure.**

---

## How It Works

```
Your Agent ──→ Gateway ──→ Policy Engine ──→ LLM Provider
                 │               │
                 ▼               ▼
           OTel Collector   Kill Switches
                 │          Trust Scoring
                 ▼          Risk Tiers
           Episode Store
           Jaeger · Prometheus
```

One line change — swap your `base_url` — and every agent call flows through AIR Blackbox automatically. No SDK changes, no code refactoring.

---

## 5-Minute Quickstart

```bash
git clone https://github.com/airblackbox/air-platform.git && cd air-platform
cp .env.example .env          # add your OPENAI_API_KEY
make up                       # 6 services running in ~8 seconds
```

Then point any OpenAI-compatible client at `localhost:8080`. That's it.

- **Traces** → `localhost:16686` (Jaeger)
- **Metrics** → `localhost:9091` (Prometheus)
- **Episodes** → `localhost:8081` (Episode Store API)

---

## Interactive Demos

Explore each component without installing anything:

| Component | Try It |
|---|---|
| **Platform Orchestration** | [Launch Demo →](https://htmlpreview.github.io/?https://github.com/airblackbox/air-platform/blob/main/demo.html) |
| **Policy Engine** | [Launch Demo →](https://htmlpreview.github.io/?https://github.com/airblackbox/agent-policy-engine/blob/main/demo.html) |
| **Episode Store** | [Launch Demo →](https://htmlpreview.github.io/?https://github.com/airblackbox/agent-episode-store/blob/main/demo.html) |
| **Gateway** | [Launch Demo →](https://htmlpreview.github.io/?https://github.com/airblackbox/gateway/blob/main/demo.html) |
| **OTel Collector** | [Launch Demo →](https://htmlpreview.github.io/?https://github.com/airblackbox/otel-collector-genai/blob/main/demo.html) |

---

## Repositories

### Core Runtime

| Repo | What It Does |
|---|---|
| [**air-platform**](https://github.com/airblackbox/air-platform) | Full stack in one command — Docker Compose orchestration |
| [**gateway**](https://github.com/airblackbox/gateway) | OpenAI-compatible reverse proxy — traces every LLM call |
| [**agent-episode-store**](https://github.com/airblackbox/agent-episode-store) | Groups traces into replayable task-level episodes |
| [**agent-policy-engine**](https://github.com/airblackbox/agent-policy-engine) | Risk tiers, kill switches, trust scoring |

### Safety & Governance

| Repo | What It Does |
|---|---|
| [**otel-collector-genai**](https://github.com/airblackbox/otel-collector-genai) | PII redaction, cost metrics, loop detection |
| [**otel-prompt-vault**](https://github.com/airblackbox/otel-prompt-vault) | Encrypted prompt storage with pre-signed URL retrieval |
| [**otel-semantic-normalizer**](https://github.com/airblackbox/otel-semantic-normalizer) | Normalizes gen_ai.* attributes to a standard schema |
| [**agent-tool-sandbox**](https://github.com/airblackbox/agent-tool-sandbox) | Sandboxed execution for agent tool calls |
| [**runtime-aibom-emitter**](https://github.com/airblackbox/runtime-aibom-emitter) | AI Bill of Materials generation at runtime |

### Instrumentation

| Repo | What It Does |
|---|---|
| [**python-sdk**](https://github.com/airblackbox/python-sdk) | Python SDK — wraps OpenAI, Anthropic, and other LLM clients |
| [**trust-crewai**](https://github.com/airblackbox/trust-crewai) | Trust plugin for CrewAI |
| [**trust-langchain**](https://github.com/airblackbox/trust-langchain) | Trust plugin for LangChain / LangGraph |
| [**trust-autogen**](https://github.com/airblackbox/trust-autogen) | Trust plugin for Microsoft AutoGen |
| [**trust-openai-agents**](https://github.com/airblackbox/trust-openai-agents) | Trust plugin for OpenAI Agents SDK |

### Evaluation & Security

| Repo | What It Does |
|---|---|
| [**eval-harness**](https://github.com/airblackbox/eval-harness) | Replay and score episodes against policies |
| [**trace-regression-harness**](https://github.com/airblackbox/trace-regression-harness) | Detect behavioral regressions across agent versions |
| [**agent-vcr**](https://github.com/airblackbox/agent-vcr) | Record and replay agent interactions for testing |
| [**mcp-security-scanner**](https://github.com/airblackbox/mcp-security-scanner) | Scan MCP server configs for vulnerabilities |
| [**mcp-policy-gateway**](https://github.com/airblackbox/mcp-policy-gateway) | Policy enforcement for Model Context Protocol |

---

## Why Infrastructure-Level?

The same reason you don't implement TLS differently in every microservice.

Agent safety needs to be a **standardized layer**, not something each team builds ad hoc. AIR Blackbox operates in the OTel pipeline, as a reverse proxy, and as a policy engine — so it works across any framework, any model, any deployment.

---

## Contributing

We're looking for contributors interested in AI safety, observability, and governance. See our [Contributing Guide](https://github.com/airblackbox/air-platform/blob/main/CONTRIBUTING.md) to get started.

**Current priorities:**
- New framework connectors (Haystack, DSPy, Semantic Kernel)
- Policy templates for common compliance scenarios
- Documentation and integration examples

---

<p align="center">
  <strong>Apache 2.0</strong> · Built on <strong>OpenTelemetry</strong> · 21 repositories
</p>