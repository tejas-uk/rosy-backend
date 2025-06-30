from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from states import AgentState
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from messages import LilyMessage  # Using AIMessage instead for PostgreSQL compatibility
from typing import Literal
import pathlib

class AnswerNode:
    def __init__(
            self, 
            model_name: str = "gpt-4.1-mini", 
            temperature: float = 0.7
        ):
        self.answer_llm = ChatOpenAI(model=model_name, temperature=temperature)

    def _get_context(self, state: AgentState) -> str|None:
        ctx_parts = []
        
        if state.get("rag"):
            ctx_parts.append(f"Retrieved info from RAG:\n{state['rag']}")
        
        if state.get("web"):
            ctx_parts.append(f"Retrieved info from web:\n{state['web']}")
        
        return "\n\n".join(ctx_parts) if ctx_parts else None

    def __call__(self, state: AgentState) -> AgentState:
        # query = next((m.content for m in reversed(state["messages"])
        #               if isinstance(m, HumanMessage)), "")
        
        conversation = "\n".join([f"{m.type}: {m.content}" for m in state["messages"]])
        # print(f"Conversation:\n{conversation}")
        context = self._get_context(state)
        prompt = ""
        if context:
            prompt = f"""Please answer the user's latest query in the conversation based on the provided context:
                    Conversation:
                    {conversation}
                    
                    Context:
                    {context}

                    Provide a helpful, accurate, and concise response based on the available information.
                    """
        else:
            prompt = f"""Please answer the user's latest query/message in the conversation:
                    Conversation:
                    {conversation}
                    """

        ROOT = pathlib.Path(__file__).parents[1]
        ROSI_PROMPT = (ROOT / "prompts" / "rosi.md").read_text(encoding="utf-8")
        
        response = self.answer_llm.invoke([
            SystemMessage(content=ROSI_PROMPT),
            HumanMessage(content=prompt)
        ]).content

        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=response)]
        }
    
    def after_web(self, state: AgentState) -> Literal["answer"]:
        return "answer"