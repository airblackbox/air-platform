#!/usr/bin/env python3
"""
Scripted air-platform demo for GIF recording.
Shows the current stack: Gateway → OTel Collector → Jaeger, MinIO prompt vault.
No Docker required — simulates the platform experience.
"""
import time

# Colors
B = "\033[1m"
D = "\033[2m"
R = "\033[0m"
G = "\033[32m"
RED = "\033[31m"
Y = "\033[33m"
C = "\033[36m"
O = "\033[38;5;208m"
W = "\033[97m"
M = "\033[35m"

def p(text, delay=0.01):
    print(text)
    time.sleep(delay)

def section(title):
    print()
    p(f"  {C}{B}━━━ {title} ━━━{R}")
    print()
    time.sleep(0.3)
# ══════════════════════════════════════════════════════════════
print()
p(f"  {O}{B}╔═══════════════════════════════════════════════════════╗{R}")
p(f"  {O}{B}║  {W}AIR BLACKBOX{O}  Platform — AI Compliance Infrastructure ║{R}")
p(f"  {O}{B}║  {R}{D}make up{R}  {O}{B}                                             ║{R}")
p(f"  {O}{B}╚═══════════════════════════════════════════════════════╝{R}")
print()
time.sleep(0.5)

# ── 1. STACK BOOT ───────────────────────────────────────────
section("1. Platform startup")

services = [
    ("MinIO (S3)",     "9000",  "Encrypted prompt vault"),
    ("Jaeger",         "16686", "Distributed tracing UI"),
    ("OTel Collector", "4317",  "Normalize + vault + redact + metrics"),
    ("Gateway",        "8080",  "OpenAI-compatible proxy, signed image"),
]
for name, port, desc in services:
    p(f"  {G}✓{R} {B}{name:16s}{R} {D}:{port}  — {desc}{R}")
    time.sleep(0.15)

print()
p(f"  {G}{B}All services healthy{R}  {D}(2.1s){R}")
time.sleep(0.5)
# ── 2. ONE-LINE INTEGRATION ─────────────────────────────────
section("2. Point your agent at the gateway")

p(f"  {D}client = OpenAI({R}")
p(f"      {D}base_url={R}{C}\"http://localhost:8080/v1\"{R}")
p(f"  {D}){R}")
print()
p(f"  {G}✓{R} No SDK changes. No refactoring. {D}~3 ms overhead per call.{R}")
time.sleep(0.5)
# ── 3. EVERY CALL RECORDED ──────────────────────────────────
section("3. Every LLM call becomes a signed audit record")

p(f"  {D}POST /v1/chat/completions{R}  {D}model:{R} gpt-4o  {D}tools:{R} [search, send_email]")
print()
p(f"  {C}→ Gateway{R}      {D}records .air.json — HMAC chained to previous record{R}")
p(f"  {C}→ Prompt Vault{R} {D}offloads prompt + completion to encrypted storage{R}")
p(f"  {C}→ Collector{R}    {D}normalizes to gen_ai.* semconv, extracts cost{R}")
print()

p(f"  {Y}⚡ genaisafe: PII detected before export{R}")
p(f"    {Y}→{R} email: jane.doe@stripe.com  {D}→ sha256:a3f8...{R}")
p(f"    {Y}→{R} api key: sk-proj-Xk29...     {D}→ [REDACTED]{R}")
p(f"  {G}✓{R} Redacted span forwarded to Jaeger")
time.sleep(0.5)
# ── 4. GUARDRAILS ───────────────────────────────────────────
section("4. Guardrails block runaway agents at the proxy")

p(f"  {D}Request #6 in 40s — identical prompt{R}")
print()
p(f"  {RED}✗ loop_detection triggered{R}  {D}similar_prompt_threshold: 0.80{R}")
p(f"    {D}action:{R} {RED}HTTP 429{R} {D}— never reaches the LLM provider{R}")
p(f"    {D}session replay saved for incident review{R}")
print()
p(f"  {D}Budget guard:{R}  {G}CLEAR{R}  {D}($0.036 of $25.00 session limit){R}")
p(f"  {D}Injection scan:{R} {G}CLEAR{R}  {D}(20 patterns, 5 attack categories){R}")
time.sleep(0.5)
# ── 5. VERIFY + EVIDENCE ────────────────────────────────────
section("5. Tamper-evident chain, verifiable evidence")

p(f"  {C}$ air-blackbox replay --verify{R}")
p(f"    {G}✓ chain valid{R}  {D}147 records · HMAC-SHA256 · ML-DSA-65 checkpoint{R}")
print()
p(f"  {C}$ air-blackbox evidence{R}")
p(f"    {G}✓ evidence-bundle.air-evidence{R}  {D}— auditor runs verify.py → PASS{R}")
time.sleep(0.4)
# ── 6. COMPLIANCE SUMMARY ───────────────────────────────────
print(f"""
  {D}┌───────────────────────────────────────────────────────┐{R}
  {D}│{R}  {B}EU AI Act — technical evidence coverage{R}              {D}│{R}
  {D}├───────────────────────────────────────────────────────┤{R}
  {D}│{R}  Art. 9   Risk Management     {G}✓{R} Guardrails + AIR Gate {D}│{R}
  {D}│{R}  Art. 10  Data Governance     {G}✓{R} PII Redaction + Vault {D}│{R}
  {D}│{R}  Art. 11  Technical Docs      {G}✓{R} Full OTel Traces      {D}│{R}
  {D}│{R}  Art. 12  Record-Keeping      {G}✓{R} HMAC Audit Chain      {D}│{R}
  {D}│{R}  Art. 14  Human Oversight     {G}✓{R} Replay + AIR Gate     {D}│{R}
  {D}│{R}  Art. 15  Robustness          {G}✓{R} Injection Detection   {D}│{R}
  {D}│{R}                                                       {D}│{R}
  {D}│{R}  {B}Frameworks:{R} OpenAI · LangChain · CrewAI · AutoGen   {D}│{R}
  {D}│{R}              Claude · Google ADK · Haystack           {D}│{R}
  {D}└───────────────────────────────────────────────────────┘{R}
""")
time.sleep(0.4)

# ── NEXT STEPS ──────────────────────────────────────────────
p(f"  {B}Get started:{R}")
p(f"  {C}git clone https://github.com/airblackbox/air-platform{R}")
p(f"  {C}cp .env.example .env && make up{R}")
p(f"")
p(f"  {D}Docs:    airblackbox.ai{R}")
p(f"  {D}GitHub:  github.com/airblackbox{R}")
print()
