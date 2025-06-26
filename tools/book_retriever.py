import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import BaseTool
from typing import Optional
from pydantic import Field, PrivateAttr

class BookRetrieverTool(BaseTool):
    name: str = "book_retriever_tool"
    description: str = "Search the book database for the most relevant books"

    # Define all configurable fields with type annotations

    # Use PrivateAttr for non-serializable/internal attributes
    _collection_name: Optional[str] = PrivateAttr()
    _embedding_model: Optional[str] = PrivateAttr()
    _persist_dir: Optional[str] = PrivateAttr()
    _k: Optional[int] = PrivateAttr()
    _retriever: object = PrivateAttr()
    
    def __init__(
        self,
        collection_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
        persist_dir: Optional[str] = None,
        k: Optional[int] = 3,

        **kwargs
    ):
        super().__init__(**kwargs)
        
        # Initialize retriever after Pydantic fields
        self._collection_name = collection_name or os.getenv("COLLECTION_NAME")
        self._embedding_model = embedding_model or os.getenv("EMBEDDING_MODEL")
        self._persist_dir = persist_dir or os.getenv("PERSIST_DIR")
        self._k = k
        self._retriever = self._init_retriever()

    def _init_retriever(self):
        print("-"*50)
        print("Initializing retriever with the following parameters:")
        print(f"Collection name: {self._collection_name}")
        print(f"Embedding model: {self._embedding_model}")
        print(f"Persist directory: {self._persist_dir}")
        print(f"K: {self._k}")
        print("-"*50)
        vectordb = Chroma(
            collection_name=self._collection_name,
            embedding_function=OpenAIEmbeddings(model=self._embedding_model),
            persist_directory=self._persist_dir,
        )
        return vectordb.as_retriever(search_kwargs={"k": self._k})

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
