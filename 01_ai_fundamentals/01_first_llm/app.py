import uuid
from datetime import datetime

import ollama

from database import (
    conversation_exists,
    create_conversation,
    get_conversation_state,
    initialize_database,
    load_messages,
    save_conversation_summary,
    save_message,
)


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
# Database initialization
# ---------------------------------------------------------

initialize_database()


# ---------------------------------------------------------
# Session / conversation selection
# ---------------------------------------------------------

print("=" * 60)
print("           🤖 ENTERPRISE AI ASSISTANT")
print("              Powered by Llama 3.2")
print("=" * 60)
print()

current_hour = datetime.now().hour

if current_hour < 12:
    greeting = "Good morning"
elif current_hour < 17:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

print(f"{greeting}, Raju! 👋")
print()
print("Conversation persistence is enabled.")
print("Press Enter to start a new conversation.")
print("Or enter an existing conversation ID to resume it.")
print()

conversation_id = input("Conversation ID: ").strip()

if conversation_id:
    if not conversation_exists(conversation_id):
        print("Conversation not found. Starting a new conversation.")
        conversation_id = str(uuid.uuid4())
        create_conversation(conversation_id)
    else:
        print("Existing conversation loaded.")
else:
    conversation_id = str(uuid.uuid4())
    create_conversation(conversation_id)
    print("New conversation created.")

print(f"Conversation ID: {conversation_id}")
print(f"Context policy: recent {MAX_HISTORY_TURNS} turns + summary")
print("Ask me anything. Type 'exit' to quit.")
print()


# ---------------------------------------------------------
# Conversation state
# ---------------------------------------------------------

conversation_state = get_conversation_state(conversation_id)
conversation_summary = conversation_state["summary"]
summary_through_message_id = conversation_state[
    "summary_through_message_id"
]


# ---------------------------------------------------------
# Context compaction / summarization
# ---------------------------------------------------------

def compact_history(history, existing_summary, last_summarized_id):
    """
    Compact older persisted history into a rolling summary.

    Raw messages remain permanently stored in SQLite.
    Only the model context is compacted.
    """

    keep_message_count = MAX_HISTORY_TURNS * 2

    if len(history) <= keep_message_count:
        return existing_summary, last_summarized_id

    cutoff_index = len(history) - keep_message_count
    candidate_messages = history[:cutoff_index]

    # Only summarize messages that have not already been compacted.
    unsummarized_messages = [
        message
        for message in candidate_messages
        if last_summarized_id is None
        or message["message_id"] > last_summarized_id
    ]

    if not unsummarized_messages:
        return existing_summary, last_summarized_id

    older_text = "\n".join(
        f"{message['role'].upper()}: {message['content']}"
        for message in unsummarized_messages
    )

    if existing_summary:
        summary_instruction = f"""
Existing conversation summary:
{existing_summary}

Update the summary using the new older conversation below.
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

Older conversation to incorporate:
{older_text}

Return only the updated summary.
"""

    summary_response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a conversation-compaction component "
                    "for an enterprise AI system."
                ),
            },
            {
                "role": "user",
                "content": summary_prompt,
            },
        ],
    )

    new_summary = summary_response["message"]["content"].strip()

    new_last_summarized_id = unsummarized_messages[-1]["message_id"]

    return new_summary, new_last_summarized_id


# ---------------------------------------------------------
# Context manager
# ---------------------------------------------------------

def build_context(history, summary):
    """Build the bounded context actually sent to the LLM."""

    recent_messages = history[-(MAX_HISTORY_TURNS * 2):]

    context = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    if summary:
        context.append(
            {
                "role": "system",
                "content": f"Conversation summary:\n{summary}",
            }
        )

    context.extend(
        {
            "role": message["role"],
            "content": message["content"],
        }
        for message in recent_messages
    )

    return context


# ---------------------------------------------------------
# Continuous chat
# ---------------------------------------------------------

while True:

    question = input("You: ").strip()

    # Exit the application
    if question.lower() == "exit":
        print("\nGoodbye, Raju! 👋")
        print(f"Your conversation ID is: {conversation_id}")
        print("You can use it to resume this conversation later.")
        break

    # Ignore empty input
    if not question:
        print("Please enter a question.\n")
        continue

    # -----------------------------------------------------
    # Persist user message
    # -----------------------------------------------------

    save_message(
        conversation_id,
        "user",
        question,
    )

    # -----------------------------------------------------
    # Load complete raw history from persistent storage
    # -----------------------------------------------------

    history = load_messages(conversation_id)

    # -----------------------------------------------------
    # Compact older context when needed
    # -----------------------------------------------------

    completed_turns = len(history) // 2

    if completed_turns >= SUMMARY_TRIGGER_TURNS:
        (
            conversation_summary,
            summary_through_message_id,
        ) = compact_history(
            history,
            conversation_summary,
            summary_through_message_id,
        )

        save_conversation_summary(
            conversation_id,
            conversation_summary,
            summary_through_message_id,
        )

    # -----------------------------------------------------
    # Build bounded model context
    # -----------------------------------------------------

    context = build_context(
        history,
        conversation_summary,
    )

    # -----------------------------------------------------
    # Call Llama
    # -----------------------------------------------------

    response = ollama.chat(
        model=MODEL_NAME,
        messages=context,
    )

    # -----------------------------------------------------
    # Extract response
    # -----------------------------------------------------

    answer = response["message"]["content"]

    # -----------------------------------------------------
    # Persist assistant response
    # -----------------------------------------------------

    save_message(
        conversation_id,
        "assistant",
        answer,
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

    latest_history = load_messages(conversation_id)

    print("\n--- AI Engineering Metrics ---")
    print(f"Conversation ID            : {conversation_id}")
    print(f"Messages persisted         : {len(latest_history)}")
    print(f"Messages sent to LLM       : {len(context)}")
    print(f"Input tokens               : {input_tokens}")
    print(f"Output tokens              : {output_tokens}")
    print(f"Total tokens               : {total_tokens}")
    print(
        f"Summary available          : "
        f"{'Yes' if conversation_summary else 'No'}"
    )
    print(f"Recent turns retained      : {MAX_HISTORY_TURNS}")
    print("------------------------------\n")
