"""Pydantic models for the chat API."""

from pydantic import BaseModel


class Message(BaseModel):
    """Represents a chat message from the user."""

    text: str
    context_type: str = "general"  # "general", "farm_selected", or "data_loaded"
    use_streaming: bool = True
