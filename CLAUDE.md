# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rosy (formerly Lily) is a conversational AI agent designed as a pediatric nurse to support expectant mothers and caregivers. It uses a graph-based LangGraph architecture with LangChain for multi-step reasoning, combining retrieval-augmented generation (RAG), web search, intelligent routing, and now includes FastAPI web service capabilities.

## Development Commands

### Running the Application
```bash
# CLI interface (main entry point)
python main.py

# FastAPI web service (production-ready)
python api.py

# Production initialization (for Render deployment)
python init_production.py
```

### Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Key dependencies: langgraph, langchain-core, langchain-openai, langchain-chroma, chromadb, 
# langchain-tavily, fastapi, uvicorn, psycopg, langgraph-checkpoint-postgres, pinecone, 
# langchain-pinecone, python-dotenv
```

### Development Tools
```bash
# Code formatting and linting (tools are installed but not configured)
python -m black .                    # Format code with Black
python -m flake8 .                   # Check style with Flake8
python -m mypy .                     # Type checking with MyPy
python -m pylint **/*.py             # Code analysis with Pylint
python -m isort .                    # Sort imports with isort

# Note: No testing framework is currently configured
# No pytest, unittest, or test files exist in the codebase
```

### Environment Setup
Copy `.env.example` to `.env` and configure:
- `OPENAI_API_KEY`: Required for LLM operations
- `TAVILY_API_KEY`: Required for web search functionality
- `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY`: For LangSmith tracing
- `CHECKPOINTER`: Set to "postgres" for PostgreSQL checkpointing, uses MemorySaver by default
- Vector DB settings: `COLLECTION_NAME`, `EMBEDDING_MODEL`, `PERSIST_DIR`
- Supabase settings: `SUPABASE_URL`, `SUPABASE_SESSION_POOLER`
- Pinecone settings: `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`

## Architecture

### Core Components

**Agent Workflow (initialize_agent.py:12-84)**
- LangGraph StateGraph orchestrates conversation flow
- Supports both memory-based and PostgreSQL checkpointing
- Graph visualization available via `agent.visualize_agent_graph()`

**State Management (states/state.py:5-9)**
- `AgentState` defines shared state across nodes
- Uses LangChain's `add_messages` for conversation history
- Tracks routing decisions and context from RAG/web search

**Agent Nodes (agents/)**
- `RouterNode`: Decides routing path (rag/web/answer/end) (agents/router.py)
- `RagJudgeNode`: Evaluates RAG relevance, can route to web search (agents/rag_judge.py)
- `WebSearchNode`: Performs web search when needed (agents/web_search.py)
- `AnswerNode`: Generates final response using context and Rosy persona (agents/answer.py)

### Key Patterns

**Node Implementation**
- All nodes implement `__call__(self, state: AgentState) -> AgentState`
- Router nodes include conditional edge methods (e.g., `from_router`)
- Use structured output with Pydantic models for routing decisions

**Tool Architecture**
- Tools inherit from LangChain's `BaseTool`
- Use `PrivateAttr` for non-serializable attributes
- Implement `_run(self, query: str) -> str` method

**Message Handling**
- Custom `LilyMessage` class for agent responses (messages/lily_message.py:5-15)
- Standard LangChain message types for user input
- Conversation history maintained in state

### Graph Flow
1. `router` → decision point based on query type
2. `rag_lookup` → retrieves relevant information, may route to web search
3. `web_search` → supplements RAG with current information
4. `answer` → generates response using accumulated context

## Adding New Components

### New Agent Node
1. Create class in `agents/` with `__call__` method
2. Add routing methods if needed (e.g., `after_my_node`)
3. Register in `agents/__init__.py`
4. Update graph in `initialize_agent.py` with `add_node` and edges

### New Tool
1. Inherit from `BaseTool` in `tools/`
2. Implement `_run` method
3. Use `PrivateAttr` for complex initialization
4. Register in `tools/__init__.py`

### Modifying Prompts
- System prompts stored in `prompts/` directory
- `rosy.md`: Main persona and behavior guidelines (formerly lily.md)
- `router.md`: Routing decision logic
- `judge.md`: RAG relevance evaluation

## Vector Database

Supports both ChromaDB and Pinecone for RAG with OpenAI embeddings:
- **ChromaDB**: Default option, stored in `pregnancy_and_parenting_chroma_db/`
- **Pinecone**: Cloud-based vector database for production deployments

The `BookRetrieverTool` (ChromaDB) and `PineconeBookRetrieverTool` handle vector search with configurable parameters.

## Persona and Behavior

Rosy is designed as a 20-year-old pediatric nurse from the US. Key behavioral traits:
- Warm, empathetic, never judgmental
- Proactively asks clarifying questions
- Provides medically accurate information
- Uses bubbly, reassuring tone for expectant mothers

Configuration in `prompts/rosy.md` defines conversation style and response guidelines.

## FastAPI Web Service

The `api.py` file provides a production-ready web service with the following endpoints:

### Authentication Options
- **Traditional**: Username/password authentication (`POST /users/register`, `POST /users/login`)
- **Simplified**: Username-only authentication (`POST /auth/username`) - auto-creates accounts

### Core Endpoints
- Chat thread management (`POST /chat/new`, `GET /users/{user_id}/chats`)
- Message sending and conversation history (`POST /chat/{user_id}/{thread_id}/message`, `GET /chat/{user_id}/{thread_id}`)
- Health checks (`GET /health`)

### Database Schema
- `lily_users`: Traditional users with password authentication
- `simple_users`: Username-only users (no password required)
- `chat_threads`: Supports both user types via `user_id` and `simple_user_id` columns

Database operations use PostgreSQL with Supabase for user management and chat persistence. See `API.md` for complete endpoint documentation and React/TypeScript client examples.

## Deployment

### Production Deployment (Render)
- `Procfile`: Defines web service command
- `init_production.py`: Initializes production database tables
- Uses PostgreSQL checkpointing for conversation persistence

### Database Utilities (`utils/`)
```bash
# Database management
python utils/init_db.py              # Initialize local development database
python utils/clear_checkpoints.py    # Clear conversation checkpoints
python utils/fix_constraints.py      # Fix database constraint issues
python utils/check_db.py             # Database health checks
python utils/graph_visualizaer.py    # Visualize agent graph structure
```