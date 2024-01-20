"""Module for the LLM service."""
from typing import Dict, List, Union

from openai import AsyncOpenAI, OpenAI

from .logging import log

client: Union[AsyncOpenAI, OpenAI, None] = None


def initialize() -> None:
    """Initializes the OpenAI API."""
    log("Initializing OpenAI API", level="info")
    global client
    client = AsyncOpenAI()
    log("OpenAI API initialized successfully", level="info")


async def async_generate_text(messages: List[Dict[str, str]]) -> Union[str, None]:
    """Generates text asynchronously."""
    model = "gpt-4-1106-preview"
    try:
        global client
        if not client:
            initialize()
        log("Generating text...", level="info")
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
        )
        generated_content = response.choices[0].message.content
        log("Text generated successfully", level="info")
        return generated_content
    except RuntimeError as err:
        log(f"Failed to generate text: {err}", level="error")
        return None
