"""
Base agent class for Novel Agent.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

from src.utils import get_llm_client, config


@dataclass
class AgentResult:
    """Result from agent execution."""

    content: str
    metadata: Dict[str, Any]
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "success": self.success,
            "error": self.error,
        }


class BaseAgent(ABC):
    """Base class for all agents in Novel Agent."""

    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        llm_provider: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """Initialize base agent.

        Args:
            name: Agent name
            role: Agent role description
            system_prompt: System prompt for the agent
            llm_provider: LLM provider ("deepseek" or "openai")
            temperature: Sampling temperature
        """
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.llm_provider = llm_provider
        self.temperature = temperature or config.AGENT_TEMPERATURE

        self.llm_client = get_llm_client(llm_provider)
        self.logger = logging.getLogger(f"novel_agent.{name}")

        # Execution history
        self.execution_history: List[Dict[str, Any]] = []

    @abstractmethod
    def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Execute agent task.

        Args:
            task: Task description
            context: Context information

        Returns:
            AgentResult with execution results
        """
        pass

    def _prepare_messages(self, task: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Prepare messages for LLM.

        Args:
            task: Task description
            context: Context information

        Returns:
            List of message dictionaries
        """
        # Format context as JSON string for inclusion in prompt
        # Handle Pydantic models by converting them to dicts
        serializable_context = {}
        for key, value in context.items():
            if hasattr(value, 'model_dump'):
                # Pydantic v2
                serializable_context[key] = value.model_dump()
            elif hasattr(value, 'dict'):
                # Pydantic v1
                serializable_context[key] = value.dict()
            elif isinstance(value, dict):
                # Recursively process nested dicts
                serializable_context[key] = self._serialize_dict(value)
            else:
                serializable_context[key] = value

        context_str = json.dumps(serializable_context, ensure_ascii=False, indent=2, default=str)

        messages = [
            {
                "role": "system",
                "content": f"""你是一个{self.role}。

{self.system_prompt}

你的名字：{self.name}
你的角色：{self.role}

请严格按照要求执行任务。""",
            },
            {
                "role": "user",
                "content": f"""任务：{task}

上下文信息：
{context_str}

请根据以上信息执行任务。""",
            },
        ]

        return messages

    def _serialize_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively serialize dictionary with Pydantic models.

        Args:
            d: Dictionary to serialize

        Returns:
            Serialized dictionary
        """
        result = {}
        for key, value in d.items():
            if hasattr(value, 'model_dump'):
                result[key] = value.model_dump()
            elif hasattr(value, 'dict'):
                result[key] = value.dict()
            elif isinstance(value, dict):
                result[key] = self._serialize_dict(value)
            elif isinstance(value, list):
                result[key] = [self._serialize_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
        return result

    def _call_llm(
        self,
        messages: List[Dict[str, str]],
        expect_json: bool = False,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Union[str, Dict[str, Any]]:
        """Call LLM with prepared messages.

        Args:
            messages: List of message dictionaries
            expect_json: Whether to expect JSON response
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments for LLM call

        Returns:
            LLM response as string or parsed JSON
        """
        try:
            if expect_json:
                return self.llm_client.chat_completion_json(
                    messages,
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )
            else:
                return self.llm_client.chat_completion_with_retry(
                    messages,
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )

        except Exception as e:
            self.logger.error(f"LLM call failed for agent {self.name}: {str(e)}")
            raise

    def _record_execution(
        self,
        task: str,
        context: Dict[str, Any],
        result: AgentResult,
        execution_time: float,
    ) -> None:
        """Record execution details.

        Args:
            task: Task description
            context: Context information
            result: Execution result
            execution_time: Execution time in seconds
        """
        record = {
            "agent": self.name,
            "task": task,
            "context_keys": list(context.keys()),
            "result_success": result.success,
            "execution_time": execution_time,
            "timestamp": time.time(),
        }

        if not result.success:
            record["error"] = result.error

        self.execution_history.append(record)

        self.logger.info(
            f"Agent {self.name} executed task in {execution_time:.2f}s. "
            f"Success: {result.success}"
        )

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics.

        Returns:
            Dictionary with execution statistics
        """
        if not self.execution_history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
            }

        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r["result_success"])
        avg_time = (
            sum(r["execution_time"] for r in self.execution_history) / total
            if total > 0
            else 0
        )

        return {
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "avg_execution_time": avg_time,
        }

    def reset_history(self) -> None:
        """Reset execution history."""
        self.execution_history.clear()
        self.logger.info(f"Agent {self.name} execution history reset")


# Import time module for execution timing
import time