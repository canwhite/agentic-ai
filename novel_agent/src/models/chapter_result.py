"""
Chapter result data models.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ChapterMetadata(BaseModel):
    """Metadata for generated chapter."""

    word_count: int = Field(..., description="Word count of the chapter")
    character_count: int = Field(..., description="Character count of the chapter")
    generation_time: float = Field(..., description="Generation time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    model_used: str = Field(..., description="LLM model used for generation")
    agent_stats: Dict[str, Any] = Field(
        default_factory=dict, description="Statistics from each agent"
    )
    quality_metrics: Dict[str, float] = Field(
        default_factory=dict,
        description="Quality metrics (coherence, tension, character_consistency, etc.)",
    )
    warnings: List[str] = Field(
        default_factory=list, description="Warnings or issues detected"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Suggestions for improvement"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "word_count": 2150,
                "character_count": 4300,
                "generation_time": 45.2,
                "timestamp": "2025-12-24T16:30:00",
                "model_used": "deepseek-chat",
                "agent_stats": {
                    "director": {"executions": 3, "success_rate": 1.0},
                    "plot_designer": {"executions": 1, "success_rate": 1.0},
                },
                "quality_metrics": {
                    "coherence": 0.85,
                    "tension": 0.92,
                    "character_consistency": 0.88,
                    "scene_vividness": 0.79,
                },
                "warnings": ["人物对话略显生硬", "场景转换稍快"],
                "suggestions": ["可增加人物心理描写", "可细化场景细节"],
            }
        }


class ChapterResult(BaseModel):
    """Result of chapter generation."""

    content: str = Field(..., description="Generated chapter content")
    metadata: ChapterMetadata = Field(..., description="Chapter metadata")
    intermediate_results: Optional[Dict[str, Any]] = Field(
        None, description="Intermediate results from agents"
    )
    raw_agent_outputs: Optional[Dict[str, Any]] = Field(
        None, description="Raw outputs from each agent"
    )
    format: str = Field(default="text", description="Output format (text or json)")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        result = {
            "content": self.content,
            "metadata": self.metadata.dict(),
            "format": self.format,
        }

        if self.intermediate_results:
            result["intermediate_results"] = self.intermediate_results

        if self.raw_agent_outputs:
            result["raw_agent_outputs"] = self.raw_agent_outputs

        return result

    def to_json(self) -> str:
        """Convert to JSON string.

        Returns:
            JSON string representation
        """
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def get_quality_score(self) -> float:
        """Calculate overall quality score.

        Returns:
            Quality score from 0 to 1
        """
        if not self.metadata.quality_metrics:
            return 0.0

        metrics = self.metadata.quality_metrics
        weights = {
            "coherence": 0.3,
            "tension": 0.25,
            "character_consistency": 0.25,
            "scene_vividness": 0.2,
        }

        score = 0.0
        total_weight = 0.0

        for metric, weight in weights.items():
            if metric in metrics:
                score += metrics[metric] * weight
                total_weight += weight

        return score / total_weight if total_weight > 0 else 0.0

    def get_warnings_summary(self) -> str:
        """Get warnings summary.

        Returns:
            Formatted warnings summary
        """
        if not self.metadata.warnings:
            return "无警告"

        return "\n".join(f"- {warning}" for warning in self.metadata.warnings)

    def get_suggestions_summary(self) -> str:
        """Get suggestions summary.

        Returns:
            Formatted suggestions summary
        """
        if not self.metadata.suggestions:
            return "无建议"

        return "\n".join(f"- {suggestion}" for suggestion in self.metadata.suggestions)

    def print_summary(self) -> None:
        """Print chapter summary."""
        print("=" * 60)
        print("章节生成结果摘要")
        print("=" * 60)
        print(f"字数: {self.metadata.word_count} 字")
        print(f"生成时间: {self.metadata.generation_time:.2f} 秒")
        print(f"使用模型: {self.metadata.model_used}")
        print(f"质量评分: {self.get_quality_score():.2%}")
        print()

        if self.metadata.quality_metrics:
            print("质量指标:")
            for metric, score in self.metadata.quality_metrics.items():
                print(f"  - {metric}: {score:.2%}")

        print()
        print("警告:")
        print(self.get_warnings_summary())

        print()
        print("改进建议:")
        print(self.get_suggestions_summary())
        print("=" * 60)

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "content": "第一章：秘境奇遇\n\n林风站在上古秘境的入口处，心中涌起一股莫名的激动...",
                "metadata": {
                    "word_count": 2150,
                    "character_count": 4300,
                    "generation_time": 45.2,
                    "timestamp": "2025-12-24T16:30:00",
                    "model_used": "deepseek-chat",
                    "quality_metrics": {
                        "coherence": 0.85,
                        "tension": 0.92,
                        "character_consistency": 0.88,
                    },
                    "warnings": [],
                    "suggestions": [],
                },
                "format": "text",
            }
        }