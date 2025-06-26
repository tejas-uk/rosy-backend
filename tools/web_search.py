import os
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from typing import Optional
from langchain_core.tools import BaseTool
from pydantic import Field, PrivateAttr

class WebSearchTool(BaseTool):
    name: str = "web_search_tool"
    description: str = "Up to date web information via Tavily"
    
    # Configurable field
    api_key: Optional[str] = Field(default=None)
    
    # Internal attribute
    _tavily_search: object = PrivateAttr()

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(
            api_key=api_key or os.getenv("TAVILY_API_KEY"),
            **kwargs
        )
        self._tavily_search = TavilySearch(api_key=self.api_key)

    def _run(self, query: str) -> str:
        """Core tool function to search the web for the query"""
        try:
            response = self._tavily_search.invoke({"query": query})

            if isinstance(response, dict) and "results" in response:
                formatted_results = []
                for item in response['results']:
                    title = item.get('title', 'No title')
                    url = item.get('url', '')
                    content = item.get('content', 'No content')
                    formatted_results.append(f"Title: {title}\nContent: {content}\nURL: {url}\n")

                return "\n\n".join(formatted_results) if formatted_results else "No results found"
            else:
                return str(response)
        except Exception as e:
            return f"Web Error: {str(e)}"

# Usage in agent:
# web_tool = WebSearchTool()
# result = web_tool.invoke({"query": "Python"})
