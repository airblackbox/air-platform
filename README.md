<p align="center">
  <img src="https://avatars.githubusercontent.com/u/262437398?v=4" alt="AIR Blackbox" width="120" />
</p>

<h1 align="center">AIR Platform</h1>
<h3 align="center">One command to run the AIR Blackbox compliance stack</h3>

<p align="center">
  <strong>Tamper-evident audit. Runtime guardrails. Full trace observability. Local-first.</strong>
</p>

<p align="center">
  <img src="demo.gif" alt="AIR Blackbox Platform demo" width="900">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License" /></a>
  <a href="https://github.com/airblackbox/air-platform/actions"><img src="https://img.shields.io/github/actions/workflow/status/airblackbox/air-platform/ci.yml?branch=main" alt="CI" /></a>
  <a href="https://pypi.org/project/air-blackbox/"><img src="https://img.shields.io/pypi/v/air-blackbox?label=air-blackbox" alt="air-blackbox on PyPI" /></a>
  <a href="https://pypi.org/project/air-gate/"><img src="https://img.shields.io/pypi/v/air-gate?label=air-gate" alt="air-gate on PyPI" /></a>
</p>

<p align="center">
  <a href="https://airblackbox.github.io/air-platform/hosted-demo.html"><strong>🎯 Live Demo</strong></a> ·
  <a href="https://airblackbox.ai"><strong>🌐 airblackbox.ai</strong></a> ·
  <a href="https://github.com/airblackbox/airblackbox"><strong>📦 Main Repo</strong></a>
</p>

---

## What This Is

`air-platform` is the Docker Compose orchestration for the [AIR Blackbox](https://github.com/airblackbox/airblackbox) stack. One command starts the gateway, the GenAI-aware OTel collector, Jaeger tracing, and a MinIO prompt vault — a self-contained, local sandbox for recording, replaying, and auditing AI agent behavior.

The gateway ships as a prebuilt, signed image from GHCR (with SLSA build provenance). Nothing here phones home: the default collector pipeline exports to your local Jaeger only.

## The Problem

The EU AI Act enforcement date for high-risk AI systems is **August 2, 2026**. Companies deploying AI agents — tool-calling LLMs that act autonomously — face mandatory requirements around logging, transparency, human oversight, and data governance. Penalties reach €35M or 7% of global turnover.

Most compliance platforms target CISOs with top-down dashboards. AIR Blackbox gives developers the building blocks to make agents audit-ready by default.

## Quick Start

```bash
git clone https://github.com/airblackbox/air-platform.git
cd air-platform
cp .env.example .env    # optional: set OPENAI_API_KEY, GATEWAY_KEY
make up                 # gateway + collector + Jaeger + MinIO
make status             # check health
```

Point your agent at the gateway instead of the provider — everything else in your code stays identical:

```python
client = OpenAI(base_url="http://localhost:8080/v1")
```

Every LLM call now produces an HMAC-SHA256 chained, replayable audit record in `./runs/`, plus an OpenTelemetry trace you can inspect in Jaeger at [localhost:16686](http://localhost:16686).

**Ports**

| Port | Service |
|---|---|
| 8080 | AIR Gateway — OpenAI-compatible proxy (`/v1/chat/completions`, `/v1/responses`, `/v1/audit`, `/v1/analytics`, `/health`) |
| 4317 / 4318 | OTel Collector (gRPC / HTTP OTLP) |
| 16686 | Jaeger UI |
| 9000 / 9001 | MinIO S3 API / Console (prompt vault) |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       YOUR AI AGENTS                         │
│   (OpenAI SDK · LangChain · CrewAI · AutoGen · any client)  │
└──────────────────────────┬──────────────────────────────────┘
                           │ base_url swap
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    AIR GATEWAY  :8080                        │
│   OpenAI-compatible proxy · HMAC-SHA256 audit chain          │
│   guardrails (budgets, loop & retry protection, tool         │
│   allowlists) · PII / injection scanning · replay records    │
└───────┬──────────────────────────────┬──────────────────────┘
        │ OTLP traces                  │ .air.json records
        ▼                              ▼
┌───────────────────────────┐   ┌─────────────────────────────┐
│   OTEL COLLECTOR :4317    │   │   ./runs/  +  MinIO vault   │
│   normalize → prompt      │   │   (signed, replayable,      │
│   vault → redact/metrics  │   │    tamper-evident)          │
└───────────┬───────────────┘   └─────────────────────────────┘
            ▼
┌───────────────────────────┐
│      JAEGER UI :16686     │
└───────────────────────────┘
```

The collector pipeline (`collector.yaml`, editable) runs three AIR processors in order: **genai_semantic_normalizer** (vendor attrs → `gen_ai.*` conventions), **promptvault** (offload prompt/response bodies to encrypted storage, replace with refs), and **genaisafe** (PII redaction, token metrics, loop detection).

## EU AI Act Mapping

| EU AI Act Article | Requirement | Where it's handled |
|---|---|---|
| **Art. 9** | Risk management | Gateway guardrails — budgets, loop/retry protection, tool blocklists; [air-gate](https://github.com/airblackbox/air-gate) risk-tiered approval policies |
| **Art. 10** | Data governance | Collector `genaisafe` PII redaction + prompt vault offload |
| **Art. 11** | Technical documentation | Full OTel trace of every call, normalized to `gen_ai.*` semantics |
| **Art. 12** | Record-keeping | HMAC-SHA256 chained `.air.json` records, ML-DSA-65 signed checkpoints |
| **Art. 14** | Human oversight | [air-gate](https://github.com/airblackbox/air-gate) — human-in-the-loop tool gating with Slack approvals |
| **Art. 15** | Robustness & security | Injection detection (20 weighted patterns, 5 attack categories), guardrail enforcement |

See the [full compliance mapping](./docs/eu-ai-act-compliance.md) for article-by-article details. AIR Blackbox checks technical requirements — it is a linter for AI governance, not a legal tool.

## The AIR Blackbox Ecosystem

| Repository | What it does | Install |
|---|---|---|
| [**airblackbox**](https://github.com/airblackbox/airblackbox) | The flight recorder: gateway proxy, audit chain, replay, evidence bundles, EU AI Act gap analysis (51+ checks), framework trust layers | `pip install air-blackbox` |
| [**air-gate**](https://github.com/airblackbox/air-gate) | Human-in-the-loop tool gating + policy engine (Art. 14) | `pip install air-gate` |
| [**air-blackbox-mcp**](https://github.com/airblackbox/air-blackbox-mcp) | MCP server — audit, replay, scan, and compliance tools in Claude Desktop, Claude Code, Cursor | via MCP config |
| [**compliance-action**](https://github.com/airblackbox/compliance-action) | GitHub Action — EU AI Act compliance checks on every PR | via workflow |
| [**air-platform**](https://github.com/airblackbox/air-platform) | This repo — one-command full stack | `make up` |
| [**tombstone**](https://github.com/airblackbox/tombstone) | Provable, crypto-shredded erasure on a tamper-evident ledger (GDPR Art. 17) | — |

Framework trust layers for LangChain, CrewAI, OpenAI Agents SDK, Claude Agent SDK, AutoGen, Google ADK, and Haystack ship inside the main [airblackbox](https://github.com/airblackbox/airblackbox) repo (`air_blackbox.trust.*`).

## Running the Compliance Scanner

The scanner runs against any Python AI project — no stack required:

```bash
pip install air-blackbox
air-blackbox comply --scan . -v     # gap analysis: Articles 9–15
air-blackbox replay                 # replay recorded episodes
air-blackbox evidence               # signed evidence bundle for auditors
```

## Testing

Integration tests run against the live stack:

```bash
make up
make test    # 6 health/audit tests; +1 live LLM round-trip when OPENAI_API_KEY is set
```

If the stack isn't running, the suite skips with instructions instead of failing. CI boots the full compose stack and runs the same tests on every push.

## Threat Model

| Threat | Risk | Mitigation |
|---|---|---|
| **Prompt data leakage** | PII or proprietary data exposed in traces | `genaisafe` hash-and-preview redaction; prompt vault offload |
| **Secret exposure** | API keys, bearer tokens in span attributes | Denylist regex detection, automatic redaction |
| **Runaway loops** | Infinite tool-calling burning budget | Gateway loop detection + session budgets; collector repeat-threshold flagging |
| **Audit tampering** | Logs edited after an incident | HMAC-SHA256 chain — modifying one record breaks every record after it |

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
