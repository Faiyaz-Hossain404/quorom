#!/usr/bin/env python3
"""Day-1 Qwen verification harness.

Run this the moment you have a Model Studio API key — it confirms the
qwen-flash -> qwen-max cascade works before you deploy anything.

    # from quorum/  (key in .env or exported)
    pip install -r engine/requirements.txt
    python engine/scripts/verify_qwen.py
"""

import os
import sys
import time

try:
    from openai import OpenAI
except ImportError:
    sys.exit("openai not installed. Run: pip install -r engine/requirements.txt")

try:
    from dotenv import load_dotenv

    load_dotenv()  # repo-root .env if present
except Exception:
    pass

API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
BASE_URL = os.getenv(
    "DASHSCOPE_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)
MODELS = {
    "flash": os.getenv("QWEN_MODEL_FLASH", "qwen-flash"),
    "max": os.getenv("QWEN_MODEL_MAX", "qwen-max"),
}


def main() -> int:
    if not API_KEY:
        print("FAIL: DASHSCOPE_API_KEY is not set.")
        print("  Set it in the environment or in quorum/.env, then re-run.")
        return 1

    print(f"Endpoint: {BASE_URL}")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    all_ok = True

    for tier, model in MODELS.items():
        print(f"\n--- {tier} ({model}) ---")
        try:
            t0 = time.perf_counter()
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Reply with exactly: Quorum online."}],
                max_tokens=64,
            )
            ms = round((time.perf_counter() - t0) * 1000)
            u = resp.usage
            print(
                f"OK  {ms} ms | tokens in/out/total: "
                f"{u.prompt_tokens}/{u.completion_tokens}/{u.total_tokens}"
            )
            print(f"    response: {resp.choices[0].message.content!r}")
        except Exception as exc:
            all_ok = False
            print(f"FAIL: {type(exc).__name__}: {exc}")
            print("  Check: base_url matches your region, the model is enabled in")
            print("  Model Studio, and the key has access.")

    print("\nRESULT:", "ALL PASS — Qwen gate cleared." if all_ok else "FAILED — see above.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
