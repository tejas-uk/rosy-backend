from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from agents import RouterNode, RagJudgeNode, AnswerNode, WebSearchNode
from states import AgentState
from langgraph.checkpoint.memory import MemorySaver
from utils.graph_visualizaer import save_graph, visualize_graph
from langchain_core.messages import HumanMessage
from typing import Optional


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
                "end": END
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
            checkpointer = MemorySaver(),
        )

        self.config = config

    def visualize_agent_graph(self):
        visualize_graph(self.agent)

    def save_agent_graph(self, path: str):
        save_graph(self.agent, path)

    def __call__(self, query: str):
        response = self.agent.invoke(
            {"messages": [HumanMessage(content=query)]},
            config = self.config
        )
        return response