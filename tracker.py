import json
import os
import sys
import time

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

load_dotenv()


PRICES = {
    "groq": {"input": 0.075, "output": 0.30},
    "openrouter": {"input": 0.08, "output": 0.20},
}


def get_env(name):
    value = os.getenv(name)
    if not value:
        print(f"Missing {name}. Add it to your .env file (see .env.example).")
        sys.exit(1)
    return value


def calc_cost(input_tokens, output_tokens, in_price, out_price):
    return (input_tokens * in_price / 1_000_000) + (output_tokens * out_price / 1_000_000)


def build_result(provider, model, reply, in_tok, out_tok, seconds):
    return {
        "provider": provider,
        "model": model,
        "reply": reply,
        "input_tokens": in_tok or 0,
        "output_tokens": out_tok or 0,
        "seconds": seconds,
        "input_price_per_m": PRICES[provider]["input"],
        "output_price_per_m": PRICES[provider]["output"],
    }


def call_groq(prompt):
    get_env("GROQ_API_KEY")
    model = get_env("GROQ_MODEL")
    client = Groq() 
    start = time.time()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    seconds = time.time() - start
    return build_result(
        "groq", model, resp.choices[0].message.content,
        resp.usage.prompt_tokens,
        resp.usage.completion_tokens,
        seconds,
    )


def call_openrouter(prompt):
    model = get_env("OPENROUTER_MODEL")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=get_env("OPENROUTER_API_KEY"),
    )
    start = time.time()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    seconds = time.time() - start
    return build_result(
        "openrouter", model, resp.choices[0].message.content,
        resp.usage.prompt_tokens,
        resp.usage.completion_tokens,
        seconds,
    )


def main():
    if len(sys.argv) < 2:
        print('Usage: uv run tracker.py "your prompt"')
        sys.exit(1)
    prompt = sys.argv[1]

    results = []
    for call in (call_groq, call_openrouter):
        r = call(prompt)
        r["cost_usd"] = calc_cost(
            r["input_tokens"], r["output_tokens"],
            r["input_price_per_m"], r["output_price_per_m"],
        )
        results.append(r)

    for r in results:
        print(f"\n--- {r['provider']} ({r['model']}) ---")
        print(r["reply"])

    print("\n{:<12} {:>8} {:>8} {:>8} {:>12}".format(
        "provider", "in_tok", "out_tok", "secs", "cost_usd"))
    for r in results:
        print("{:<12} {:>8} {:>8} {:>8.2f} {:>12.6f}".format(
            r["provider"], r["input_tokens"], r["output_tokens"],
            r["seconds"], r["cost_usd"]))
    print("\nNote: these calls used free tiers. Cost shown is what each call "
          "WOULD cost at the paid price.")

    fields = ["provider", "model", "reply", "input_tokens", "output_tokens",
              "input_price_per_m", "output_price_per_m", "cost_usd"]
    with open("results.json", "w") as f:
        json.dump([{k: r[k] for k in fields} for r in results], f, indent=2)


if __name__ == "__main__":
    main()