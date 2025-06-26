from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from states import AgentState
from langchain_core.messages import HumanMessage
from tools import BookRetrieverTool
from typing import Literal

class RagJudge(BaseModel):
    sufficient: bool

class RagJudgeNode:
    def __init__(
            self, 
            model_name: str = "gpt-4.1-mini", 
            temperature: float = 0.7
        ):
        self.judge_llm = ChatOpenAI(model=model_name, temperature=temperature)\
            .with_structured_output(RagJudge)
        self.rag_search = BookRetrieverTool()
    
    def __call__(self, state: AgentState) -> AgentState:
        query = next((m.content for m in reversed(state["messages"])
                      if isinstance(m, HumanMessage)), "")
        
        chunks = self.rag_search.invoke({"query": query})
        
        judge_messages = [
            ("system",
            ("You are a RAG agent that can answer questions based on the provided documents. \n"
            "You will be given a query and a list of documents. \n"
            "You need to answer the query based on the documents. \n"
            )),
            ("user", f"Query: {query}\nRetrienved info: {chunks}\n\nIs this enough to answer the query?")
        ]

        verdict = self.judge_llm.invoke(judge_messages)

        return {
            **state,
            "rag_docs": chunks,
            "route": "answer" if verdict.sufficient else "web"
        }
    
    def after_rag(self, state: AgentState) -> Literal["answer", "web"]:
        return state["route"]