import ollama
from datetime import datetime


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
print()


# ---------------------------------------------------------
# Conversation history
# ---------------------------------------------------------

messages = []


# ---------------------------------------------------------
# Continuous chat
# ---------------------------------------------------------

while True:

    question = input("You: ")

    # Exit the application
    if question.lower() == "exit":
        print("\nGoodbye, Raju! 👋")
        break

    # Add user's message to conversation history
    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Send conversation history to Llama
    response = ollama.chat(
        model="llama3.2",
        messages=messages
    )

    # Extract AI response
    answer = response["message"]["content"]

    # Add AI response to conversation history
    messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    # Display AI response
    print("\nAI:", answer)
    print()