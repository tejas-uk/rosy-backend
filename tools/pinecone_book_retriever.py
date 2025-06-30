import os
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import BaseTool
from typing import Optional
from pydantic import Field, PrivateAttr
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

class PineconeBookRetrieverTool(BaseTool):
    name: str = "book_retriever_tool"
    description: str = "Search the book database for the most relevant books"

    # Define all configurable fields with type annotations

    # Use PrivateAttr for non-serializable/internal attributes
    _index_name: Optional[str] = PrivateAttr()
    _embedding_model: Optional[str] = PrivateAttr()
    _k: Optional[int] = PrivateAttr()
    _retriever: object = PrivateAttr()
    
    def __init__(
        self,
        index_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
        k: Optional[int] = 5,

        **kwargs
    ):
        super().__init__(**kwargs)
        
        # Initialize retriever after Pydantic fields
        self._index_name = index_name or os.getenv("INDEX_NAME")
        self._embedding_model = embedding_model or os.getenv("EMBEDDING_MODEL")
        self._k = k
        self._retriever = self._init_retriever()

    def _init_retriever(self):
        # print("-"*50)
        # print("Initializing retriever with the following parameters:")
        # print(f"Index name: {self._index_name}")
        # print(f"Embedding model: {self._embedding_model}")
        # print(f"K: {self._k}")
        # print("-"*50)
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

        vectorstore = PineconeVectorStore(
            index_name=self._index_name,
            embedding=OpenAIEmbeddings(model=self._embedding_model),
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        )

        return vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self._k}
        )

    def _run(self, query: str) -> str:
        """
        Execute the book search with error handling
        """
        try:
            docs = self._retriever.invoke(query)
            return "\n\n".join(doc.page_content for doc in docs) if docs else "No books found"
        except Exception as e:
            return f"Retrieval Error: {str(e)}"

# Usage:
# book_tool = BookRetrieverTool()
# result = book_tool.invoke({"query": "science fiction"})
