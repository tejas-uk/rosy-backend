from langchain_core.messages import AIMessage

class LilyMessage(AIMessage):
    """A custom message class with type 'lily'."""
    type: str = "lily"

    def __init__(self, content, **kwargs):
        super().__init__(content, **kwargs)