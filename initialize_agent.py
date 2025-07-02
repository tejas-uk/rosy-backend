from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from agents import RouterNode, RagJudgeNode, AnswerNode, WebSearchNode
from states import AgentState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from utils.graph_visualizaer import save_graph, visualize_graph
from langchain_core.messages import HumanMessage
from typing import Optional
import os

class Agent:
    def __init__(self, config: Optional[dict] = None):
        self.router = RouterNode()
        self.rag_lookup = RagJudgeNode()
        self.web_search = WebSearchNode()
        self.answer = AnswerNode()

        self.graph = StateGraph(AgentState)

        self.graph.add_node("router", self.router)
        self.graph.add_node("rag_lookup", self.rag_lookup)
        self.graph.add_node("web_search", self.web_search)
        self.graph.add_node("answer", self.answer)

        self.graph.set_entry_point("router")

        self.graph.add_conditional_edges(
            "router", 
            self.router.from_router,
            {
                "rag": "rag_lookup",
                "web": "web_search",
                "answer": "answer",
            }
        )

        self.graph.add_conditional_edges(
            "rag_lookup",
            self.rag_lookup.after_rag,
            {
                "answer": "answer",
                "web": "web_search"
            }
        )

        self.graph.add_edge("web_search", "answer")

        self.graph.add_edge("answer", END)
        
        self.agent = self.graph.compile(
            checkpointer = self._init_checkpointer(),
        )

        self.config = config

    def _init_checkpointer(self):
        if os.getenv("CHECKPOINTER") == "postgres":
            # print ("-"*60)
            # print("Using PostgresSaver")
            # print(f"Connection String: {os.getenv('SUPABASE_URL')}")
            # PostgresSaver.from_conn_string returns a context manager
            # We need to enter the context and keep the connection alive
            checkpointer_cm = PostgresSaver.from_conn_string(
                os.getenv("SUPABASE_URL")
            )
            checkpointer = checkpointer_cm.__enter__()
            # print(f"Checkpointer: {checkpointer}")
            # print("Setting up checkpointer tables")
            checkpointer.setup()
            # print ("-"*60)
            # Store the context manager for later cleanup if needed
            self._checkpointer_cm = checkpointer_cm
        else:
            checkpointer = MemorySaver()
        return checkpointer
        
    def visualize_agent_graph(self):
        visualize_graph(self.agent)

    def save_agent_graph(self, path: str):
        save_graph(self.agent, path)

    def __call__(self, state: AgentState):
        response = self.agent.invoke(
            state,
            config = self.config
        )
        return response
