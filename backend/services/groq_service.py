"""
CollegePath AI — Groq LLM Service
Wraps Groq API calls for all agents.
"""
from groq import AsyncGroq
from typing import AsyncGenerator, Optional
from backend.core.config import get_settings
from loguru import logger

settings = get_settings()


class GroqService:
    """Async Groq LLM service used by all agents."""

    def __init__(self):
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = settings.groq_model

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
        json_mode: bool = False,
    ) -> str:
        """Single completion call — returns full text."""
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        kwargs = dict(
            model=self.model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            resp = await self.client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise

    async def stream_chat(
        self,
        messages: list[dict],
        system_prompt: str = "",
        temperature: float = 0.4,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """Streaming completion — yields text chunks."""
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            logger.error(f"Groq streaming error: {e}")
            raise


_groq_service: Optional[GroqService] = None


def get_groq_service() -> GroqService:
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service
