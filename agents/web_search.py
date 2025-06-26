from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from states import AgentState
from langchain_core.messages import HumanMessage
from tools import WebSearchTool

class WebSearchNode:
    def __init__(self):
        self.web_tool = WebSearchTool()

    def __call__(self, state: AgentState) -> AgentState:
        query = next((m.content for m in reversed(state["messages"])
                      if isinstance(m, HumanMessage)), "")

        search_results = self.web_tool.invoke({"query": query})
        
        return {
            **state,
            "web": search_results,
            "route": "answer"
        }