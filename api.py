from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uuid
import hashlib
import os
from typing import Optional, List
from initialize_agent import Agent
from langchain_core.messages import HumanMessage, AIMessage
import psycopg
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class ChatCreate(BaseModel):
    user_id: str

class MessageSend(BaseModel):
    message: str

class ChatResponse(BaseModel):
    thread_id: str
    user_id: str

class MessageResponse(BaseModel):
    type: str
    content: str
    timestamp: Optional[str] = None

class ChatHistory(BaseModel):
    thread_id: str
    user_id: str
    messages: List[MessageResponse]

# Database connection
def get_db_connection():
    """Get database connection for user management."""
    conn_string = os.getenv("SUPABASE_URL")
    if not conn_string:
        raise HTTPException(status_code=500, detail="Database connection not configured")
    return psycopg.connect(conn_string)

def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == hashed

# Initialize database tables
def init_db():
    """Initialize user management tables."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Create lily_users table (avoid conflict with Supabase auth.users)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS lily_users (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(64) NOT NULL,
                        email VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create chat_threads table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_threads (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        thread_id VARCHAR(100) UNIQUE NOT NULL,
                        user_id UUID REFERENCES lily_users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                print("Database tables initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Initialize DB on startup
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)

app = FastAPI(
    title="Lily Chat API", 
    description="Pediatric nurse AI chat API", 
    version="1.0.0",
    lifespan=lifespan
)

# User Management Endpoints
@app.post("/users/register", response_model=dict)
def register_user(user: UserCreate):
    """Create a new user account."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if username already exists
                cur.execute("SELECT id FROM lily_users WHERE username = %s", (user.username,))
                if cur.fetchone():
                    raise HTTPException(status_code=400, detail="Username already exists")
                
                # Create user
                password_hash = hash_password(user.password)
                cur.execute(
                    "INSERT INTO lily_users (username, password_hash, email) VALUES (%s, %s, %s) RETURNING id",
                    (user.username, password_hash, user.email)
                )
                user_id = cur.fetchone()[0]
                conn.commit()
                
                return {"user_id": str(user_id), "username": user.username, "message": "User created successfully"}
                
    except psycopg.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/users/login", response_model=dict)
def login_user(user: UserLogin):
    """Login existing user."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, password_hash FROM lily_users WHERE username = %s",
                    (user.username,)
                )
                result = cur.fetchone()
                
                if not result or not verify_password(user.password, result[1]):
                    raise HTTPException(status_code=401, detail="Invalid username or password")
                
                return {"user_id": str(result[0]), "username": user.username, "message": "Login successful"}
                
    except psycopg.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Chat Management Endpoints
@app.post("/chat/new", response_model=ChatResponse)
def create_chat(chat: ChatCreate):
    """Create a new chat thread for a user."""
    try:
        # Verify user exists
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM lily_users WHERE id = %s", (chat.user_id,))
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="User not found")
                
                # Create new thread
                thread_id = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO chat_threads (thread_id, user_id) VALUES (%s, %s)",
                    (thread_id, chat.user_id)
                )
                conn.commit()
                
                return ChatResponse(thread_id=thread_id, user_id=chat.user_id)
                
    except psycopg.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/chat/{user_id}/{thread_id}", response_model=ChatHistory)
def get_chat(user_id: str, thread_id: str):
    """Load existing chat conversation."""
    try:
        # Verify thread belongs to user
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT ct.thread_id FROM chat_threads ct WHERE ct.thread_id = %s AND ct.user_id = %s",
                    (thread_id, user_id)
                )
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="Chat thread not found")
        
        # Get conversation from checkpointer
        config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
        agent = Agent(config=config)
        
        # Try to get existing state
        try:
            state = agent.agent.get_state(config)
            messages = state.values.get("messages", []) if state.values else []
        except Exception:
            # If no state exists, return empty conversation
            messages = []
        
        # Convert messages to response format
        message_responses = []
        for msg in messages:
            message_responses.append(MessageResponse(
                type=msg.type,
                content=msg.content
            ))
        
        return ChatHistory(
            thread_id=thread_id,
            user_id=user_id,
            messages=message_responses
        )
        
    except psycopg.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/chat/{user_id}/{thread_id}/message", response_model=MessageResponse)
def send_message(user_id: str, thread_id: str, message: MessageSend):
    """Send a message to a chat thread."""
    try:
        # Verify thread belongs to user
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT ct.thread_id FROM chat_threads ct WHERE ct.thread_id = %s AND ct.user_id = %s",
                    (thread_id, user_id)
                )
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="Chat thread not found")
        
        # Process message with agent
        config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
        agent = Agent(config=config)
        
        # Create state with the new message
        state = {"messages": [HumanMessage(content=message.message)]}
        
        # Get response from agent
        response = agent(state)
        
        # Return the latest AI message
        ai_messages = [m for m in response["messages"] if m.type == "ai"]
        if not ai_messages:
            raise HTTPException(status_code=500, detail="No response generated")
        
        last_message = ai_messages[-1]
        return MessageResponse(
            type="ai",
            content=last_message.content
        )
        
    except psycopg.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Lily Chat API"}

# Get user's chat threads
@app.get("/users/{user_id}/chats")
def get_user_chats(user_id: str):
    """Get all chat threads for a user."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT thread_id, created_at FROM chat_threads WHERE user_id = %s ORDER BY created_at DESC",
                    (user_id,)
                )
                threads = cur.fetchall()
                
                return {
                    "user_id": user_id,
                    "threads": [
                        {"thread_id": thread[0], "created_at": thread[1].isoformat()}
                        for thread in threads
                    ]
                }
                
    except psycopg.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)