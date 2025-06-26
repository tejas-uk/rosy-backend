# Lily: Nurture-Guide Conversational Agent

## Project Overview
Lily is an empathetic, pediatric nurse-inspired conversational agent designed to support moms and caregivers with pregnancy and early childhood questions. The system uses a modular, graph-based agent architecture with retrieval-augmented generation (RAG), web search, and custom routing logic.

## Directory Structure
```
main.py                        # Entry point for the CLI chat interface
initialize_agent.py            # Defines and compiles the agent workflow graph
agents/                        # Agent node implementations (router, answer, RAG judge, web search)
tools/                         # Custom tools (book retriever, web search)
states/                        # Agent state definitions
utils/                         # Utilities (e.g., graph visualization)
prompts/                       # Prompt templates for agents
image/                         # Project images (e.g., first_agent.png)
pregnancy_and_parenting_chroma_db/ # Vector DB and data files for RAG
```

## Creating a New Tool
1. **Create the Tool Class**: Inherit from `BaseTool` in a new file under `tools/`.
2. **Implement `_run(self, query: str)`**: This method should execute the tool's core logic.
3. **Register the Tool**: Add an import in `tools/__init__.py`.
4. **Use in Agents**: Instantiate and use your tool in the relevant agent node (e.g., in `agents/`).

**Example:**
```python
# tools/my_tool.py
from langchain_core.tools import BaseTool
class MyTool(BaseTool):
    name = "my_tool"
    description = "Describe what your tool does."
    def _run(self, query: str) -> str:
        # Tool logic here
        return "result"
```

## Creating a New Agent Node
1. **Create the Node Class**: Inherit from `object` (or a base node class) in `agents/`.
2. **Implement `__call__(self, state: AgentState) -> AgentState`**: This method processes the state and returns the updated state.
3. **(Optional) Add Routing Methods**: If your node routes to others, add methods like `from_router` or `after_<node>`.
4. **Register the Node**: Add an import in `agents/__init__.py`.

**Example:**
```python
# agents/my_agent.py
from states import AgentState
class MyAgentNode:
    def __call__(self, state: AgentState) -> AgentState:
        # Node logic here
        return state
```

## Updating the Graph in `initialize_agent.py`
1. **Add Your Node**: Instantiate your node in the `Agent.__init__` method.
2. **Register the Node in the Graph**:
   - `self.graph.add_node("my_node", self.my_node)`
3. **Add Edges**: Use `add_edge` or `add_conditional_edges` to define transitions.
4. **Set Entry/Exit Points**: Use `set_entry_point` and connect to `END` as needed.
5. **Recompile the Agent**: The graph is compiled with `self.graph.compile()`.

**Example:**
```python
self.my_node = MyAgentNode()
self.graph.add_node("my_node", self.my_node)
self.graph.add_edge("my_node", "answer")
```

## Logging with Lang Smith
Lily supports logging and tracing via Lang Smith. To enable logging, set the following environment variables in your `.env` file:

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=your-project-name
```

> **Note:** Logging is enabled by environment variable initialization only. No explicit logging code is present; LangChain/LangSmith will pick up these variables automatically.

## Running the Project
1. Install dependencies (see requirements.txt, not included here).
2. Set up your `.env` file with required API keys and Lang Smith variables.
3. Run the CLI:
   ```bash
   python main.py
   ```
4. Interact with Lily in the terminal.

## Visualizing the Agent Graph
You can visualize or save the agent workflow graph:
```python
agent = Agent()
agent.visualize_agent_graph()  # Show graph (requires Jupyter/IPython)
agent.save_agent_graph("graph.png")  # Save as PNG
```

---

For further customization, see the code in `initialize_agent.py`, `agents/`, and `tools/`. 