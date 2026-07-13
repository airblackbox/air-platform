# Changelog

All notable changes to **AIR Platform** will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] — 2026-07-13

### Changed
- Rebuilt Docker Compose around the consolidated stack: gateway now pulled as the
  signed `ghcr.io/airblackbox/airblackbox` image; collector built directly from the
  public repo. No local sibling checkouts required — `docker compose up` works from
  a fresh clone.
- Rewrote README for the current ecosystem (airblackbox, air-gate, air-blackbox-mcp,
  compliance-action, tombstone); removed links to archived repositories.
- Replaced integration tests targeting the retired Episode Store / Policy Engine /
  Eval Harness services with tests for the gateway audit surface (`/health`,
  `/v1/audit`, `/v1/analytics`, `/v1/audit/export`) plus an optional live LLM
  round-trip (needs `OPENAI_API_KEY`).
- Tests now skip with instructions when the stack is down (hard-fail in CI via
  `AIR_REQUIRE_STACK=1`).
- CI now boots the full compose stack and runs the integration suite.

### Added
- `collector.yaml` — local-only OTel pipeline config mounted over the image default
  (normalize → prompt vault → redact/metrics → batch). Nothing leaves your machine.
- `guardrails.yaml` — gateway guardrails config (budgets, loop/retry protection,
  tool allow/blocklists).

### Fixed
- Invalid `build-backend` in pyproject.toml (`setuptools.backends._legacy:_Backend`
  → `setuptools.build_meta`).
- Worked around duplicate `processors:` key in the upstream collector config that
  crashed the collector on boot (fix also submitted to the main repo).

### Removed
- Obsolete tests and smoke script for archived services (`test_production.py`,
  `test_e2e_stack.py`, `test_end_to_end.py`, `test_episode_flow.py`,
  `test_policy_flow.py`).

## [0.1.0] — 2026-02-22

- Docker Compose orchestration for full AIR Blackbox stack
- Integration test suite (18 tests across all components)
- Interactive dashboard (dashboard.html) and comparison tool (compare.html)
- Hosted demo page for browser-based walkthrough
- Architecture documentation and component catalog
