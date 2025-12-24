"""
Configuration management for Novel Agent.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for Novel Agent."""

    # LLM Configuration
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # OpenAI fallback (optional)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Agent Configuration
    AGENT_MAX_RETRIES: int = int(os.getenv("AGENT_MAX_RETRIES", "3"))
    AGENT_TIMEOUT: int = int(os.getenv("AGENT_TIMEOUT", "30"))
    AGENT_TEMPERATURE: float = float(os.getenv("AGENT_TEMPERATURE", "0.7"))

    # Novel Generation Configuration
    DEFAULT_CHAPTER_LENGTH: int = int(os.getenv("DEFAULT_CHAPTER_LENGTH", "2000"))
    MAX_CHAPTER_LENGTH: int = int(os.getenv("MAX_CHAPTER_LENGTH", "5000"))
    MIN_CHAPTER_LENGTH: int = int(os.getenv("MIN_CHAPTER_LENGTH", "1000"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "novel_agent.log")

    # Cache
    USE_CACHE: bool = os.getenv("USE_CACHE", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))

    # Default LLM provider
    DEFAULT_LLM_PROVIDER: str = "deepseek"

    @classmethod
    def validate(cls) -> None:
        """Validate configuration."""
        if not cls.DEEPSEEK_API_KEY and not cls.OPENAI_API_KEY:
            raise ValueError(
                "Either DEEPSEEK_API_KEY or OPENAI_API_KEY must be set in environment variables"
            )

        if cls.DEFAULT_LLM_PROVIDER == "deepseek" and not cls.DEEPSEEK_API_KEY:
            raise ValueError(
                "DEEPSEEK_API_KEY is required when using DeepSeek as default provider"
            )

        if cls.DEFAULT_LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required when using OpenAI as default provider"
            )

    @classmethod
    def get_llm_config(cls, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get LLM configuration for the specified provider."""
        provider = provider or cls.DEFAULT_LLM_PROVIDER

        if provider == "deepseek":
            return {
                "api_key": cls.DEEPSEEK_API_KEY,
                "base_url": cls.DEEPSEEK_BASE_URL,
                "model": cls.DEEPSEEK_MODEL,
                "provider": "deepseek",
            }
        elif provider == "openai":
            return {
                "api_key": cls.OPENAI_API_KEY,
                "base_url": cls.OPENAI_BASE_URL,
                "model": cls.OPENAI_MODEL,
                "provider": "openai",
            }
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @classmethod
    def get_agent_config(cls) -> Dict[str, Any]:
        """Get agent configuration."""
        return {
            "max_retries": cls.AGENT_MAX_RETRIES,
            "timeout": cls.AGENT_TIMEOUT,
            "temperature": cls.AGENT_TEMPERATURE,
        }

    @classmethod
    def get_novel_config(cls) -> Dict[str, Any]:
        """Get novel generation configuration."""
        return {
            "default_chapter_length": cls.DEFAULT_CHAPTER_LENGTH,
            "max_chapter_length": cls.MAX_CHAPTER_LENGTH,
            "min_chapter_length": cls.MIN_CHAPTER_LENGTH,
        }


# Global configuration instance
config = Config()