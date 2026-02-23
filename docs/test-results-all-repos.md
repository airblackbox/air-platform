# AIR Blackbox — Full Test Suite Results

**Date:** February 23, 2026
**Repos tested:** 21 of 22 (`.github` is org profile, no code)
**Total tests:** 697 unit tests + 18 live integration tests
**Result: ALL PASSING**

---

## Part 1: Unit Tests (per-repo)

### Go Repos (4 repos — `go test ./...`)

| Repo | Tests | Result | Notes |
|------|-------|--------|-------|
| gateway | 6 packages | PASS | guardrails, proxy, recorder, replay, trust, vault |
| otel-prompt-vault | 1 package | PASS | promptvaultprocessor |
| otel-semantic-normalizer | 2 packages | PASS | genainormprocessor, genainormalizerprocessor |
| otel-collector-genai | 1 package | PASS | genaisafeprocessor |

### Python Repos (15 repos — `pytest`)

| Repo | Tests | Result | Notes |
|------|-------|--------|-------|
| agent-episode-store | 66 | PASS | Storage, API, replay, diff, export |
| agent-policy-engine | 37 | PASS | Evaluator, killswitch, tiers, trust scoring |
| agent-tool-sandbox | 22 | PASS | Enforcer, models, runner |
| agent-vcr | 25 | PASS | Recorder, replayer, models |
| aibom-policy-engine | 27 | PASS | API, builder, checker, models |
| eval-harness | 25 | PASS | Regression, reports, scoring |
| mcp-policy-gateway | 16 | PASS | API, interceptor, models |
| mcp-security-scanner | 11 | PASS | Analyzer, models, rules |
| python-sdk | 18 | PASS | Client, integrations, wrapper |
| runtime-aibom-emitter | 20 | PASS | API, models, observer, publisher |
| trace-regression-harness | 20 | PASS | Engine, formatter, models, runner |
| trust-autogen | 100 | PASS | Callbacks, guardrails, vault, audit, plugin |
| trust-crewai | 79 | PASS | Callbacks, guardrails, vault, audit, plugin |
| trust-langchain | 82 | PASS | Callbacks, guardrails, vault, injection detector |
| trust-openai-agents | 85 | PASS | Callbacks, guardrails, vault, injection detector |

### TypeScript Repos (1 repo — `npm test` / Jest)

| Repo | Tests | Suites | Result | Coverage | Notes |
|------|-------|--------|--------|----------|-------|
| trust-openclaw | 44 | 4 | PASS | 61% stmts | audit-ledger, consent-gate, data-vault, injection-detector |

### Config/Platform Repos (2 repos)

| Repo | Check | Result | Notes |
|------|-------|--------|-------|
| air-platform | docker-compose config | VALID | 4 HTML tools + full-stack compose |
| .github | org profile | N/A | Community health files only |

---

## Part 2: Live Integration Tests (against running stack)

Running services: Gateway (:8080), OTel Collector (:4317), Jaeger (:16686), MinIO (:9000), Episode Store (:8100), Policy Engine (:8200)

### End-to-End Pipeline (5/5 PASS)

| Step | Component | Result | Details |
|------|-----------|--------|---------|
| 1 | Gateway -> OpenAI | PASS | "Mars, Venus, Jupiter." — 23 tokens, 954ms |
| 2 | AIR Record on disk | PASS | SHA-256 checksums, vault refs, trace_id |
| 3 | OTel trace in Jaeger | PASS | llm.call span, trace_id matched |
| 4 | Episode in Episode Store | PASS | Episode created, steps linked to AIR record |
| 5 | Policy Engine evaluate | PASS | allowed=true with "autonomous" policy |

### python-sdk (3/3 PASS)

| Test | Result | Details |
|------|--------|---------|
| AIRClient.chat() | PASS | "Two." — 21 tokens via live Gateway |
| AIRClient.health() | PASS | {"status":"ok"} |
| air_openai() wrapper | PASS | "Bonjour !" — OpenAI client proxied through Gateway |

### trust-langchain (3/3 PASS)

| Test | Result | Details |
|------|--------|---------|
| InjectionDetector.scan() | PASS | score=0.9, blocked=True on "Ignore previous instructions" |
| DataVault.tokenize() | PASS | SSN + email -> [AIR:vault:pii:...] tokens (2 found) |
| AuditLedger.verify() | PASS | Hash chain valid after 2 entries |

### trust-openai-agents (1/1 PASS)

| Test | Result | Details |
|------|--------|---------|
| InjectionDetector.scan() | PASS | score=0.9, blocked=True |

### trust-crewai (1/1 PASS)

| Test | Result | Details |
|------|--------|---------|
| DataVault.tokenize() | PASS | SSN detected and tokenized |

### trust-autogen (1/1 PASS)

| Test | Result | Details |
|------|--------|---------|
| AuditLedger.verify() | PASS | Chain valid=True |

### eval-harness (2/2 PASS)

| Test | Result | Details |
|------|--------|---------|
| EpisodeClient -> live store | PASS | Retrieved 1 episode from localhost:8100 |
| ScoringEngine.score() | PASS | correctness=1.0, safety=1.0 on real episode |

### mcp-security-scanner (1/1 PASS)

| Test | Result | Details |
|------|--------|---------|
| SecurityAnalyzer.scan() | PASS | 1 finding on execute_command tool, passed=False |

### mcp-policy-gateway (1/1 PASS)

| Test | Result | Details |
|------|--------|---------|
| ToolInterceptor.intercept() | PASS | Decision=DENY on unconfigured agent |

---

## Summary

```
UNIT TESTS
  Total repos:        22
  Repos with tests:   20
  All tests passing:  20/20
  Total test count:   697

INTEGRATION TESTS (live stack)
  Pipeline tests:     5/5 PASS
  SDK tests:          3/3 PASS
  Trust layer tests:  6/6 PASS
  Eval tests:         2/2 PASS
  MCP tests:          2/2 PASS
  Total:              18/18 PASS

OVERALL: 697 unit tests + 18 integration tests = ALL GREEN

Warnings (resolved):
  - datetime.utcnow() deprecation in 4 Python repos — FIXED
  - trust-openclaw: Jest worker force-exit warning
```

## Architecture Validated

The following end-to-end flow was proven with real OpenAI API traffic:

```
User Request
    |
AIR Gateway (:8080) — Go reverse proxy
    | proxies to OpenAI, captures everything
    |-- AIR Record (.air.json) — checksums, vault refs, tokens
    |-- OTel Trace -> Collector -> Jaeger (:16686)
    |-- Vault -> MinIO S3 (:9000) — encrypted request/response storage
    |
Episode Store (:8100) — Python/FastAPI
    | stores episodes with linked AIR records
Policy Engine (:8200) — Python/FastAPI
    | evaluates actions against autonomy policies
Eval Harness — scores episodes, detects regressions
    |
Trust Layers — inject into LangChain/CrewAI/AutoGen/OpenAI Agents/OpenClaw
    |-- Injection detection (prompt injection -> blocked)
    |-- PII tokenization (SSN/email -> vault tokens)
    |-- Audit chain (hash-linked, tamper-evident)
```
