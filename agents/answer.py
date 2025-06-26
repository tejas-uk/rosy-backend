from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from states import AgentState
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Literal
import pathlib

class AnswerNode:
    def __init__(
            self, 
            model_name: str = "gpt-4.1-mini", 
            temperature: float = 0.7
        ):
        self.answer_llm = ChatOpenAI(model=model_name, temperature=temperature)

    def _get_context(self, state: AgentState) -> str:
        ctx_parts = []
        
        if state.get("rag"):
            ctx_parts.append(f"Retrieved info from RAG:\n{state['rag']}")
        
        if state.get("web"):
            ctx_parts.append(f"Retrieved info from web:\n{state['web']}")
        
        return "\n\n".join(ctx_parts) if ctx_parts else "No external info available"

    def __call__(self, state: AgentState) -> AgentState:
        query = next((m.content for m in reversed(state["messages"])
                      if isinstance(m, HumanMessage)), "")
        
        context = self._get_context(state)

        ROOT = pathlib.Path(__file__).parents[1]
        LILY_PROMPT = (ROOT / "prompts" / "lily.md").read_text(encoding="utf-8")
        prompt = f"""Please answer the user's query based on the provided context:
                Query:
                {query}
                
                Context:
                {context}

                Provide a helpful, accurate, and concise response based on the available information.
                """
        
        response = self.answer_llm.invoke([
            SystemMessage(content=LILY_PROMPT),
            HumanMessage(content=prompt)
        ]).content

        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=response)]
        }
    
    def after_web(self, state: AgentState) -> Literal["answer"]:
        return "answer"