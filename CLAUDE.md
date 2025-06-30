# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lily is a conversational AI agent designed as a pediatric nurse to support expectant mothers and caregivers. It uses a graph-based LangGraph architecture with LangChain for multi-step reasoning, combining retrieval-augmented generation (RAG), web search, and intelligent routing.

## Development Commands

### Running the Application
```bash
# CLI interface (main entry point)
python main.py

# FastAPI server (in development)
# Note: api.py has incomplete implementation
```

### Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Key dependencies: langgraph, langchain-core, langchain-openai, chromadb, python-dotenv
```

### Environment Setup
Copy `.env.example` to `.env` and configure:
- `OPENAI_API_KEY`: Required for LLM operations
- `TAVILY_API_KEY`: Required for web search functionality
- `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY`: For LangSmith tracing
- `CHECKPOINTER=postgres`: Optional, uses MemorySaver by default
- Vector DB settings: `COLLECTION_NAME`, `EMBEDDING_MODEL`, `PERSIST_DIR`

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
- `RouterNode`: Decides routing path (rag/web/answer/end)
- `RagJudgeNode`: Evaluates RAG relevance, can route to web search
- `WebSearchNode`: Performs web search when needed
- `AnswerNode`: Generates final response using context and Lily persona

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
- Custom `LilyMessage` class for agent responses (messages/lily_message.py)
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
- `lily.md`: Main persona and behavior guidelines
- `router.md`: Routing decision logic
- `judge.md`: RAG relevance evaluation

## Vector Database

Uses ChromaDB for RAG with OpenAI embeddings. Database stored in `pregnancy_and_parenting_chroma_db/`. The `BookRetrieverTool` handles vector search with configurable parameters.

## Persona and Behavior

Lily is designed as a 20-year-old pediatric nurse from the US. Key behavioral traits:
- Warm, empathetic, never judgmental
- Proactively asks clarifying questions
- Provides medically accurate information
- Uses bubbly, reassuring tone for expectant mothers

Configuration in `prompts/lily.md` defines conversation style and response guidelines.