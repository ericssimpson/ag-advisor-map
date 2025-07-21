"""Service for interacting with the OpenRouter API."""

import json
import logging
from typing import Any, AsyncGenerator

import httpx

from app.core.config import LONG_QUERY_THRESHOLD, settings

logger = logging.getLogger(__name__)


def select_model(text: str, context_type: str) -> str:
    """Select an appropriate LLM model based on query complexity and context."""
    text_length = len(text)
    if context_type == "data_loaded" or text_length > LONG_QUERY_THRESHOLD:
        return settings.advanced_model
    return settings.default_model


def get_system_prompt(context_type: str) -> str:
    """Get the system prompt based on the conversation context."""
    base_prompt = (
        "You are AgriBot, a helpful assistant specialized in agricultural advice and "
        "data interpretation. Provide insightful and actionable farming "
        "recommendations based on location data, soil conditions, and "
        "agricultural metrics."
    )
    prompts = {
        "farm_selected": (
            f"{base_prompt} The user has selected a farm location. Analyze this "
            "geographical context to provide location-specific agricultural insights "
            "such as suitable crops, regional climate patterns, and local best "
            "practices. When specific values are provided (like NDVI, soil moisture, "
            "etc.), interpret them in practical terms for the farmer."
        ),
        "data_loaded": (
            f"{base_prompt} The user has loaded farm data. Analyze the provided "
            "metrics and offer meaningful interpretations. For example, explain what "
            "the values mean for crop health, soil conditions, or irrigation needs. "
            "Translate technical data into practical farming advice. If coordinates "
            "are provided, consider regional agricultural patterns for that location."
        ),
        "general": (
            f"{base_prompt} Provide general farming information and encourage "
            "the user to select a farm location on the map for more tailored advice. "
            "Explain the benefits of location-specific agricultural insights."
        ),
    }

    prompt = prompts.get(context_type, prompts["general"])
    return f"{prompt} All responses must be in English."


def _prepare_request_payload(
    model: str, system_prompt: str, user_text: str, stream: bool
) -> dict[str, Any]:
    """Prepare the JSON payload for the OpenRouter API request."""
    return {
        "model": model,
        "models": [model, settings.fallback_model],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        "max_tokens": settings.max_tokens,
        "temperature": 0.7,
        "stream": stream,
    }


def _prepare_headers() -> dict[str, str]:
    """Prepare the headers for the OpenRouter API request."""
    return {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.app_url,
        "X-Title": "AgriOrbit",
    }


async def _process_stream_chunk(chunk: str, buffer: str) -> tuple[str, str]:
    """Process a single chunk from the streaming response."""
    buffer += chunk
    lines = buffer.split("\n")
    buffer = lines[-1]
    processed_data = ""

    for line in lines[:-1]:
        if line.startswith("data:") and line.strip() != "data: [DONE]":
            try:
                json_str = line[5:].strip()
                if json_str:
                    chunk_data = json.loads(json_str)
                    content = (
                        chunk_data.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content", "")
                    )
                    if content:
                        data_to_yield = {"content": content}
                        processed_data += f"data: {json.dumps(data_to_yield)}\n\n"
            except json.JSONDecodeError:
                logger.warning("Incomplete JSON chunk received: %s", line)
        elif line.strip() == "data: [DONE]":
            processed_data += "data: [DONE]\n\n"
            break
    return processed_data, buffer


async def generate_streaming_response(
    json_data: dict,
) -> AsyncGenerator[str, None]:
    """Generate a streaming response from OpenRouter, handling complexity."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", url, headers=_prepare_headers(), json=json_data, timeout=90.0
            ) as response:
                response.raise_for_status()
                buffer = ""
                async for chunk in response.aiter_bytes():
                    if chunk.strip():
                        processed_data, buffer = await _process_stream_chunk(
                            chunk.decode("utf-8"), buffer
                        )
                        if processed_data:
                            yield processed_data

                if not buffer.strip().endswith("[DONE]"):
                    yield "data: [DONE]\n\n"

    except httpx.HTTPStatusError as e:
        error_detail = e.response.text or f"Status {e.response.status_code}"
        logger.error(
            "OpenRouter HTTPStatusError: %s - %s", e.response.status_code, error_detail
        )
        error_content = {
            "error": f"OpenRouter API error ({e.response.status_code}): {error_detail}"
        }
        yield f"data: {json.dumps(error_content)}\n\n"
        yield "data: [DONE]\n\n"
    except httpx.RequestError as e:
        logger.error("OpenRouter RequestError: %s", e)
        error_content = {"error": f"Network error connecting to OpenRouter: {e}"}
        yield f"data: {json.dumps(error_content)}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error("Unexpected error during streaming: %s", e, exc_info=True)
        error_content = {"error": f"Unexpected error: {e}"}
        yield f"data: {json.dumps(error_content)}\n\n"
        yield "data: [DONE]\n\n"


async def get_chat_response(
    message_text: str, context_type: str, use_streaming: bool
) -> AsyncGenerator[str, None] | dict[str, Any]:
    """Get chat response from OpenRouter, streaming or non-streaming."""
    selected_model = select_model(message_text, context_type)
    system_prompt = get_system_prompt(context_type)
    json_data = _prepare_request_payload(
        selected_model, system_prompt, message_text, use_streaming
    )

    logger.info(
        "Sending request to OpenRouter with model: %s (streaming: %s)",
        selected_model,
        use_streaming,
    )

    if use_streaming:
        return generate_streaming_response(json_data)

    # Non-streaming logic
    headers = _prepare_headers()
    url = "https://openrouter.ai/api/v1/chat/completions"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=json_data, timeout=90.0)
        response.raise_for_status()
        openrouter_response = response.json()

        if "error" in openrouter_response:
            error_msg = openrouter_response["error"].get("message", "Unknown error")
            raise ValueError(error_msg)

        if not openrouter_response.get("choices"):
            raise ValueError("Invalid response format from OpenRouter")

        used_model = openrouter_response.get("model", selected_model)
        if used_model != selected_model:
            logger.info("Fallback model used: %s", used_model)

        reply_text = openrouter_response["choices"][0]["message"]["content"]
        return {"response": reply_text}
