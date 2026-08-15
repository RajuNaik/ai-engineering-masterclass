import ollama
from datetime import datetime


# ---------------------------------------------------------
# Application configuration
# ---------------------------------------------------------

MODEL_NAME = "llama3.2"
MAX_HISTORY_TURNS = 3
SUMMARY_TRIGGER_TURNS = 4

SYSTEM_PROMPT = """
You are an enterprise AI engineering assistant.
Answer clearly and accurately.
When the user asks a technical question, prefer practical examples.
Use the supplied conversation summary and recent messages as context.
If the available context is insufficient, say so rather than inventing context.
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
print(f"Context policy: recent {MAX_HISTORY_TURNS} turns + summary")
print()


# ---------------------------------------------------------
# Application state
# ---------------------------------------------------------

messages = []
conversation_summary = ""


# ---------------------------------------------------------
# Context compaction / summarization
# ---------------------------------------------------------

def compact_history(history, existing_summary):
    """
    Compact older conversation into a rolling summary.

    We retain the most recent N turns as raw messages and summarize
    older turns so important information can survive context reduction.
    """

    keep_message_count = MAX_HISTORY_TURNS * 2

    if len(history) <= keep_message_count:
        return existing_summary, history

    older_messages = history[:-keep_message_count]
    recent_messages = history[-keep_message_count:]

    older_text = "\n".join(
        f"{message['role'].upper()}: {message['content']}"
        for message in older_messages
    )

    if existing_summary:
        summary_instruction = f"""
Existing conversation summary:
{existing_summary}

Update this summary using the older conversation below.
Preserve important facts, decisions, user requirements, terminology,
open questions, and references that may be needed later.
Do not invent information.
"""
    else:
        summary_instruction = """
Create a concise conversation summary for future context.
Preserve important facts, decisions, user requirements, terminology,
open questions, and references that may be needed later.
Do not invent information.
"""

    summary_prompt = f"""
{summary_instruction}

Older conversation:
{older_text}

Return only the updated summary.
"""

    summary_response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a conversation-compaction component for an enterprise AI system."
            },
            {
                "role": "user",
                "content": summary_prompt
            }
        ]
    )

    new_summary = summary_response["message"]["content"].strip()

    return new_summary, recent_messages


# ---------------------------------------------------------
# Context manager
# ---------------------------------------------------------

def build_context(history, summary):
    """Build the final context sent to the LLM."""

    recent_messages = history[-(MAX_HISTORY_TURNS * 2):]

    context = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    if summary:
        context.append(
            {
                "role": "system",
                "content": f"Conversation summary:\n{summary}"
            }
        )

    context.extend(recent_messages)

    return context


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
    # Compact older history when the context grows
    # -----------------------------------------------------

    completed_turns = len(messages) // 2

    if completed_turns >= SUMMARY_TRIGGER_TURNS:
        conversation_summary, messages = compact_history(
            messages,
            conversation_summary
        )

    # -----------------------------------------------------
    # Build the context actually sent to the LLM
    # -----------------------------------------------------

    context = build_context(messages, conversation_summary)

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
    print(f"Recent messages in memory  : {len(messages)}")
    print(f"Messages sent to LLM       : {len(context)}")
    print(f"Input tokens               : {input_tokens}")
    print(f"Output tokens              : {output_tokens}")
    print(f"Total tokens               : {total_tokens}")
    print(f"Summary available          : {'Yes' if conversation_summary else 'No'}")
    print(f"Recent turns retained      : {MAX_HISTORY_TURNS}")
    print("------------------------------\n")
