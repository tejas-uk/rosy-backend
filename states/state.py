from typing import TypedDict, Literal
from langchain_core.messages import BaseMessage

class AgentState(TypedDict, total=False):
    messages: list[BaseMessage]
    route: Literal["rag", "answer", "end"]
    rag: str
    web: str