import logging
import os
import re

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi


# -------------------------
# Load API key
# -------------------------
# Loads values from `.env` into environment variables.
load_dotenv()
# Creates a reusable OpenAI client for all API calls in this script.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# Logging setup
# -------------------------
logging.basicConfig(filename="logs.txt", level=logging.INFO)

# -------------------------
# Text preprocessing
# -------------------------
def preprocess(text):
    # Normalize text so retrieval is based on consistent lowercase word tokens.
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.split()


# -------------------------
# Load Excel dataset
# -------------------------
# Reads the complaint examples that act as the knowledge base.
df = pd.read_excel("Complaint Dataset.xlsx")

dataset = []

for _, row in df.iterrows():
    # Keep each row in a simpler structure for retrieval and prompt building.
    dataset.append(
        {
            "title": row["Category"],
            "trouble": row["Trouble"],
            "solution": row["Solution"],
            "alternate_solution": row["Alternate Solution"],
            "company_response": row["Company Response"],
            "content": f"""
Trouble: {row['Trouble']}
Solution: {row['Solution']}
Alternate Solution: {row['Alternate Solution']}
Company Response: {row['Company Response']}
""",
        }
    )

# -------------------------
# Build BM25 index (ONLY Trouble column)
# -------------------------
# BM25 is a keyword search algorithm; only the "Trouble" field is indexed here.
corpus = [preprocess(item["trouble"]) for item in dataset]
bm25 = BM25Okapi(corpus)


# -------------------------
# Retrieve top documents
# -------------------------
def retrieve_docs(query, k=3):
    # Convert the user complaint into the same token format as the indexed data.
    tokenized_query = preprocess(query)
    scores = bm25.get_scores(tokenized_query)

    ranked = sorted(
        [(i, scores[i]) for i in range(len(scores))],
        key=lambda x: x[1],
        reverse=True,
    )

    top_k = ranked[:k]

    results = []
    for idx, score in top_k:
        results.append((dataset[idx], score))
        # Use ASCII-only debug output so it works reliably in Windows terminals.
        print(f"[BM25] {dataset[idx]['trouble']} -> {score:.3f}")

    return results


# -------------------------
# Check low confidence
# -------------------------
def is_low_confidence(scores, threshold=0.3):
    # If the best retrieval score is too small, the script prefers escalation.
    return max(scores) < threshold


# -------------------------
# Build context
# -------------------------
def build_context(docs):
    # Merge the retrieved complaint records into one text block for the model.
    context = ""
    for d in docs:
        context += f"""
Customer Issue Type: {d['trouble']}
{d['content']}
---
"""
    return context


# -------------------------
# Prompt builder
# -------------------------
def build_prompt(mode, context, query):
    if mode == "strict":
        # Strict mode aims for a short, policy-grounded answer.
        return (
            f"""
You are a professional customer support assistant.
Use ONLY the provided policy context.
Do not add extra assumptions.

Context:
{context}

Customer Issue:
{query}

Give a clear and concise answer.
""",
            0.2,
            150,
        )

    if mode == "friendly":
        # Friendly mode allows a warmer tone and slightly more flexible output.
        return (
            f"""
You are a polite and empathetic support agent.
Use the policy context but respond in a friendly tone.

Context:
{context}

Customer Issue:
{query}
""",
            0.7,
            200,
        )

    # Default to strict mode if the caller passes an unsupported value.
    return build_prompt("strict", context, query)


# -------------------------
# Call OpenAI
# -------------------------
def generate_response(prompt, temperature, max_tokens):
    # Send the final prompt to the model and return only the generated message text.
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content


# -------------------------
# Main pipeline
# -------------------------
def handle_query(query, mode="strict"):
    # Step 1: find the most relevant complaint examples from the dataset.
    results = retrieve_docs(query)

    docs = [r[0] for r in results]
    scores = [r[1] for r in results]
    # Pair each retrieved document with its score so the UI can display both.
    retrieved_items = [
        {
            "title": doc["title"],
            "trouble": doc["trouble"],
            "solution": doc["solution"],
            "alternate_solution": doc["alternate_solution"],
            "company_response": doc["company_response"],
            "content": doc["content"],
            "score": float(score),
        }
        for doc, score in results
    ]

    # Fallback
    if is_low_confidence(scores):
        # Step 2: if retrieval is weak, avoid guessing and escalate to a human.
        return {
            "response": "Please escalate this issue to a human support agent.",
            "docs": docs,
            "retrieved_items": retrieved_items,
        }

    # Step 3: turn retrieved examples into context for the language model.
    context = build_context(docs)

    # Step 4: create the prompt and generation settings for the selected mode.
    prompt, temp, max_tok = build_prompt(mode, context, query)

    # Step 5: generate the final support response.
    try:
        response = generate_response(prompt, temp, max_tok)
    except Exception as exc:
        # If the model call fails, fall back to the closest known company response.
        logging.exception("OpenAI generation failed")
        response = docs[0]["company_response"] or "Please escalate this issue to a human support agent."
        return {
            "response": response,
            "docs": docs,
            "retrieved_items": retrieved_items,
            "warning": f"Model generation failed, so the closest known response was used instead: {exc}",
        }

    # Logging
    # Store the full run details so you can inspect behavior later in logs.txt.
    logging.info(
        f"""
QUERY: {query}
MODE: {mode}
DOCS: {docs}
PROMPT: {prompt}
TEMP: {temp}
MAX_TOKENS: {max_tok}
RESPONSE: {response}
----------------------
"""
    )

    return {
        "response": response,
        "docs": docs,
        "retrieved_items": retrieved_items,
    }


# -------------------------
# Test run
# -------------------------
if __name__ == "__main__":
    # Simple command-line loop for trying multiple complaints one after another.
    while True:
        query = input("\nEnter customer complaint: ")
        mode = input("Mode (strict/friendly): ")

        result = handle_query(query, mode)

        print("\n--- AI RESPONSE ---")
        print(result["response"])

        print("\n--- RETRIEVED DOCS ---")
        for d in result["docs"]:
            print("-", d["trouble"])
