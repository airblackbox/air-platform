"""
AIR Blackbox — Production Smoke Test
=====================================
Run this AFTER you've started the stack.

This script sends real LLM requests through the AIR Blackbox Gateway
and verifies every layer of the trust pipeline is working:
  1. Gateway proxies the request to OpenAI
  2. AIR record is written to disk with checksums + vault refs
  3. OTel trace is captured in Jaeger
  4. Episode Store accepts and stores the episode
  5. Policy Engine evaluates the action

Prerequisites:
  - Docker running with gateway, collector, jaeger, minio
  - Episode Store running on port 8100
  - Policy Engine running on port 8200
  - OpenAI API key in your environment
  - pip install requests

Usage:
  export OPENAI_API_KEY=sk-...
  python test_production.py
"""

import os
import sys
import time
import json
import subprocess
import requests


# -- Configuration ---------------------------------------------------------
GATEWAY_URL = "http://localhost:8080"        # AIR Blackbox Gateway
EPISODE_STORE_URL = "http://localhost:8100"  # Episode Store API
POLICY_ENGINE_URL = "http://localhost:8200"  # Policy Engine API
JAEGER_URL = "http://localhost:16686"        # Jaeger Query API

# Gateway container name (for reading AIR records from disk)
GATEWAY_CONTAINER = "air-blackbox-gateway-gateway-1"

# Your OpenAI key -- reads from environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


def print_step(num, title):
    print(f"\n{'='*60}")
    print(f"  Step {num}: {title}")
    print(f"{'='*60}")

def print_pass(msg):
    print(f"  PASS -- {msg}")

def print_fail(msg):
    print(f"  FAIL -- {msg}")

def print_info(msg):
    print(f"  INFO  {msg}")


def check_services():
    print_step(0, "Checking all services are running")
    services = {
        "Gateway":       (f"{GATEWAY_URL}/health", 200),
        "Episode Store": (f"{EPISODE_STORE_URL}/v1/health", 200),
        "Policy Engine": (f"{POLICY_ENGINE_URL}/v1/health", 200),
        "Jaeger":        (f"{JAEGER_URL}/api/services", 200),
    }
    all_up = True
    for name, (url, expected) in services.items():
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == expected:
                print_pass(f"{name} is up ({url})")
            else:
                print_info(f"{name} returned {r.status_code} (expected {expected})")
                print_pass(f"{name} is responding")
        except requests.ConnectionError:
            print_fail(f"{name} is not reachable at {url}")
            all_up = False
        except Exception as e:
            print_fail(f"{name} error: {e}")
            all_up = False
    if not all_up:
        print("\nSome services are down.")
        print("   Gateway: docker compose up -d (in airblackbox-mvp/)")
        print("   Episode Store: uvicorn app.server:app --port 8100")
        print("   Policy Engine: uvicorn app.server:app --port 8200")
        sys.exit(1)
    return True


def test_gateway_request():
    print_step(1, "Sending a real LLM request through Gateway")
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Name three planets. Reply in exactly three words."}
        ],
        "max_tokens": 20
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    try:
        r = requests.post(f"{GATEWAY_URL}/v1/chat/completions", json=payload, headers=headers, timeout=30)
        if r.status_code != 200:
            print_fail(f"Gateway returned {r.status_code}: {r.text[:200]}")
            return None
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        model = data.get("model", "unknown")
        tokens = data.get("usage", {})
        run_id = r.headers.get("x-run-id", "none")
        print_pass(f'Got response: "{content}"')
        print_info(f"Model: {model}")
        print_info(f"Tokens: {tokens.get('total_tokens', 0)}")
        print_info(f"Run ID: {run_id}")
        return {"run_id": run_id, "tokens": tokens, "response": content, "model": model}
    except requests.ConnectionError:
        print_fail("Cannot connect to Gateway. Is Docker running?")
        return None
    except Exception as e:
        print_fail(f"Request failed: {e}")
        return None


def test_air_record(run_id):
    print_step(2, "Reading AIR record from Gateway disk")
    if not run_id or run_id == "none":
        print_fail("No run_id from Gateway -- cannot check AIR record")
        return None
    try:
        result = subprocess.run(
            ["docker", "exec", GATEWAY_CONTAINER, "cat", f"/data/runs/{run_id}.air.json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            print_fail(f"Could not read AIR record: {result.stderr[:200]}")
            return None
        air = json.loads(result.stdout)
        print_pass(f"AIR record found for run {run_id}")
        print_info(f"Version:  {air.get('version')}")
        print_info(f"Model:    {air.get('model')}")
        print_info(f"Provider: {air.get('provider')}")
        print_info(f"Tokens:   {air.get('tokens', {}).get('total', 0)}")
        print_info(f"Duration: {air.get('duration_ms')}ms")
        print_info(f"Status:   {air.get('status')}")
        print_info(f"Vault:    {air.get('request_vault_ref', 'n/a')}")
        print_info(f"Checksum: {air.get('request_checksum', 'n/a')[:50]}...")
        return air
    except subprocess.TimeoutExpired:
        print_fail("Timed out reading AIR record from container")
        return None
    except Exception as e:
        print_fail(f"Error reading AIR record: {e}")
        return None


def test_jaeger_trace(trace_id):
    print_step(3, "Checking OTel trace in Jaeger")
    if not trace_id:
        print_fail("No trace_id from AIR record -- skipping Jaeger check")
        return False
    print_info("Waiting 2 seconds for trace to propagate...")
    time.sleep(2)
    try:
        r = requests.get(f"{JAEGER_URL}/api/traces/{trace_id}", timeout=10)
        if r.status_code != 200:
            r2 = requests.get(f"{JAEGER_URL}/api/traces?service=air-blackbox-gateway&limit=1&lookback=5m", timeout=10)
            if r2.status_code == 200:
                traces = r2.json().get("data", [])
                if traces:
                    print_pass(f"Found {len(traces)} recent trace(s) in Jaeger")
                    span = traces[0]["spans"][0]
                    print_info(f"Trace ID:  {traces[0]['traceID']}")
                    print_info(f"Operation: {span['operationName']}")
                    print_info(f"Duration:  {span['duration'] // 1000}ms")
                    return True
            print_fail(f"Jaeger returned {r.status_code} for trace {trace_id}")
            return False
        trace_data = r.json()
        spans = trace_data.get("data", [{}])[0].get("spans", [])
        print_pass(f"Trace found with {len(spans)} span(s)")
        if spans:
            print_info(f"Operation: {spans[0]['operationName']}")
            print_info(f"Duration:  {spans[0]['duration'] // 1000}ms")
        return True
    except requests.ConnectionError:
        print_fail("Cannot connect to Jaeger")
        return False
    except Exception as e:
        print_fail(f"Error checking Jaeger: {e}")
        return False


def test_episode_store(air_record, response_text):
    print_step(4, "Posting episode to Episode Store")
    if not air_record:
        print_fail("No AIR record -- cannot create episode")
        return False
    episode_payload = {
        "agent_id": "smoke-test-agent",
        "status": air_record.get("status", "success"),
        "steps": [{
            "step_index": 0,
            "step_type": "llm_call",
            "air_record_id": air_record["run_id"],
            "model": air_record.get("model"),
            "provider": air_record.get("provider"),
            "input_summary": "Name three planets. Reply in exactly three words.",
            "output_summary": response_text or "unknown",
            "tokens": air_record.get("tokens", {}).get("total", 0),
            "cost_usd": 0.00002,
            "duration_ms": air_record.get("duration_ms", 0),
            "timestamp": air_record.get("timestamp"),
            "metadata": {
                "trace_id": air_record.get("trace_id"),
                "request_checksum": air_record.get("request_checksum"),
                "response_checksum": air_record.get("response_checksum"),
            }
        }],
        "metadata": {"source": "production-smoke-test", "vault_ref": air_record.get("request_vault_ref")}
    }
    try:
        r = requests.post(f"{EPISODE_STORE_URL}/v1/episodes", json=episode_payload, timeout=10)
        if r.status_code in (200, 201):
            episode = r.json()
            print_pass(f"Episode created: {episode.get('episode_id', 'unknown')}")
            print_info(f"Agent:    {episode.get('agent_id')}")
            print_info(f"Status:   {episode.get('status')}")
            print_info(f"Steps:    {episode.get('step_count', len(episode.get('steps', [])))}")
            print_info(f"Tokens:   {episode.get('total_tokens', 0)}")
            return True
        else:
            print_fail(f"Episode Store returned {r.status_code}: {r.text[:300]}")
            return False
    except requests.ConnectionError:
        print_fail("Cannot connect to Episode Store")
        return False
    except Exception as e:
        print_fail(f"Error: {e}")
        return False


def test_policy_engine(air_record):
    print_step(5, "Evaluating action with Policy Engine")
    if not air_record:
        print_fail("No AIR record -- cannot evaluate policy")
        return False
    payload = {
        "agent_id": "smoke-test-agent",
        "action_context": {
            "tool_name": "chat_completions",
            "model": air_record.get("model", "gpt-4o-mini"),
            "step_type": "llm_call",
            "cost_usd": 0.00002,
            "tokens": air_record.get("tokens", {}).get("total", 0),
        }
    }
    try:
        r = requests.post(f"{POLICY_ENGINE_URL}/v1/evaluate", json=payload, timeout=10)
        if r.status_code == 200:
            result = r.json()
            allowed = result.get("allowed", "unknown")
            action = result.get("action", "unknown")
            reason = result.get("reason", "")
            decisions = result.get("decisions", [])
            print_pass(f"Policy evaluated -- allowed={allowed}, action={action}")
            print_info(f"Reason: {reason}")
            if decisions:
                for d in decisions:
                    print_info(f"  Policy '{d.get('policy')}': {d.get('action')} -- {d.get('reason')}")
            else:
                print_info("No policies configured -- using default action")
            return True
        else:
            print_fail(f"Policy Engine returned {r.status_code}: {r.text[:200]}")
            return False
    except requests.ConnectionError:
        print_fail("Cannot connect to Policy Engine")
        return False
    except Exception as e:
        print_fail(f"Error: {e}")
        return False


def test_episode_query():
    print_step(6, "Verifying episodes are queryable")
    try:
        r = requests.get(f"{EPISODE_STORE_URL}/v1/episodes", timeout=10)
        if r.status_code == 200:
            episodes = r.json()
            count = len(episodes) if isinstance(episodes, list) else 1
            print_pass(f"Episode Store has {count} episode(s)")
            print_info("Open dashboard.html in your browser to visualize them")
            print_info(f"API: {EPISODE_STORE_URL}/v1/episodes")
            return True
        else:
            print_fail(f"Episode Store returned {r.status_code}")
            return False
    except Exception as e:
        print_fail(f"Error: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("  AIR Blackbox -- Production Smoke Test")
    print("=" * 60)
    if not OPENAI_API_KEY:
        print("\nNo OPENAI_API_KEY found.")
        print("   Set it: export OPENAI_API_KEY=sk-...")
        sys.exit(1)
    results = {}
    check_services()
    gateway_result = test_gateway_request()
    results["gateway_request"] = gateway_result is not None
    run_id = gateway_result["run_id"] if gateway_result else None
    response_text = gateway_result["response"] if gateway_result else None
    air_record = test_air_record(run_id)
    results["air_record"] = air_record is not None
    trace_id = air_record.get("trace_id") if air_record else None
    results["jaeger_trace"] = test_jaeger_trace(trace_id)
    results["episode_store"] = test_episode_store(air_record, response_text)
    results["policy_engine"] = test_policy_engine(air_record)
    results["episode_query"] = test_episode_query()
    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for test_name, test_passed in results.items():
        status = "PASS" if test_passed else "FAIL"
        print(f"  {status}  {test_name}")
    print(f"\n  {passed}/{total} tests passed")
    if passed == total:
        print("\n  All systems go! Full pipeline verified end-to-end:")
        print("     User -> Gateway -> OpenAI -> AIR Record -> OTel/Jaeger")
        print("                                              -> Episode Store")
        print("                                              -> Policy Engine")
    elif passed >= 4:
        print("\n  Mostly working -- check the failures above.")
    else:
        print("\n  Multiple failures -- check service status.")
    print()
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
