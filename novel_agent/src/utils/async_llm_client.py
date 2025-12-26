"""
Async LLM client for Novel Agent supporting DeepSeek and OpenAI.

This module provides an asynchronous interface for LLM API calls,
enabling high-concurrency and non-blocking operations.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Union
import aiohttp

from .config import config


class AsyncLLMClient:
    """Async LLM client supporting multiple providers."""

    def __init__(self, provider: Optional[str] = None):
        """Initialize async LLM client.

        Args:
            provider: LLM provider ("deepseek" or "openai")
        """
        self.provider = provider or config.DEFAULT_LLM_PROVIDER
        self.config = config.get_llm_config(self.provider)

    async def achat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """Send async chat completion request using aiohttp (community recommended).

        Args:
            messages: List of message dictionaries with "role" and "content"
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_format: Response format specification
            **kwargs: Additional arguments for chat completion

        Returns:
            Generated text content
        """
        import logging
        logger = logging.getLogger("novel_agent.async_llm_client")

        temperature = temperature or config.AGENT_TEMPERATURE
        logger.info(f"[AsyncLLMClient] achat_completion called, model={self.config['model']}, temperature={temperature}")

        # Prepare request
        url = f"{self.config['base_url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": temperature,
            "stream": False,  # Non-streaming
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if response_format:
            payload["response_format"] = response_format

        logger.info(f"[AsyncLLMClient] Sending POST to {url}")
        logger.debug(f"[AsyncLLMClient] Payload: {payload}")

        # Use aiohttp (community recommended method)
        session = aiohttp.ClientSession()
        try:
            resp = await session.post(url, json=payload, headers=headers)
            logger.info(f"[AsyncLLMClient] Got response status: {resp.status}")

            if resp.status != 200:
                error_text = await resp.text()
                logger.error(f"[AsyncLLMClient] Non-200 status: {resp.status}")
                await session.close()
                raise RuntimeError(f"API returned status {resp.status}: {error_text}")

            logger.info("[AsyncLLMClient] Before await resp.text()")
            response_text = await resp.text()
            logger.info("[AsyncLLMClient] After await resp.text()")
            logger.info(f"[AsyncLLMClient] Response text length: {len(response_text)}")

            # Parse JSON manually
            response_data = json.loads(response_text)
            logger.info("[AsyncLLMClient] JSON parsed successfully")
            logger.info(f"[AsyncLLMClient] Response JSON keys: {list(response_data.keys())}")
            logger.info(f"[AsyncLLMClient] Choices count: {len(response_data.get('choices', []))}")

            await session.close()

            if "choices" not in response_data or not response_data["choices"]:
                logger.error("[AsyncLLMClient] No choices in response")
                raise ValueError("Empty response from LLM")

            content = response_data["choices"][0]["message"]["content"]
            logger.info(f"[AsyncLLMClient] Got content, length={len(content)}")
            return content

        except Exception as e:
            logger.error(f"[AsyncLLMClient] Exception in achat_completion: {e}", exc_info=True)
            try:
                await session.close()
            except:
                pass
            raise RuntimeError(f"Async LLM request failed: {str(e)}")

    async def achat_completion_with_retry(
        self,
        messages: List[Dict[str, str]],
        max_retries: Optional[int] = None,
        retry_delay: float = 1.0,
        **kwargs,
    ) -> str:
        """Send async chat completion request with retry logic.

        Args:
            messages: List of message dictionaries
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            **kwargs: Additional arguments for achat_completion

        Returns:
            Generated text content
        """
        import logging
        logger = logging.getLogger("novel_agent.async_llm_client")

        max_retries = max_retries or config.AGENT_MAX_RETRIES
        logger.info(f"[AsyncLLMClient] achat_completion_with_retry, max_retries={max_retries}")

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"[AsyncLLMClient] Attempt {attempt + 1}/{max_retries + 1}")
                result = await self.achat_completion(messages, **kwargs)
                logger.info(f"[AsyncLLMClient] achat_completion returned successfully")
                return result
            except Exception as e:
                logger.error(f"[AsyncLLMClient] Attempt {attempt + 1} failed: {e}")
                last_error = e
                if attempt < max_retries:
                    # Exponential backoff
                    delay = retry_delay * (2 ** attempt)
                    logger.info(f"[AsyncLLMClient] Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    break

        # All retries exhausted
        logger.error(f"[AsyncLLMClient] All retries exhausted")
        raise RuntimeError(
            f"Async LLM request failed after {max_retries} retries: {str(last_error)}"
        )

    async def achat_completion_json(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Send async chat completion request expecting JSON response.

        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments

        Returns:
            Parsed JSON response as dictionary
        """
        import logging
        logger = logging.getLogger("novel_agent.async_llm_client")

        logger.info("[AsyncLLMClient] achat_completion_json called")

        # Add JSON response format requirement
        json_messages = messages.copy()
        if json_messages and json_messages[-1]["role"] == "user":
            json_messages[-1]["content"] += "\n\n请以JSON格式返回结果。"

        logger.info("[AsyncLLMClient] Calling achat_completion_with_retry...")
        response_text = await self.achat_completion_with_retry(
            json_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        logger.info(f"[AsyncLLMClient] Got response, length={len(response_text)}")

        try:
            # Try to extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            logger.info(f"[AsyncLLMClient] Parsing JSON, json_start={json_start}, json_end={json_end}")

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                logger.info(f"[AsyncLLMClient] JSON parsed successfully")
                return result
            else:
                # If no JSON found, try to parse the whole response
                logger.info("[AsyncLLMClient] No JSON markers found, parsing whole response")
                result = json.loads(response_text)
                logger.info(f"[AsyncLLMClient] JSON parsed successfully")
                return result

        except json.JSONDecodeError as e:
            logger.error(f"[AsyncLLMClient] JSON decode failed: {e}")
            raise ValueError(
                f"Failed to parse JSON response: {str(e)}\nResponse: {response_text}"
            )

    async def aclose(self):
        """Close the async client and release resources."""
        await self.client.close()
        await self.http_client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()

    # Compatibility methods (sync wrappers for convenience)
    def chat_completion(self, *args, **kwargs) -> str:
        """Sync wrapper for achat_completion."""
        return asyncio.run(self.achat_completion(*args, **kwargs))

    def chat_completion_with_retry(self, *args, **kwargs) -> str:
        """Sync wrapper for achat_completion_with_retry."""
        return asyncio.run(self.achat_completion_with_retry(*args, **kwargs))

    def chat_completion_json(self, *args, **kwargs) -> Dict[str, Any]:
        """Sync wrapper for achat_completion_json."""
        return asyncio.run(self.achat_completion_json(*args, **kwargs))


# Global async LLM client instance (lazy initialization)
_async_llm_client: Optional[AsyncLLMClient] = None


def get_async_llm_client(provider: Optional[str] = None) -> AsyncLLMClient:
    """Get or create global async LLM client instance.

    Args:
        provider: LLM provider

    Returns:
        AsyncLLMClient instance

    Note:
        For multiprocessing environments, it's better to create a new client
        in each worker process rather than sharing a global one.
    """
    # Always create a new instance to avoid event loop issues
    # This is less efficient but more stable in multiprocessing
    return AsyncLLMClient(provider)


def reset_async_llm_client():
    """Reset global async LLM client instance."""
    global _async_llm_client
    _async_llm_client = None
