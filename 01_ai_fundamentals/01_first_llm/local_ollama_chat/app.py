"""Standalone local Ollama chat application.

Implementation will be expanded incrementally to add:
- last-5-message context
- persisted conversation history in ADLS Gen2
- persisted summary
- seven-day cleanup
"""

import ollama

MODEL_NAME = "llama3.2"


def chat(prompt: str) -> str:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]


if __name__ == "__main__":
    prompt = input("You: ")
    answer = chat(prompt)
    print(f"Assistant: {answer}")
