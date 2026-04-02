#!/usr/bin/env python3
"""
Scripted air-platform demo for GIF recording.
Shows the full stack: Gateway → Episode Store → Policy Engine → OTel Collector
No Docker required — simulates the platform experience.
"""
import time
import json

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
p(f"  {O}{B}║  {R}{D}docker compose up{R}  {O}{B}                                   ║{R}")
p(f"  {O}{B}╚═══════════════════════════════════════════════════════╝{R}")
print()
time.sleep(0.5)

# ── 1. STACK BOOT ───────────────────────────────────────────
section("1. Platform startup")

services = [
    ("MinIO (S3)",          "9000", "Object storage for prompt vault"),
    ("Jaeger",              "16686", "Distributed tracing UI"),
    ("OTel Collector",      "4317", "Redaction + cost metrics + loop detection"),
    ("Gateway",             "8080", "OpenAI-compatible reverse proxy"),
    ("Episode Store",       "8100", "Task-level episode grouping"),
    ("Policy Engine",       "8200", "Risk tiers + kill switches + trust scoring"),
]
for name, port, desc in services:
    p(f"  {G}✓{R} {B}{name:22s}{R} {D}:{port}  — {desc}{R}")
    time.sleep(0.15)

print()
p(f"  {G}{B}All 6 services healthy{R}  {D}(3.2s){R}")
time.sleep(0.5)
# ── 2. AGENT REQUEST THROUGH GATEWAY ────────────────────────
section("2. Agent sends LLM request through Gateway")

p(f"  {D}POST http://localhost:8080/v1/chat/completions{R}")
p(f"  {D}model:{R} gpt-4o")
p(f"  {D}messages:{R} [{D}system: \"You are a recruiting assistant\"{R}]")
p(f"  {D}tools:{R} [search_candidates, send_email, delete_records]")
print()
time.sleep(0.3)

p(f"  {C}→ Gateway intercepts{R}  {D}records OTel span{R}")
p(f"  {C}→ Prompt Vault{R}  {D}encrypts & stores prompt + completion{R}")
p(f"  {C}→ OTel Collector{R}  {D}extracts cost metrics{R}")
print()

# Show PII redaction
p(f"  {Y}⚡ OTel Processor: PII detected in completion{R}")
p(f"    {Y}→{R} email: jane.doe@stripe.com  {D}→ sha256:a3f8...{R}")
p(f"    {Y}→{R} phone: 415-555-0199        {D}→ sha256:7b2c...{R}")
p(f"    {Y}→{R} ssn:   123-45-6789         {D}→ [REDACTED]{R}")
p(f"  {G}✓{R} Redacted span forwarded to Jaeger")
time.sleep(0.5)
# ── 3. EPISODE STORE ────────────────────────────────────────
section("3. Episode Store groups traces into task episodes")

p(f"  {D}GET http://localhost:8100/v1/episodes{R}")
print()
p(f"  {B}Episode: ep-7f3a2b{R}  {D}\"Recruit senior data engineer\"{R}")
p(f"    {D}├─{R} span 1: {C}chat.completion{R}  {D}gpt-4o  1,247 tokens  $0.018{R}")
p(f"    {D}├─{R} span 2: {C}tool.call{R}       {D}search_candidates → 12 results{R}")
p(f"    {D}├─{R} span 3: {C}chat.completion{R}  {D}gpt-4o  892 tokens   $0.013{R}")
p(f"    {D}├─{R} span 4: {C}tool.call{R}       {D}send_email → GATED{R}")
p(f"    {D}└─{R} span 5: {C}chat.completion{R}  {D}gpt-4o  341 tokens   $0.005{R}")
print()
p(f"  {D}Total:{R} {B}5 spans{R}  {D}|{R}  {B}2,480 tokens{R}  {D}|{R}  {B}$0.036{R}  {D}|{R}  {B}1 gated action{R}")
time.sleep(0.5)
# ── 4. POLICY ENGINE ────────────────────────────────────────
section("4. Policy Engine evaluates episode")

p(f"  {D}POST http://localhost:8200/v1/evaluate{R}")
p(f"  {D}episode:{R} ep-7f3a2b")
print()
p(f"  {B}Policy Evaluation:{R}")
p(f"    {D}Risk tier:{R}      {Y}MEDIUM{R}  {D}(tool calls + outbound comms){R}")
p(f"    {D}Trust score:{R}    {B}0.82{R}  {D}(above 0.7 threshold){R}")
p(f"    {D}Autonomy:{R}       {G}SUPERVISED{R}  {D}(human approves gated actions){R}")
p(f"    {D}Kill switch:{R}    {D}INACTIVE{R}")
print()
p(f"  {B}Action decisions:{R}")
p(f"    {G}✓{R} search_candidates  {G}AUTO-ALLOWED{R}  {D}(read-only){R}")
p(f"    {Y}⏳{R} send_email          {Y}PENDING{R}       {D}(requires human approval){R}")
p(f"    {RED}✗{R} delete_records      {RED}BLOCKED{R}       {D}(policy: no AI deletes){R}")
print()
p(f"  {D}Loop detection:{R}   {G}CLEAR{R}  {D}(no repeated tool patterns){R}")
p(f"  {D}Budget guard:{R}     {G}CLEAR{R}  {D}($0.036 of $5.00 limit){R}")
time.sleep(0.5)
# ── 5. COMPLIANCE SUMMARY ───────────────────────────────────
section("5. EU AI Act compliance status")

print(f"""
  {D}┌───────────────────────────────────────────────────────┐{R}
  {D}│{R}  {B}AIR Blackbox — Platform Compliance Report{R}           {D}│{R}
  {D}├───────────────────────────────────────────────────────┤{R}
  {D}│{R}                                                       {D}│{R}
  {D}│{R}  Art. 9   Risk Management     {G}✓{R} Policy Engine        {D}│{R}
  {D}│{R}  Art. 10  Data Governance      {G}✓{R} PII Redaction        {D}│{R}
  {D}│{R}  Art. 11  Technical Docs       {G}✓{R} Full Call Graphs     {D}│{R}
  {D}│{R}  Art. 12  Record-Keeping       {G}✓{R} HMAC Audit Chain     {D}│{R}
  {D}│{R}  Art. 14  Human Oversight      {G}✓{R} ConsentGate          {D}│{R}
  {D}│{R}  Art. 15  Robustness           {G}✓{R} Injection Detection  {D}│{R}
  {D}│{R}                                                       {D}│{R}
  {D}│{R}  {B}Infrastructure:{R}                                     {D}│{R}
  {D}│{R}  Gateway           {G}✓{R}  OTel Collector    {G}✓{R}             {D}│{R}
  {D}│{R}  Episode Store     {G}✓{R}  Prompt Vault      {G}✓{R}             {D}│{R}
  {D}│{R}  Policy Engine     {G}✓{R}  Eval Harness      {G}✓{R}             {D}│{R}
  {D}│{R}                                                       {D}│{R}
  {D}│{R}  {B}Frameworks:{R} OpenAI · LangChain · CrewAI · AutoGen   {D}│{R}
  {D}│{R}  {B}Deadline:{R}   {Y}August 2, 2026{R}  {D}(487 days){R}              {D}│{R}
  {D}└───────────────────────────────────────────────────────┘{R}
""")
time.sleep(0.5)

# ── NEXT STEPS ──────────────────────────────────────────────
p(f"  {B}Get started:{R}")
p(f"  {C}git clone https://github.com/airblackbox/air-platform{R}")
p(f"  {C}cp .env.example .env && make up{R}")
p(f"")
p(f"  {D}Docs:    airblackbox.ai{R}")
p(f"  {D}GitHub:  github.com/airblackbox{R}")
print()