import ollama
from datetime import datetime


# ---------------------------------------------------------
# Application configuration
# ---------------------------------------------------------

MODEL_NAME = "llama3.2"
MAX_HISTORY_TURNS = 3

SYSTEM_PROMPT = """
You are an enterprise AI engineering assistant.
Answer clearly and accurately.
When the user asks a technical question, prefer practical examples.
If the available conversation context is insufficient, say so rather than inventing context.
""".strip()


# ---------------------------------------------------------
# Welcome message
# ---------------------------------------------------------

current_hour = datetime.now().hour

if current_hour < 12:
    greeting = "Good morning"
elif current_hour < 17:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"


print("=" * 60)
print("           🤖 ENTERPRISE AI ASSISTANT")
print("              Powered by Llama 3.2")
print("=" * 60)
print()
print(f"{greeting}, Raju! 👋")
print("Ask me anything. Type 'exit' to quit.")
print(f"Context policy: last {MAX_HISTORY_TURNS} turns")
print()


# ---------------------------------------------------------
# Conversation history
# ---------------------------------------------------------

messages = []


# ---------------------------------------------------------
# Context manager
# ---------------------------------------------------------

def build_context(history):
    """
    Build the context sent to the LLM.

    This is intentionally a simple sliding-window strategy.
    The application may retain a long conversation in memory,
    but only the most recent N turns are sent to the model.
    """

    recent_messages = history[-(MAX_HISTORY_TURNS * 2):]

    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        *recent_messages
    ]


# ---------------------------------------------------------
# Continuous chat
# ---------------------------------------------------------

while True:

    question = input("You: ")

    # Exit the application
    if question.lower() == "exit":
        print("\nGoodbye, Raju! 👋")
        break

    # Ignore empty input
    if not question.strip():
        print("Please enter a question.\n")
        continue

    # -----------------------------------------------------
    # Store user message in application history
    # -----------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # -----------------------------------------------------
    # Build the context actually sent to the LLM
    # -----------------------------------------------------

    context = build_context(messages)

    response = ollama.chat(
        model=MODEL_NAME,
        messages=context
    )

    # -----------------------------------------------------
    # Extract AI response
    # -----------------------------------------------------

    answer = response["message"]["content"]

    # -----------------------------------------------------
    # Store AI response in application history
    # -----------------------------------------------------

    messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    # -----------------------------------------------------
    # Display response
    # -----------------------------------------------------

    print("\nAI:", answer)

    # -----------------------------------------------------
    # LLM / context metrics
    # -----------------------------------------------------

    input_tokens = response.get("prompt_eval_count", 0)
    output_tokens = response.get("eval_count", 0)
    total_tokens = input_tokens + output_tokens

    print("\n--- AI Engineering Metrics ---")
    print(f"Total messages stored        : {len(messages)}")
    print(f"Messages sent to LLM         : {len(context)}")
    print(f"Input tokens for this request: {input_tokens}")
    print(f"Output tokens generated     : {output_tokens}")
    print(f"Total tokens                : {total_tokens}")
    print(f"History turns retained      : {MAX_HISTORY_TURNS}")
    print("------------------------------\n")
