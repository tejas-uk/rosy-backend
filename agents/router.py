from pydantic import BaseModel, Field
from typing import Literal
from langchain_openai import ChatOpenAI
from states import AgentState
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import pathlib

class RouteDecision(BaseModel):
    route: Literal["rag", "answer", "end", "web"]
    reply: str | None = Field(None, description="Filled only when route == end")

class RouterNode:
    def __init__(
            self, 
            model_name: str = "gpt-4o", 
            temperature: float = 0.7
        ):
        self.router_llm = ChatOpenAI(model=model_name, temperature=temperature)\
            .with_structured_output(RouteDecision)

    def __call__(self, state: AgentState) -> AgentState:
        query = next((m.content for m in reversed(state["messages"])
                      if isinstance(m, HumanMessage)), "")
        
        ROOT = pathlib.Path(__file__).parents[1]
        ROUTER_PROMPT = (ROOT / "prompts" / "router.md").read_text(encoding="utf-8")

        # messages = [
        #     ("system", 
        #      ROUTER_PROMPT),
        #     ("user", query)
        # ]
        messages = [
            SystemMessage(content=ROUTER_PROMPT),
            HumanMessage(content=query)
        ]

        result: RouteDecision = self.router_llm.invoke(messages)

        out = {"messages": state["messages"], "route": result.route}
        # if result.route == "end":
        #     out["messages"] = state["messages"] + [ AIMessage(content=result.reply or "Hello!") ]

        return out
    
    def from_router(self, state: AgentState) -> Literal["rag", "answer", "web"]:
        return state["route"]

# Usage in LangGraph:
# g.add_node("router", RouterNode())