# Assignment 1: Two Provider Cost Tracker

A Python script that sends the same prompt to two LLM providers (Groq and
OpenRouter), then prints each reply, the token counts, the time taken, and
the cost of each call. It also saves everything to `results.json`.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) installed
- A free Groq API key (console.groq.com)
- A free OpenRouter API key (openrouter.ai)

## Setup

1. Clone the repo and enter the folder:

   git clone https://github.com/KhurramRaja35/a1-cost-tracker.git
   cd a1-cost-tracker

2. Install the packages:

   uv sync

3. Copy the example env file and fill in your own values:

   copy .env.example .env        (Windows)
   cp .env.example .env          (Mac and Linux)

4. Set these variables in `.env`:

   | GROQ_API_KEY | Your Groq key |
   | GROQ_MODEL | Groq model id, for example openai/gpt-oss-20b |
   | OPENROUTER_API_KEY | Your OpenRouter key |
   | OPENROUTER_MODEL | An OpenRouter model id, for example nvidia/nemotron-3.5-lightning:free |

   `.env` is listed in `.gitignore` and is never committed.

## Run

    uv run tracker.py "Explain tokens in one sentence."

If a key or model name is missing, the script prints a clear message
telling you which variable to add.

## Sample output

--- groq (openai/gpt-oss-20b) ---
Tokens are the basic units of text—usually words or subwords—that a language model splits input into to process and generate language.

--- openrouter (nvidia/nemotron-3.5-lightning:free) ---
Tokens are the basic text units—such as words, subwords, or characters—that AI models convert into numerical representations for processing and generation.

provider       in_tok  out_tok     secs     cost_usd
groq               77       74     1.36     0.000028
openrouter         23      325     4.36     0.000067

A copy of the structured results is saved to `results.json`, with one
object per provider: provider, model, reply, input_tokens, output_tokens,
input_price_per_m, output_price_per_m, cost_usd.

## How cost is calculated

    cost = input_tokens x input_price / 1,000,000
         + output_tokens x output_price / 1,000,000

Token counts come from each API's usage data, never estimated. Prices are
USD per 1 million tokens (paid tier) and are set in the PRICES dictionary
in `tracker.py`:

- Groq openai/gpt-oss-20b: $0.075 input, $0.30 output (source: Groq's
  models page, checked on 11-22-2026)
- OpenRouter nvidia/nemotron-3.5-lightning: $0.08 input, $0.20
  output (source: OpenRouter model page, checked on 11-22-2026)

Both calls ran on free tiers, so they cost nothing. As the assignment
requires, the cost column shows what each call would cost at the paid
price, and the script labels it that way.
