from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from states import AgentState
from langchain_core.messages import HumanMessage, SystemMessage
from tools import PineconeBookRetrieverTool
from typing import Literal
import pathlib

class RagJudge(BaseModel):
    sufficient: bool
    use_web: bool

class RagJudgeNode:
    def __init__(
            self, 
            model_name: str = "gpt-4o", 
            temperature: float = 0.7
        ):
        self.judge_llm = ChatOpenAI(model=model_name, temperature=temperature)\
            .with_structured_output(RagJudge)
        self.rag_search = PineconeBookRetrieverTool()
    
    def __call__(self, state: AgentState) -> AgentState:
        query = next((m.content for m in reversed(state["messages"])
                      if isinstance(m, HumanMessage)), "")
        
        chunks = self.rag_search.invoke({"query": query})
        _ROOT = pathlib.Path(__file__).parents[1]
        _JUDGE_PROMPT = (_ROOT / "prompts" / "judge.md").read_text(encoding="utf-8")
        judge_messages = [
            SystemMessage(content=_JUDGE_PROMPT),
            HumanMessage(content=f"""Query: {query}\nRetrienved info: {chunks}\n\nIs this enough to answer the query?
            If not, mark **use_web** as True.
            If yes, and the retrieved info is not enough, mark **use_web** as True.
            If yes, and the retrieved info is enough, mark **use_web** as False.
            """)
        ]

        verdict = self.judge_llm.invoke(judge_messages)

        route = ""
        if verdict.sufficient:
            if verdict.use_web:
                route = "web"
            else:
                route = "answer"
        else:
            route = "web"

        return {
            **state,
            "rag_docs": chunks,
            "route": route
        }
    
    def after_rag(self, state: AgentState) -> Literal["answer", "web"]:
        return state["route"]