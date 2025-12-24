"""
Writing Optimizer Agent - Optimizes writing style, language expression, and literary quality.
"""

import json
import time
from typing import Dict, Any, Optional

from src.agents.base_agent import BaseAgent, AgentResult
from src.models import NovelInput


class WritingOptimizerAgent(BaseAgent):
    """Writing optimizer agent that improves writing style and language expression."""

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """Initialize writing optimizer agent.

        Args:
            llm_provider: LLM provider
            temperature: Sampling temperature
        """
        system_prompt = """你是小说文笔优化师，专门负责优化语言表达、提升文学性和改善阅读体验。

你的职责：
1. 优化语言表达，使文笔更加优美流畅
2. 提升文学性，增强艺术感染力
3. 改善阅读体验，使文字更加生动有趣
4. 调整语言风格，使其符合小说类型要求
5. 润色文字，消除冗余和生硬表达

优化原则：
1. 语言要优美流畅，有节奏感
2. 表达要准确生动，有画面感
3. 风格要符合小说类型和读者期待
4. 文字要有文学性和艺术性
5. 阅读体验要舒适自然
6. 保持原文的核心内容和情感

请以专业、细腻的态度进行文笔优化。"""

        super().__init__(
            name="文笔优化师",
            role="小说文笔优化师",
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            temperature=temperature,
        )

    def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Execute writing optimization task.

        Args:
            task: Task description
            context: Context information

        Returns:
            AgentResult with optimized writing
        """
        start_time = time.time()

        try:
            # Parse novel input from context
            novel_input = self._parse_novel_input(context)

            # Determine task type
            if "语言优化" in task or "language" in task.lower():
                result = self._optimize_language_expression(novel_input, context)
            elif "文学性" in task or "literary" in task.lower():
                result = self._enhance_literary_quality(novel_input, context)
            elif "风格调整" in task or "style" in task.lower():
                result = self._adjust_writing_style(novel_input, context)
            elif "润色" in task or "polish" in task.lower():
                result = self._polish_text(novel_input, context)
            elif "阅读体验" in task or "readability" in task.lower():
                result = self._improve_readability(novel_input, context)
            else:
                # Default: complete writing optimization
                result = self._complete_writing_optimization(novel_input, context)

            execution_time = time.time() - start_time
            self._record_execution(task, context, result, execution_time)

            return result

        except Exception as e:
            self.logger.error(f"Writing optimizer agent execution failed: {str(e)}")
            execution_time = time.time() - start_time
            error_result = AgentResult(
                content="",
                metadata={"error": str(e), "task": task},
                success=False,
                error=str(e),
            )
            self._record_execution(task, context, error_result, execution_time)
            return error_result

    def _parse_novel_input(self, context: Dict[str, Any]) -> NovelInput:
        """Parse novel input from context.

        Args:
            context: Context dictionary

        Returns:
            NovelInput object
        """
        # Check if NovelInput is already in context
        if "novel_input" in context and isinstance(context["novel_input"], NovelInput):
            return context["novel_input"]

        # Try to create from dict
        try:
            return NovelInput(**context)
        except Exception as e:
            raise ValueError(f"Failed to parse novel input from context: {str(e)}")

    def _optimize_language_expression(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Optimize language expression.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with optimized language
        """
        # Get text to optimize from context
        text_to_optimize = context.get("text", "")
        if not text_to_optimize:
            text_to_optimize = context.get("chapter_content", "")

        original_length = len(text_to_optimize)

        task_description = f"""优化以下小说章节的语言表达：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
目标读者：{novel_input.target_audience or '一般读者'}

待优化文本（前1000字）：
{text_to_optimize[:1000]}{'...' if len(text_to_optimize) > 1000 else ''}

优化要求：
1. 使语言更加优美流畅
2. 增强表达的准确性和生动性
3. 改善句子结构和节奏感
4. 丰富词汇选择，避免重复
5. 保持原文的核心内容和情感
6. 符合{novel_input.genre}类型的语言特点

请直接输出优化后的文本，不需要额外说明。"""

        messages = self._prepare_messages(task_description, context)
        optimized_text = self._call_llm(messages, expect_json=False, max_tokens=original_length + 500)

        return AgentResult(
            content=optimized_text,
            metadata={
                "optimization_type": "language_expression",
                "original_length": original_length,
                "optimized_length": len(optimized_text),
                "length_change": len(optimized_text) - original_length,
                "genre": novel_input.genre,
            },
        )

    def _enhance_literary_quality(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Enhance literary quality.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with enhanced literary text
        """
        # Get text to enhance from context
        text_to_enhance = context.get("text", "")
        if not text_to_enhance:
            text_to_enhance = context.get("chapter_content", "")

        original_length = len(text_to_enhance)

        task_description = f"""提升以下小说章节的文学性：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
文学风格：{novel_input.writing_style or '一般文学风格'}

待提升文本（前1000字）：
{text_to_enhance[:1000]}{'...' if len(text_to_enhance) > 1000 else ''}

提升要求：
1. 增强文学性和艺术感染力
2. 丰富修辞手法（比喻、拟人、排比等）
3. 深化主题表达和思想内涵
4. 增强情感共鸣和感染力
5. 提升文字的审美价值和艺术性
6. 保持故事的可读性和流畅性

请直接输出提升后的文本，不需要额外说明。"""

        messages = self._prepare_messages(task_description, context)
        enhanced_text = self._call_llm(messages, expect_json=False, max_tokens=original_length + 500)

        return AgentResult(
            content=enhanced_text,
            metadata={
                "optimization_type": "literary_quality",
                "original_length": original_length,
                "enhanced_length": len(enhanced_text),
                "length_change": len(enhanced_text) - original_length,
                "genre": novel_input.genre,
                "writing_style": novel_input.writing_style or "一般",
            },
        )

    def _adjust_writing_style(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Adjust writing style.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with style-adjusted text
        """
        # Get text to adjust from context
        text_to_adjust = context.get("text", "")
        if not text_to_adjust:
            text_to_adjust = context.get("chapter_content", "")

        original_length = len(text_to_adjust)
        target_style = context.get("target_style", novel_input.writing_style or f"{novel_input.genre}风格")

        task_description = f"""调整以下小说章节的写作风格：

当前风格：待分析
目标风格：{target_style}
小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}

待调整文本（前1000字）：
{text_to_adjust[:1000]}{'...' if len(text_to_adjust) > 1000 else ''}

调整要求：
1. 将文本风格调整为{target_style}
2. 调整语言特点：词汇选择、句式结构、修辞手法等
3. 调整叙事节奏和语调
4. 调整情感表达方式
5. 保持故事内容和情节不变
6. 确保风格调整自然流畅

请直接输出调整后的文本，不需要额外说明。"""

        messages = self._prepare_messages(task_description, context)
        adjusted_text = self._call_llm(messages, expect_json=False, max_tokens=original_length + 500)

        return AgentResult(
            content=adjusted_text,
            metadata={
                "optimization_type": "writing_style",
                "original_length": original_length,
                "adjusted_length": len(adjusted_text),
                "length_change": len(adjusted_text) - original_length,
                "target_style": target_style,
                "genre": novel_input.genre,
            },
        )

    def _polish_text(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Polish and refine text.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with polished text
        """
        # Get text to polish from context
        text_to_polish = context.get("text", "")
        if not text_to_polish:
            text_to_polish = context.get("chapter_content", "")

        original_length = len(text_to_polish)

        task_description = f"""润色以下小说章节：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}

待润色文本（前1000字）：
{text_to_polish[:1000]}{'...' if len(text_to_polish) > 1000 else ''}

润色要求：
1. 消除冗余和重复表达
2. 修正生硬和不自然的表达
3. 优化句子流畅度和连贯性
4. 统一术语和表达方式
5. 修正语法和标点错误
6. 提升整体文字质量
7. 保持原文的核心内容和风格

请直接输出润色后的文本，不需要额外说明。"""

        messages = self._prepare_messages(task_description, context)
        polished_text = self._call_llm(messages, expect_json=False, max_tokens=original_length + 300)

        return AgentResult(
            content=polished_text,
            metadata={
                "optimization_type": "text_polishing",
                "original_length": original_length,
                "polished_length": len(polished_text),
                "length_change": len(polished_text) - original_length,
                "genre": novel_input.genre,
            },
        )

    def _improve_readability(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Improve text readability.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with improved readability text
        """
        # Get text to improve from context
        text_to_improve = context.get("text", "")
        if not text_to_improve:
            text_to_improve = context.get("chapter_content", "")

        original_length = len(text_to_improve)
        target_audience = novel_input.target_audience or "一般读者"

        task_description = f"""改善以下小说章节的阅读体验：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
目标读者：{target_audience}

待改善文本（前1000字）：
{text_to_improve[:1000]}{'...' if len(text_to_improve) > 1000 else ''}

改善要求：
1. 提升文本的可读性和易理解性
2. 调整句子长度和复杂度，适合{target_audience}阅读
3. 改善段落结构和逻辑连贯性
4. 增强阅读流畅度和舒适度
5. 保持故事的趣味性和吸引力
6. 符合目标读者的阅读习惯和水平

请直接输出改善后的文本，不需要额外说明。"""

        messages = self._prepare_messages(task_description, context)
        improved_text = self._call_llm(messages, expect_json=False, max_tokens=original_length + 500)

        return AgentResult(
            content=improved_text,
            metadata={
                "optimization_type": "readability",
                "original_length": original_length,
                "improved_length": len(improved_text),
                "length_change": len(improved_text) - original_length,
                "target_audience": target_audience,
                "genre": novel_input.genre,
            },
        )

    def _complete_writing_optimization(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Complete writing optimization including all elements.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with complete optimization
        """
        # Get text to optimize from context
        text_to_optimize = context.get("text", "")
        if not text_to_optimize:
            text_to_optimize = context.get("chapter_content", "")

        if not text_to_optimize:
            return AgentResult(
                content="",
                metadata={"error": "No text provided for optimization"},
                success=False,
                error="No text provided for optimization",
            )

        original_length = len(text_to_optimize)
        target_style = novel_input.writing_style or f"{novel_input.genre}风格"
        target_audience = novel_input.target_audience or "一般读者"

        task_description = f"""对以下小说章节进行完整的文笔优化：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
目标风格：{target_style}
目标读者：{target_audience}

待优化文本（前1500字）：
{text_to_optimize[:1500]}{'...' if len(text_to_optimize) > 1500 else ''}

优化要求（包含以下所有方面）：
1. 语言表达优化：使语言更加优美流畅
2. 文学性提升：增强艺术感染力和审美价值
3. 风格调整：调整为{target_style}
4. 文字润色：消除冗余，修正错误，提升质量
5. 阅读体验改善：提升可读性，适合{target_audience}阅读
6. 优化总结：说明主要优化点和效果

请以JSON格式返回完整的优化方案，包含优化后的文本和优化说明。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=original_length + 1000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "optimization_type": "complete_optimization",
                "original_length": original_length,
                "optimized_length": len(response.get("optimized_text", "")),
                "length_change": len(response.get("optimized_text", "")) - original_length,
                "optimization_aspects": list(response.keys()),
                "genre": novel_input.genre,
                "target_style": target_style,
                "target_audience": target_audience,
            },
        )

    def analyze_writing_quality(
        self, text: str, novel_input: NovelInput, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze writing quality.

        Args:
            text: Text to analyze
            novel_input: Novel input data
            context: Context information

        Returns:
            Analysis results
        """
        analysis_task = f"""分析以下小说章节的写作质量：

小说类型：{novel_input.genre}
目标风格：{novel_input.writing_style or f'{novel_input.genre}风格'}
目标读者：{novel_input.target_audience or '一般读者'}

待分析文本（前800字）：
{text[:800]}{'...' if len(text) > 800 else ''}

分析维度：
1. 语言表达：优美度、流畅度、准确性
2. 文学性：艺术感染力、修辞手法、思想深度
3. 风格一致性：是否符合{novel_input.genre}风格
4. 可读性：阅读流畅度、理解难度
5. 情感表达：情感感染力、共鸣度
6. 改进建议：具体改进点和建议

请以JSON格式返回分析结果。"""

        messages = self._prepare_messages(analysis_task, context)
        analysis_result = self._call_llm(messages, expect_json=True, max_tokens=1500)

        return analysis_result

    def calculate_readability_score(
        self, text: str
    ) -> Dict[str, Any]:
        """Calculate readability score.

        Args:
            text: Text to analyze

        Returns:
            Readability metrics
        """
        # Simple readability metrics (can be enhanced)
        words = text.split()
        sentences = text.replace('!', '.').replace('?', '.').split('.')

        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0

        # Simple readability score (lower is easier to read)
        readability_score = (avg_sentence_length * 0.4) + (avg_word_length * 0.6)

        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "avg_word_length": round(avg_word_length, 2),
            "readability_score": round(readability_score, 2),
            "readability_level": self._get_readability_level(readability_score),
        }

    def _get_readability_level(self, score: float) -> str:
        """Get readability level from score.

        Args:
            score: Readability score

        Returns:
            Readability level description
        """
        if score < 15:
            return "非常易读（适合所有读者）"
        elif score < 20:
            return "易读（适合一般读者）"
        elif score < 25:
            return "中等（需要一定阅读能力）"
        elif score < 30:
            return "较难（需要较高阅读能力）"
        else:
            return "很难（需要专业阅读能力）"