"""
LLM client for Novel Agent supporting DeepSeek and OpenAI.
"""

import json
import time
from typing import Dict, Any, List, Optional, Union
from openai import OpenAI
from openai.types.chat import ChatCompletion

from .config import config


class LLMClient:
    """LLM client supporting multiple providers."""

    def __init__(self, provider: Optional[str] = None):
        """Initialize LLM client.

        Args:
            provider: LLM provider ("deepseek" or "openai")
        """
        self.provider = provider or config.DEFAULT_LLM_PROVIDER
        self.config = config.get_llm_config(self.provider)

        # Initialize OpenAI client (compatible with DeepSeek)
        self.client = OpenAI(
            api_key=self.config["api_key"],
            base_url=self.config["base_url"],
            timeout=config.AGENT_TIMEOUT,
            max_retries=config.AGENT_MAX_RETRIES,
        )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """Send chat completion request.

        Args:
            messages: List of message dictionaries with "role" and "content"
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_format: Response format specification
            **kwargs: Additional arguments for chat completion

        Returns:
            Generated text content
        """
        temperature = temperature or config.AGENT_TEMPERATURE

        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                **kwargs,
            )

            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Empty response from LLM")

            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"LLM request failed: {str(e)}")

    def chat_completion_with_retry(
        self,
        messages: List[Dict[str, str]],
        max_retries: Optional[int] = None,
        retry_delay: float = 1.0,
        **kwargs,
    ) -> str:
        """Send chat completion request with retry logic.

        Args:
            messages: List of message dictionaries
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            **kwargs: Additional arguments for chat_completion

        Returns:
            Generated text content
        """
        max_retries = max_retries or config.AGENT_MAX_RETRIES

        for attempt in range(max_retries + 1):
            try:
                return self.chat_completion(messages, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    raise RuntimeError(
                        f"LLM request failed after {max_retries} retries: {str(e)}"
                    )

                # Exponential backoff
                delay = retry_delay * (2**attempt)
                time.sleep(delay)

        # This should never be reached
        raise RuntimeError("Unexpected error in chat_completion_with_retry")

    def chat_completion_json(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Send chat completion request expecting JSON response.

        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments

        Returns:
            Parsed JSON response as dictionary
        """
        # Add JSON response format requirement
        json_messages = messages.copy()
        if json_messages and json_messages[-1]["role"] == "user":
            json_messages[-1]["content"] += "\n\n请以JSON格式返回结果。"

        response_text = self.chat_completion_with_retry(
            json_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        try:
            # Try to extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # If no JSON found, try to parse the whole response
                return json.loads(response_text)

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response_text}")

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text.

        Note: This is a rough estimation. For accurate token counting,
        use the provider's tokenizer if available.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters for English,
        # 1 token ≈ 2 characters for Chinese
        # This is a simplified estimation
        chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        other_chars = len(text) - chinese_chars

        # Estimate tokens: Chinese ~2 chars per token, others ~4 chars per token
        estimated_tokens = (chinese_chars / 2) + (other_chars / 4)
        return int(estimated_tokens)

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model.

        Returns:
            Dictionary with model information
        """
        return {
            "provider": self.provider,
            "model": self.config["model"],
            "base_url": self.config["base_url"],
            "supports_json": True,  # Both DeepSeek and OpenAI support JSON
            "max_tokens": 4096,  # Default, can be overridden
        }


# Global LLM client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client(provider: Optional[str] = None) -> LLMClient:
    """Get or create global LLM client instance.

    Args:
        provider: LLM provider

    Returns:
        LLMClient instance
    """
    global _llm_client

    if _llm_client is None:
        _llm_client = LLMClient(provider)

    return _llm_client