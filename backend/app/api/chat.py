"""API endpoints for chat functionality."""

import logging
from typing import AsyncGenerator

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.chat import Message
from app.services.openrouter import get_chat_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.options("/chat")
async def options_chat():
    """Handle OPTIONS requests for CORS preflight."""
    return {"message": "OK"}


@router.post("/chat")
async def chat(message: Message):
    """Handle chat requests and interact with OpenRouter."""
    try:
        response_data = await get_chat_response(
            message.text, message.context_type, message.use_streaming
        )

        if isinstance(response_data, AsyncGenerator):
            return StreamingResponse(response_data, media_type="text/event-stream")

        return response_data

    except httpx.HTTPStatusError as e:
        logger.error("HTTP error: %s - %s", e.response.status_code, e.response.text)
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"OpenRouter API error: {e.response.text}",
        ) from e
    except httpx.RequestError as e:
        logger.error("Request error: %s", e)
        raise HTTPException(status_code=500, detail=f"Network error: {e}") from e
    except ValueError as e:
        logger.exception("Validation error in chat endpoint: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        logger.exception("Unexpected critical error in chat endpoint: %s", e)
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {e}"
        ) from e
