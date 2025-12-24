"""
Consistency Checker Agent - Checks plot logic, character consistency, and overall coherence.
"""

import json
import time
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent, AgentResult
from src.models import NovelInput, ChapterDraft


class ConsistencyCheckerAgent(BaseAgent):
    """Consistency checker agent that ensures overall coherence and implements anti-collapse mechanisms."""

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """Initialize consistency checker agent.

        Args:
            llm_provider: LLM provider
            temperature: Sampling temperature
        """
        system_prompt = """你是小说连贯性检查员，专门负责检查情节逻辑、人物一致性和整体连贯性，实施"三板斧"防崩机制。

你的职责：
1. 检查情节逻辑的合理性和连贯性
2. 检查人物行为的一致性，防止OOC（Out of Character）
3. 检查整体故事的连贯性和自洽性
4. 实施"三板斧"防崩机制
5. 提供具体的改进建议

"三板斧"防崩机制：
1. 防"水"：检查有无无意义的内容填充
2. 防崩人设：检查人物性格是否崩坏
3. 防OOC：检查人物行为是否符合设定

检查原则：
1. 严谨细致，不放过任何不一致之处
2. 客观公正，基于设定和逻辑进行检查
3. 具体明确，指出具体问题和改进建议
4. 全面覆盖，检查所有关键方面
5. 注重实效，提供可操作的改进方案

请以专业、严谨的态度进行检查工作。"""

        super().__init__(
            name="连贯性检查员",
            role="小说连贯性检查员",
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            temperature=temperature,
        )

    def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Execute consistency check task.

        Args:
            task: Task description
            context: Context information

        Returns:
            AgentResult with consistency check results
        """
        start_time = time.time()

        try:
            # Parse novel input from context
            novel_input = self._parse_novel_input(context)

            # Determine task type
            if "情节逻辑" in task or "plot" in task.lower():
                result = self._check_plot_logic(novel_input, context)
            elif "人物一致性" in task or "character" in task.lower():
                result = self._check_character_consistency(novel_input, context)
            elif "整体连贯性" in task or "overall" in task.lower():
                result = self._check_overall_coherence(novel_input, context)
            elif "三板斧" in task or "anti-collapse" in task.lower():
                result = self._perform_anti_collapse_check(novel_input, context)
            elif "时间线" in task or "timeline" in task.lower():
                result = self._check_timeline_consistency(novel_input, context)
            else:
                # Default: complete consistency check
                result = self._complete_consistency_check(novel_input, context)

            execution_time = time.time() - start_time
            self._record_execution(task, context, result, execution_time)

            return result

        except Exception as e:
            self.logger.error(f"Consistency checker agent execution failed: {str(e)}")
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

    def _check_plot_logic(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Check plot logic and coherence.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with plot logic check results
        """
        # Get plot information from context
        plot_structure = context.get("plot_structure", "")
        plot_points = context.get("plot_points", [])
        chapter_content = context.get("chapter_content", "")

        task_description = f"""检查以下小说章节的情节逻辑：

小说类型：{novel_input.genre}
整体大纲：{novel_input.overall_outline[:200] if novel_input.overall_outline else '无'}
本章提纲：{novel_input.chapter_outline}

情节结构：
{plot_structure if plot_structure else '无具体结构'}

情节点：
{json.dumps(plot_points[:10], ensure_ascii=False, indent=2) if plot_points else '无具体情节点'}

章节内容（前1500字）：
{chapter_content[:1500]}{'...' if len(chapter_content) > 1500 else ''}

检查要点：
1. 情节发展是否合理，有无逻辑漏洞
2. 冲突设置是否恰当，解决是否合理
3. 悬念设置是否有效，解答是否满意
4. 情感曲线是否自然，起伏是否合理
5. 情节节奏是否恰当，快慢是否合适
6. 与整体大纲是否一致，有无矛盾

请以JSON格式返回情节逻辑检查结果，包含问题列表和改进建议。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "check_type": "plot_logic",
                "issues_found": len(response.get("issues", [])),
                "suggestions_count": len(response.get("suggestions", [])),
                "plot_points_checked": len(plot_points),
                "content_length": len(chapter_content),
            },
        )

    def _check_character_consistency(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Check character consistency.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with character consistency check results
        """
        # Get character information from context
        character_performance = context.get("character_performance", {})
        chapter_content = context.get("chapter_content", "")

        task_description = f"""检查以下小说章节的人物一致性：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}

人物设定：
{self._format_characters_for_prompt(novel_input.characters)}

人物表现：
{json.dumps(character_performance, ensure_ascii=False, indent=2) if character_performance else '无具体表现数据'}

章节内容（前1500字）：
{chapter_content[:1500]}{'...' if len(chapter_content) > 1500 else ''}

检查要点（"三板斧"防崩机制）：
1. 防OOC：人物行为是否符合设定？
   - 性格一致性：行为是否与性格匹配
   - 背景一致性：行为是否与背景相符
   - 能力一致性：行为是否与能力匹配
2. 防崩人设：人物性格是否崩坏？
   - 性格稳定性：性格是否突然变化
   - 行为合理性：行为是否有合理动机
   - 情感真实性：情感是否真实可信
3. 防水：人物表现是否空洞无物？
   - 对话质量：对话是否有意义
   - 行为价值：行为是否推动情节
   - 情感深度：情感是否有层次

请以JSON格式返回人物一致性检查结果，包含问题列表和改进建议。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2500)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "check_type": "character_consistency",
                "characters_checked": len(novel_input.characters),
                "anti_collapse_checks": ["防OOC", "防崩人设", "防水"],
                "issues_found": sum(len(check.get("issues", [])) for check in response.get("checks", {}).values()),
                "suggestions_count": sum(len(check.get("suggestions", [])) for check in response.get("checks", {}).values()),
            },
        )

    def _format_characters_for_prompt(self, characters: List[Any]) -> str:
        """Format characters for prompt.

        Args:
            characters: List of character objects

        Returns:
            Formatted string
        """
        if not characters:
            return "无具体人物设定"

        formatted = []
        for char in characters:
            char_info = f"- {char.name} ({char.role})"
            char_info += f"\n  性格：{char.personality}"
            char_info += f"\n  背景：{char.background}"
            if hasattr(char, 'speech_style') and char.speech_style:
                char_info += f"\n  说话风格：{char.speech_style}"
            formatted.append(char_info)

        return "\n\n".join(formatted)

    def _check_overall_coherence(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Check overall story coherence.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with overall coherence check results
        """
        # Get all relevant information from context
        plot_structure = context.get("plot_structure", "")
        character_performance = context.get("character_performance", {})
        scene_rendering = context.get("scene_rendering", {})
        chapter_content = context.get("chapter_content", "")

        task_description = f"""检查以下小说章节的整体连贯性：

小说类型：{novel_input.genre}
整体大纲：{novel_input.overall_outline[:200] if novel_input.overall_outline else '无'}
本章提纲：{novel_input.chapter_outline}

情节结构：
{plot_structure if plot_structure else '无具体结构'}

人物表现摘要：
{json.dumps({k: v.get('summary', '无摘要') for k, v in character_performance.items()}, ensure_ascii=False, indent=2) if character_performance else '无人物表现'}

场景渲染摘要：
{json.dumps({k: v.get('summary', '无摘要') for k, v in scene_rendering.items()}, ensure_ascii=False, indent=2) if scene_rendering else '无场景渲染'}

章节内容（前2000字）：
{chapter_content[:2000]}{'...' if len(chapter_content) > 2000 else ''}

检查要点：
1. 情节-人物一致性：情节发展是否与人物表现一致
2. 人物-场景一致性：人物行为是否与场景氛围一致
3. 场景-情节一致性：场景设置是否服务于情节发展
4. 整体自洽性：所有元素是否构成有机整体
5. 风格统一性：语言风格、叙事风格是否统一
6. 主题连贯性：主题表达是否贯穿始终

请以JSON格式返回整体连贯性检查结果，包含问题列表和改进建议。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=3000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "check_type": "overall_coherence",
                "coherence_dimensions": ["情节-人物", "人物-场景", "场景-情节", "整体自洽", "风格统一", "主题连贯"],
                "issues_found": len(response.get("issues", [])),
                "suggestions_count": len(response.get("suggestions", [])),
                "content_length": len(chapter_content),
            },
        )

    def _perform_anti_collapse_check(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Perform anti-collapse mechanism check.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with anti-collapse check results
        """
        chapter_content = context.get("chapter_content", "")

        task_description = f"""对以下小说章节实施"三板斧"防崩机制检查：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}

章节内容（前2000字）：
{chapter_content[:2000]}{'...' if len(chapter_content) > 2000 else ''}

"三板斧"检查标准：

1. 防"水"检查（避免无意义内容填充）：
   - 每段文字是否都有明确目的（推进情节、塑造人物、营造氛围等）
   - 有无冗余描述、重复表达、空洞对话
   - 信息密度是否合理，有无注水嫌疑
   - 节奏控制是否恰当，有无拖沓之处

2. 防崩人设检查（防止人物性格崩坏）：
   - 人物行为是否符合其性格设定
   - 人物情感变化是否自然合理
   - 人物成长是否有合理轨迹
   - 人物关系发展是否真实可信

3. 防OOC检查（防止人物行为不符合设定）：
   - 人物言行是否与其背景、能力匹配
   - 人物在特定情境下的反应是否合理
   - 人物决策是否符合其价值观和动机
   - 人物是否有突然的性格或能力变化

请对每个方面进行详细检查，指出具体问题，提供改进建议。
请以JSON格式返回"三板斧"检查结果。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=3000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "check_type": "anti_collapse",
                "mechanisms": ["防'水'", "防崩人设", "防OOC"],
                "issues_by_mechanism": {mechanism: len(response.get(mechanism, {}).get("issues", [])) for mechanism in ["防'水'", "防崩人设", "防OOC"]},
                "total_issues": sum(len(response.get(mechanism, {}).get("issues", [])) for mechanism in ["防'水'", "防崩人设", "防OOC"]),
                "content_length": len(chapter_content),
            },
        )

    def _check_timeline_consistency(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Check timeline consistency.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with timeline check results
        """
        # Get timeline information from context
        timeline_info = context.get("timeline", {})
        scene_times = context.get("scene_times", {})
        chapter_content = context.get("chapter_content", "")

        task_description = f"""检查以下小说章节的时间线一致性：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}

时间线信息：
{json.dumps(timeline_info, ensure_ascii=False, indent=2) if timeline_info else '无具体时间线'}

场景时间：
{json.dumps(scene_times, ensure_ascii=False, indent=2) if scene_times else '无场景时间信息'}

章节内容（前1500字）：
{chapter_content[:1500]}{'...' if len(chapter_content) > 1500 else ''}

检查要点：
1. 时间顺序是否合理，有无时间跳跃矛盾
2. 时间跨度是否恰当，节奏是否合理
3. 时间提示是否清晰，读者能否理解时间流逝
4. 时间与情节发展的匹配度
5. 时间与人物成长的同步性
6. 时间与场景变化的协调性

请以JSON格式返回时间线一致性检查结果，包含问题列表和改进建议。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "check_type": "timeline_consistency",
                "timeline_points": len(timeline_info) if timeline_info else 0,
                "scenes_with_time": len(scene_times),
                "issues_found": len(response.get("issues", [])),
                "suggestions_count": len(response.get("suggestions", [])),
            },
        )

    def _complete_consistency_check(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Perform complete consistency check including all aspects.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with complete check results
        """
        # Get all relevant information from context
        plot_structure = context.get("plot_structure", "")
        plot_points = context.get("plot_points", [])
        character_performance = context.get("character_performance", {})
        scene_rendering = context.get("scene_rendering", {})
        timeline_info = context.get("timeline", {})
        chapter_content = context.get("chapter_content", "")

        if not chapter_content:
            return AgentResult(
                content="",
                metadata={"error": "No chapter content provided for check"},
                success=False,
                error="No chapter content provided for check",
            )

        task_description = f"""对以下小说章节进行完整的连贯性检查：

小说类型：{novel_input.genre}
整体大纲：{novel_input.overall_outline[:200] if novel_input.overall_outline else '无'}
本章提纲：{novel_input.chapter_outline}

情节结构：
{plot_structure if plot_structure else '无具体结构'}

关键情节点（前5个）：
{json.dumps(plot_points[:5], ensure_ascii=False, indent=2) if plot_points else '无具体情节点'}

人物表现摘要：
{json.dumps({k: v.get('summary', '无摘要') for k, v in character_performance.items()}, ensure_ascii=False, indent=2) if character_performance else '无人物表现'}

场景渲染摘要：
{json.dumps({k: v.get('summary', '无摘要') for k, v in scene_rendering.items()}, ensure_ascii=False, indent=2) if scene_rendering else '无场景渲染'}

时间线信息：
{json.dumps(timeline_info, ensure_ascii=False, indent=2) if timeline_info else '无具体时间线'}

章节内容（前2500字）：
{chapter_content[:2500]}{'...' if len(chapter_content) > 2500 else ''}

检查要求（包含以下所有方面）：
1. 情节逻辑检查：情节发展是否合理
2. 人物一致性检查：实施"三板斧"防崩机制
3. 整体连贯性检查：各元素协调性
4. 时间线一致性检查：时间顺序和跨度
5. 综合评估：整体质量评分和改进优先级
6. 具体建议：可操作的改进方案

请以JSON格式返回完整的连贯性检查报告。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=4000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "check_type": "complete_consistency",
                "check_aspects": list(response.keys()),
                "content_length": len(chapter_content),
                "plot_points_checked": len(plot_points),
                "characters_checked": len(character_performance),
                "scenes_checked": len(scene_rendering),
                "has_timeline_check": "timeline" in response,
                "has_anti_collapse_check": "anti_collapse" in response,
            },
        )

    def calculate_coherence_score(
        self, check_results: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate coherence score from check results.

        Args:
            check_results: Consistency check results
            context: Context information

        Returns:
            Coherence score and metrics
        """
        # Extract issues from check results
        total_issues = 0
        issue_severity = {"low": 0, "medium": 0, "high": 0}

        # Count issues from different check types
        for check_type, check_data in check_results.items():
            if isinstance(check_data, dict):
                issues = check_data.get("issues", [])
                total_issues += len(issues)

                # Simple severity estimation based on issue description
                for issue in issues:
                    issue_lower = issue.lower()
                    if any(word in issue_lower for word in ["严重", "重大", "致命", "矛盾", "崩坏"]):
                        issue_severity["high"] += 1
                    elif any(word in issue_lower for word in ["问题", "不一致", "不合理", "需要改进"]):
                        issue_severity["medium"] += 1
                    else:
                        issue_severity["low"] += 1

        # Calculate base score (100 - issues * weight)
        high_weight = 5
        medium_weight = 3
        low_weight = 1

        penalty = (
            issue_severity["high"] * high_weight +
            issue_severity["medium"] * medium_weight +
            issue_severity["low"] * low_weight
        )

        base_score = max(0, 100 - penalty)

        # Adjust score based on content length
        content_length = context.get("content_length", 0)
        if content_length > 0:
            # Normalize by content length (more content, more potential issues)
            length_factor = min(1.0, content_length / 5000)  # Cap at 5000 chars
            adjusted_score = base_score * (1.0 - length_factor * 0.2)  # Max 20% reduction
        else:
            adjusted_score = base_score

        return {
            "total_issues": total_issues,
            "issue_severity": issue_severity,
            "base_score": round(base_score, 1),
            "adjusted_score": round(adjusted_score, 1),
            "coherence_level": self._get_coherence_level(adjusted_score),
            "improvement_priority": self._get_improvement_priority(issue_severity),
        }

    def _get_coherence_level(self, score: float) -> str:
        """Get coherence level from score.

        Args:
            score: Coherence score

        Returns:
            Coherence level description
        """
        if score >= 90:
            return "优秀（高度连贯）"
        elif score >= 80:
            return "良好（基本连贯）"
        elif score >= 70:
            return "一般（有些问题）"
        elif score >= 60:
            return "需要改进（较多问题）"
        else:
            return "问题严重（需要大改）"

    def _get_improvement_priority(self, issue_severity: Dict[str, int]) -> List[str]:
        """Get improvement priority based on issue severity.

        Args:
            issue_severity: Issue severity counts

        Returns:
            List of improvement priorities
        """
        priorities = []

        if issue_severity["high"] > 0:
            priorities.append("高优先级：修复严重问题（情节矛盾、人物崩坏等）")

        if issue_severity["medium"] > 0:
            priorities.append("中优先级：改进一般问题（逻辑不合理、表达不清等）")

        if issue_severity["low"] > 0:
            priorities.append("低优先级：优化细节问题（语言表达、节奏控制等）")

        if not priorities:
            priorities.append("无需重大改进，可进行微调优化")

        return priorities