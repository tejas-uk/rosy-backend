from fastapi import FastAPI, HTTPException
import uuid
from initialize_agent import Agent

app = FastAPI()

@app.post("/chat/new")
def create_chat(user_id: str):
    thread_id = str(uuid.uuid4())
    # Optionally: create an initial state in DB
    # agent = Agent(user_id=user_id, thread_id=thread_id)
    # agent.memory.save_state(
    #     {"configurable": {"thread_id": thread_id, "user_id": user_id}},
    #     {"messages": []}
    # )
    return {"thread_id": thread_id, "user_id": user_id}

@app.get("/chat/{user_id}/{thread_id}")
def get_chat(user_id: str, thread_id: str):
    agent = Agent(user_id=user_id, thread_id=thread_id)
    # Retrieve state from persistent checkpointer (Supabase)
    state = agent.memory.get_state({"configurable": {"thread_id": thread_id, "user_id": user_id}})
    messages = state.values.get("messages", [])
    return {"messages": [m.content for m in messages]}

@app.post("/chat/{user_id}/{thread_id}/message")
def send_message(user_id: str, thread_id: str, message: str):
    agent = Agent(user_id=user_id, thread_id=thread_id)
    response = agent(message)
    # Return the latest AI message
    last_message = next((m for m in reversed(response["messages"]) if m.type == "ai"), None)
    return {"response": last_message.content if last_message else "Something went wrong"}