from dotenv import load_dotenv
import os
from langchain_core.messages import AIMessage

load_dotenv(dotenv_path=".env", override=True)

from initialize_agent import Agent

config = {"configurable": {"thread_id": "thread-12"}}
agent = Agent(config = config)

while True:
    query = input("⛄️ You: ")

    response = agent(query)
    # Get the last message from the result
    last_message = next((m for m in reversed(response["messages"])
                            if isinstance(m, AIMessage)), None)
    
    if last_message:
        print(f"🧚‍♂️ Lily: {last_message.content}")
    else:
        print("🧚‍♂️ Lily: No response from the agent.")