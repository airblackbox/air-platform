# AIR Platform

**One command to run the complete AI accountability stack.**

The AIR Platform orchestrates all four layers of the trust infrastructure:

```
┌─────────────────────────────────────────────────────┐
│                   AIR Platform                       │
│                                                      │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Gateway   │→│ Episode Store │→│ Eval Harness  │  │
│  │ :8080     │  │ :8100        │  │ (CLI)        │  │
│  └──────────┘  └──────────────┘  └──────────────┘  │
│       │              │                    │          │
│       ▼              ▼                    ▼          │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ MinIO     │  │ SQLite       │  │ Policy Engine│  │
│  │ :9000     │  │ (embedded)   │  │ :8200        │  │
│  └──────────┘  └──────────────┘  └──────────────┘  │
│       │                                              │
│       ▼                                              │
│  ┌──────────┐  ┌──────────────┐                     │
│  │ Collector │  │ Jaeger UI    │                     │
│  │ :4317     │  │ :16686       │                     │
│  └──────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone with sibling repos
git clone https://github.com/nostalgicskinco/air-platform.git
git clone https://github.com/nostalgicskinco/air-blackbox-gateway.git ../airblackbox-mvp
git clone https://github.com/nostalgicskinco/agent-episode-store.git ../agent-episode-store
git clone https://github.com/nostalgicskinco/eval-harness.git ../eval-harness
git clone https://github.com/nostalgicskinco/agent-policy-engine.git ../agent-policy-engine

# Start everything
cd air-platform
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
make up

# Check all services are running
make status
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| **Gateway** | 8080 | OpenAI-compatible reverse proxy, records AIR audit trails |
| **Episode Store** | 8100 | Groups AIR records into replayable task-level episodes |
| **Policy Engine** | 8200 | Risk-tiered autonomy, kill switches, trust scoring |
| **Eval Harness** | — | CLI tool for replaying and scoring episodes |
| **MinIO** | 9000/9001 | S3-compatible vault for prompts and completions |
| **OTel Collector** | 4317/4318 | Telemetry pipeline (normalize, vault, redact) |
| **Jaeger** | 16686 | Distributed tracing UI |

## Commands

```bash
make up        # Start the full stack
make down      # Stop all services
make clean     # Stop and delete all data
make test      # Run integration tests
make logs      # Tail all service logs
make status    # Health check all services
```

## Integration Tests

The test suite verifies cross-service communication:

- **IT-1: Health** — All services respond to health checks
- **IT-2: Episode Flow** — Ingest → List → Get → Replay
- **IT-3: Policy Flow** — Create policy → Evaluate actions → Enforce rules
- **IT-4: End-to-End** — Episodes feed trust scores that influence policy decisions

```bash
# Run tests (requires stack to be running)
make test
```

## Repository Layout

```
air-platform/           ← You are here (orchestration)
├── docker-compose.yml  ← Wires all services together
├── Makefile            ← Convenience commands
├── tests/              ← Integration tests
│   ├── test_health.py
│   ├── test_episode_flow.py
│   ├── test_policy_flow.py
│   └── test_end_to_end.py
│
├── ../airblackbox-mvp/        ← Gateway (Go)
├── ../agent-episode-store/    ← Episode Store (Python)
├── ../eval-harness/           ← Eval Harness (Python)
└── ../agent-policy-engine/    ← Policy Engine (Python)
```

## The Data Flow

1. **Record** — Agent makes an LLM call through the Gateway. The call is recorded as a tamper-evident AIR record with vault-backed storage.

2. **Group** — The Episode Store groups related AIR records into task-level episodes. One "write an email" task = one episode with multiple LLM calls.

3. **Score** — The Eval Harness replays episodes, scoring them on correctness (40%), cost delta (20%), tool match (20%), latency delta (10%), and safety (10%).

4. **Enforce** — The Policy Engine uses eval scores to compute trust, assigns agents to autonomy tiers (SHADOW → GATED → SUPERVISED → AUTONOMOUS), and enforces runtime rules with kill switches.

## Roadmap

- [x] Gateway — Proxy + vault + AIR records
- [x] Episode Store — SQLite + replay + JSONL export
- [x] Eval Harness — Scoring + regression detection
- [x] Policy Engine — Tiers + kill switches + trust
- [x] Docker Compose — Full stack orchestration
- [x] Integration Tests — Cross-service verification
- [ ] Collector Pipeline — OTel processors (normalize, vault, redact)
- [ ] Live Replay — Replay episodes through the gateway
- [ ] Dashboard — Real-time monitoring UI
- [ ] CI/CD — GitHub Actions for the full stack

## License

Apache-2.0