import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load OPENROUTER_API_KEY from .env into the environment
load_dotenv()

# Point the OpenAI client at OpenRouter instead of api.openai.com
client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)

# The question we want to ask
QUESTION = "What is the difference between machine learning and deep learning? Answer in 3 sentences."

MODELS = [
    "deepseek/deepseek-r1",
    "qwen/qwen3-235b-a22b",
]

# Input and output price in USD per million tokens (verify at openrouter.ai/models)
PRICES = {
    "deepseek/deepseek-r1":    {"in": 0.55,  "out": 2.19},
    "qwen/qwen3-235b-a22b":    {"in": 0.30,  "out": 1.20},
}


TIMEOUT = 60  # seconds before giving up on a model


def ask(question, model):
    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": question}],
        timeout=TIMEOUT,
    )
    latency = time.perf_counter() - start

    answer = response.choices[0].message.content
    in_tokens = response.usage.prompt_tokens
    out_tokens = response.usage.completion_tokens

    price = PRICES[model]
    cost = (in_tokens * price["in"] + out_tokens * price["out"]) / 1_000_000

    return answer, latency, in_tokens, out_tokens, cost


if __name__ == "__main__":
    PREVIEW_LEN = 80  # characters shown from each answer

    results = []
    for model in MODELS:
        print(f"Querying {model}...", flush=True)
        try:
            answer, latency, in_tokens, out_tokens, cost = ask(QUESTION, model)
            results.append({
                "model":   model,
                "preview": answer.replace("\n", " "),
                "latency": f"{latency:.2f}s",
                "cost":    f"${cost:.6f}",
                "error":   None,
            })
        except Exception as e:
            results.append({
                "model":   model,
                "preview": "",
                "latency": "-",
                "cost":    "-",
                "error":   str(e),
            })

    # Column widths derived from content
    col_model   = max(len(r["model"])   for r in results)
    col_latency = max(len(r["latency"]) for r in results)
    col_cost    = max(len(r["cost"])    for r in results)
    col_model   = max(col_model,   len("Model"))
    col_latency = max(col_latency, len("Latency"))
    col_cost    = max(col_cost,    len("Cost"))

    header = (
        f"{'Model':<{col_model}}  "
        f"{'Preview':<{PREVIEW_LEN}}  "
        f"{'Latency':>{col_latency}}  "
        f"{'Cost':>{col_cost}}"
    )
    divider = "-" * len(header)

    print()
    print(header)
    print(divider)
    for r in results:
        if r["error"]:
            preview = f"ERROR: {r['error']}"
        else:
            raw = r["preview"]
            preview = raw[:PREVIEW_LEN] if len(raw) <= PREVIEW_LEN else raw[:PREVIEW_LEN - 1] + "…"
        print(
            f"{r['model']:<{col_model}}  "
            f"{preview:<{PREVIEW_LEN}}  "
            f"{r['latency']:>{col_latency}}  "
            f"{r['cost']:>{col_cost}}"
        )
