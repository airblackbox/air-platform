# Contributing to AIR Blackbox

Thank you for your interest in contributing to AIR Blackbox. This project is building the infrastructure layer for safe deployment of autonomous AI agents, and community contributions are essential to getting it right.

## Getting Started

1. **Fork the repository** you want to contribute to
2. **Clone your fork** locally
3. **Create a branch** for your changes (`git checkout -b feature/your-feature`)
4. **Make your changes** and commit them
5. **Push to your fork** and open a Pull Request

## What We're Looking For

### High-Impact Contributions

- **New framework connectors** — Trust plugins for additional AI frameworks (e.g., Haystack, DSPy, Semantic Kernel)
- **OTel Collector processors** — Additional safety processors for the collector pipeline
- **Policy templates** — Pre-built policy configurations for common compliance scenarios
- **Documentation** — Architecture guides, tutorials, and integration examples

### Bug Reports

If you find a bug, please open an issue with:

- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Go/Python version, OTel Collector version)

### Feature Requests

Open an issue tagged `enhancement` with:

- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

## Code Guidelines

### Go (Gateway, OTel Processors)

- Follow standard Go conventions (`gofmt`, `golint`)
- Write table-driven tests
- Keep functions small and focused
- Add comments for exported types and functions

### Python (SDK, Trust Plugins)

- Follow PEP 8
- Type hints for all public functions
- Docstrings for all public classes and methods
- Tests using `pytest`

## Pull Request Process

1. Ensure all tests pass locally
2. Update documentation if your change affects public APIs
3. Keep PRs focused — one feature or fix per PR
4. Write a clear PR description explaining the "why"
5. Link any related issues

## Code of Conduct

Be respectful. Be constructive. We're building infrastructure that matters.

## Questions?

Open a discussion in the relevant repository or reach out via GitHub Issues.

---

**AIR Blackbox** — Agent Infrastructure Runtime
