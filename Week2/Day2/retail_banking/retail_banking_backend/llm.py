import config  # noqa: F401 — loads .env.local
import os
import anthropic
from functools import lru_cache
from typing import Any
from collections.abc import Iterator
from pydantic import BaseModel, ValidationError
from fastapi import HTTPException

MODEL = os.environ["ANTHROPIC_MODEL"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
MAX_TOKENS = int(os.environ["MAX_TOKENS"])
MAX_RETRIES = int(os.environ["MAX_RETRIES"])
TIMEOUT = float(os.environ["MODEL_TIMEOUT"])

@lru_cache(maxsize=1)
def get_client() -> anthropic.Anthropic:
    """
    Lazy singleton. 
    Reads ANTHROPIC_API_KEY from env, 
    instantiates the Anthropic client once, caches it. 
    Everyone else imports and calls this.
    """
    client = anthropic.Anthropic(
        api_key = ANTHROPIC_API_KEY,
        timeout = TIMEOUT,
        max_retries = MAX_RETRIES
    )
    return client

def generate(system:str, user:str)-> dict[str, Any]:
    """
    Plain blocking call. 
    Returns {"text": str, "input_tokens": int, "output_tokens": int}. 
    Used by /complaints/{id}/summary.
    """
    client = get_client()
    try:
        response = client.messages.create(
            model = MODEL,
            max_tokens=MAX_TOKENS,
            system = system,
            messages = [{"role": "user", "content": user}]
        )
        return {
            "text": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "stop_reason": response.stop_reason,
        }
    except anthropic.APIError as e:
        raise handle_anthropic_error(e)
    except ValidationError:
        raise HTTPException(502, "upstream LLM returned invalid structured output")
    

def stream(system:str, user:str) -> Iterator[str]:
    """
        Streaming version — 
        yields text chunks as they arrive. 
        Used by /complaints/{id}/summary/stream.
    """
    try:
        with get_client().messages.stream(
            model =  MODEL,
            max_tokens = MAX_TOKENS,
            system = system,
            messages = [{"role":"user", "content": user }]
        ) as stream:
            for text in stream.text_stream:
                yield text
                
    except anthropic.APIError as e:
        raise handle_anthropic_error(e)
    except ValidationError:
        raise HTTPException(502, "upstream LLM returned invalid structured output")


def generate_structured(system: str, user: str, response_model: type[BaseModel], max_tokens:int= MAX_TOKENS) -> dict[str, Any]:
    """
        Calls Claude asking for JSON matching response_model, parses the response, 
        validates with Pydantic, raises if invalid. 
        Used by /complaints/{id}/analyze.
    """
    client = get_client()
    try:
        response = client.messages.parse(
            model =  MODEL,
            max_tokens = max_tokens,
            system = system,
            messages = [{"role":"user", "content": user }],
            output_format = response_model
        )
        structured_output = response.content[0].parsed_output

    except anthropic.APIError as e:
        raise handle_anthropic_error(e)
    except ValidationError:
        raise HTTPException(502, "upstream LLM returned invalid structured output")
    
    return {
        "structured_output": structured_output,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "stop_reason": response.stop_reason,
    }


def handle_anthropic_error(exc: Exception) -> HTTPException:
    """
        Maps Anthropic SDK exceptions to HTTP responses: 
        APITimeoutError → 504, 
        RateLimitError → 429, 
        everything else → 502. 
        Called by every endpoint that touches Claude.
    """
    if isinstance(exc,anthropic.APITimeoutError):
        return HTTPException(504, "Upstream Model Timeout Error")
    if isinstance(exc, anthropic.RateLimitError):
        return HTTPException(429, "Upstream Model Rate Limit Error")
    return HTTPException(502, "Upstream Model Error")

def estimate_input_tokens(system: str, user: str) -> int:
    counted = get_client().messages.count_tokens(
        model= MODEL,
        system=system,
        messages=[{'role': 'user', 'content':user}]
    )
    return counted.input_tokens