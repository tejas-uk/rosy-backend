from dotenv import load_dotenv
import os
from langchain_core.messages import AIMessage, HumanMessage
from states import AgentState

load_dotenv(dotenv_path=".env", override=True)

from initialize_agent import Agent

config = {"configurable": {"thread_id": "thread-12"}}
agent = Agent(config = config)


def run_agent():
    state = {"messages": []}
    while True:
        query = input("⛄️ You: ")

        if query.lower() == "exit":
            break

        state["messages"] = state.get("messages", []) + [HumanMessage(content=query)]
        response = agent(state)
        # Get the last message from the result
        last_message = next((m for m in reversed(response["messages"])
                            if isinstance(m, AIMessage)), None)
    
        if last_message:
            print(f"🧚‍♂️ Lily: {last_message.content}")
        else:
            print("🧚‍♂️ Lily: No response from the agent.")


if __name__ == "__main__":
    run_agent()