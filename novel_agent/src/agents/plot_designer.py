"""
Plot Design Agent - Designs plot structure and narrative flow for novel chapters.
"""

import json
import time
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent, AgentResult
from src.models import NovelInput, ChapterDraft, PlotPoint


class PlotDesignAgent(BaseAgent):
    """Plot design agent that creates plot structure and narrative flow."""

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """Initialize plot design agent.

        Args:
            llm_provider: LLM provider
            temperature: Sampling temperature
        """
        system_prompt = """你是小说情节设计师，专门负责设计章节的情节结构和叙事流程。

你的职责：
1. 根据大纲设计具体的情节发展
2. 创建合理的叙事节奏和情感曲线
3. 设置冲突、悬念、转折点等关键情节点
4. 确保情节逻辑连贯，符合故事类型
5. 设计章节的开头、发展、高潮、结尾结构

设计原则：
1. 开头要吸引人，快速建立场景和冲突
2. 发展要合理推进，保持读者兴趣
3. 高潮要有足够的张力和情感冲击
4. 结尾要留有悬念或完成小闭环
5. 情感曲线要起伏有致，避免平淡

请以专业、创新的态度设计情节。"""

        super().__init__(
            name="情节设计师",
            role="小说情节设计师",
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            temperature=temperature,
        )

    def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Execute plot design task.

        Args:
            task: Task description
            context: Context information

        Returns:
            AgentResult with plot design
        """
        start_time = time.time()

        try:
            # Parse novel input from context
            novel_input = self._parse_novel_input(context)

            # Determine task type
            if "情节结构" in task or "plot structure" in task.lower():
                result = self._design_plot_structure(novel_input, context)
            elif "情节点" in task or "plot points" in task.lower():
                result = self._design_plot_points(novel_input, context)
            elif "情感曲线" in task or "emotional curve" in task.lower():
                result = self._design_emotional_curve(novel_input, context)
            elif "冲突设计" in task or "conflict" in task.lower():
                result = self._design_conflicts(novel_input, context)
            else:
                # Default: design complete plot structure
                result = self._design_complete_plot(novel_input, context)

            execution_time = time.time() - start_time
            self._record_execution(task, context, result, execution_time)

            return result

        except Exception as e:
            self.logger.error(f"Plot design agent execution failed: {str(e)}")
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

    def _design_plot_structure(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design overall plot structure.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with plot structure
        """
        task_description = f"""为以下小说章节设计完整的情节结构：

小说类型：{novel_input.genre}
整体大纲：{novel_input.overall_outline}
本章提纲：{novel_input.chapter_outline}
人物列表：{', '.join([char.name for char in novel_input.characters])}
场景列表：{', '.join([scene.name for scene in novel_input.scenes])}

设计要求：
1. 设计章节的完整情节结构（开头、发展、高潮、结尾）
2. 确定叙事视角和节奏
3. 规划场景转换和时空安排
4. 考虑人物出场顺序和互动时机
5. 确保情节符合{novel_input.genre}类型的特点

请以JSON格式返回情节结构设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=1500)

        # Validate and format response
        plot_structure = self._validate_plot_structure(response, novel_input)

        return AgentResult(
            content=json.dumps(plot_structure, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "plot_structure",
                "novel_genre": novel_input.genre,
                "structure_elements": list(plot_structure.keys()),
            },
        )

    def _validate_plot_structure(
        self, structure_data: Dict[str, Any], novel_input: NovelInput
    ) -> Dict[str, Any]:
        """Validate plot structure.

        Args:
            structure_data: Raw structure data from LLM
            novel_input: Novel input for validation

        Returns:
            Validated plot structure
        """
        # Ensure required sections
        required_sections = [
            "overall_structure",
            "scene_sequence",
            "pacing",
            "point_of_view",
        ]

        validated_structure = {
            "design_id": f"plot_{int(time.time())}",
            "genre": novel_input.genre,
            "chapter_outline": novel_input.chapter_outline,
        }

        for section in required_sections:
            if section in structure_data:
                validated_structure[section] = structure_data[section]
            else:
                # Provide default values
                if section == "overall_structure":
                    validated_structure[section] = "引入→发展→冲突→高潮→回落"
                elif section == "scene_sequence":
                    validated_structure[section] = ["场景1", "场景2", "场景3"]
                elif section == "pacing":
                    validated_structure[section] = "中等"
                elif section == "point_of_view":
                    validated_structure[section] = "第三人称"

        # Add character involvement
        if "character_involvement" not in structure_data:
            character_names = [char.name for char in novel_input.characters]
            validated_structure["character_involvement"] = {
                char: f"在情节中扮演重要角色" for char in character_names
            }
        else:
            validated_structure["character_involvement"] = structure_data[
                "character_involvement"
            ]

        # Add estimated length
        validated_structure["estimated_length"] = structure_data.get(
            "estimated_length", novel_input.target_length or 2000
        )

        return validated_structure

    def _design_plot_points(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design key plot points.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with plot points
        """
        task_description = f"""为以下小说章节设计关键情节点：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
人物列表：{', '.join([char.name for char in novel_input.characters])}

设计要求：
1. 设计5-8个关键情节点（引入、发展、冲突、转折、高潮、悬念等）
2. 每个情节点包含：类型、描述、重要性、涉及人物、张力等级
3. 确保情节点之间逻辑连贯，推进合理
4. 设置适当的悬念和伏笔
5. 考虑情感起伏和节奏变化

请以JSON格式返回情节点设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2000)

        # Convert to PlotPoint models
        plot_points = self._create_plot_points(response, novel_input)

        return AgentResult(
            content=json.dumps(
                [point.dict() for point in plot_points], ensure_ascii=False, indent=2
            ),
            metadata={
                "design_type": "plot_points",
                "point_count": len(plot_points),
                "point_types": list(set(point.point_type for point in plot_points)),
                "avg_tension": sum(point.tension_level for point in plot_points)
                / len(plot_points)
                if plot_points
                else 0,
            },
        )

    def _create_plot_points(
        self, points_data: List[Dict[str, Any]], novel_input: NovelInput
    ) -> List[PlotPoint]:
        """Create PlotPoint objects from raw data.

        Args:
            points_data: Raw plot points data
            novel_input: Novel input for validation

        Returns:
            List of PlotPoint objects
        """
        plot_points = []

        for i, point_data in enumerate(points_data):
            try:
                # Ensure required fields
                point_data.setdefault("point_type", f"情节点{i+1}")
                point_data.setdefault("description", "待完善")
                point_data.setdefault("significance", "推进情节发展")
                point_data.setdefault("characters_involved", [])
                point_data.setdefault("tension_level", 5)
                point_data.setdefault("is_foreshadowing", False)

                # Validate tension level
                tension = point_data["tension_level"]
                if not isinstance(tension, (int, float)):
                    point_data["tension_level"] = 5
                elif tension < 1:
                    point_data["tension_level"] = 1
                elif tension > 10:
                    point_data["tension_level"] = 10

                plot_point = PlotPoint(**point_data)
                plot_points.append(plot_point)

            except Exception as e:
                self.logger.warning(f"Failed to create plot point {i+1}: {str(e)}")
                # Create a default plot point
                default_point = PlotPoint(
                    point_type=f"情节点{i+1}",
                    description="待完善的情节点",
                    significance="推进情节发展",
                    characters_involved=[],
                    tension_level=5,
                    is_foreshadowing=False,
                )
                plot_points.append(default_point)

        return plot_points

    def _design_emotional_curve(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design emotional curve.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with emotional curve design
        """
        # Use provided emotional curve or design new one
        if novel_input.emotional_curve:
            emotional_curve = novel_input.emotional_curve
            task_type = "provided"
        else:
            emotional_curve = ["平静", "紧张", "高潮", "回落"]
            task_type = "default"

        task_description = f"""为以下小说章节设计情感曲线：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
基础情感曲线：{', '.join(emotional_curve)}

设计要求：
1. 将情感曲线映射到具体情节段落
2. 为每个情感阶段设计具体的情感内容和强度（1-10分）
3. 考虑情感转换的合理性和流畅性
4. 确保情感变化与情节发展相匹配
5. 设计情感高潮的位置和强度

请以JSON格式返回情感曲线设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=1500)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "emotional_curve",
                "curve_type": task_type,
                "base_curve": emotional_curve,
                "curve_segments": len(response.get("segments", [])),
            },
        )

    def _design_conflicts(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design conflicts for the chapter.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with conflict design
        """
        task_description = f"""为以下小说章节设计冲突：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
人物列表：{', '.join([char.name for char in novel_input.characters])}

冲突类型考虑：
1. 人物内心的冲突（情感、道德、选择）
2. 人物之间的冲突（利益、观念、情感）
3. 人物与环境的冲突（自然、社会、命运）
4. 人物与超自然力量的冲突（玄幻/科幻特有）

设计要求：
1. 设计2-4个主要冲突
2. 每个冲突包含：类型、双方、原因、发展、解决/悬置
3. 冲突要有层次感，从轻微到激烈
4. 冲突要服务于人物发展和情节推进
5. 考虑冲突的解决时机和方式

请以JSON格式返回冲突设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=1500)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "conflicts",
                "conflict_count": len(response.get("conflicts", [])),
                "conflict_types": list(
                    set(conflict.get("type", "未知") for conflict in response.get("conflicts", []))
                ),
            },
        )

    def _design_complete_plot(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design complete plot including all elements.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with complete plot design
        """
        task_description = f"""为以下小说章节设计完整的情节方案：

小说类型：{novel_input.genre}
整体大纲：{novel_input.overall_outline}
本章提纲：{novel_input.chapter_outline}
人物列表：{', '.join([char.name for char in novel_input.characters])}
场景列表：{', '.join([scene.name for scene in novel_input.scenes])}
道具列表：{', '.join([prop.name for prop in novel_input.props])}

设计要求（包含以下所有部分）：
1. 情节结构：完整的叙事结构
2. 情节点：5-8个关键情节点
3. 情感曲线：情感起伏设计
4. 冲突设计：主要冲突安排
5. 悬念设置：悬念和伏笔
6. 节奏控制：叙事节奏安排
7. 章节标题：建议的章节标题

请以JSON格式返回完整的情节设计方案。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2500)

        # Create ChapterDraft from response
        chapter_draft = self._create_chapter_draft(response, novel_input)

        return AgentResult(
            content=json.dumps(chapter_draft.dict(), ensure_ascii=False, indent=2),
            metadata={
                "design_type": "complete_plot",
                "draft_elements": [
                    "plot_structure",
                    "plot_points",
                    "conflicts",
                    "emotional_curve",
                ],
                "estimated_length": chapter_draft.estimated_length,
                "chapter_title": chapter_draft.chapter_title,
            },
        )

    def _create_chapter_draft(
        self, plot_data: Dict[str, Any], novel_input: NovelInput
    ) -> ChapterDraft:
        """Create ChapterDraft from plot design data.

        Args:
            plot_data: Plot design data
            novel_input: Novel input for context

        Returns:
            ChapterDraft object
        """
        # Extract data with defaults
        plot_structure = plot_data.get("plot_structure", "引入→发展→高潮→结尾")
        plot_points_data = plot_data.get("plot_points", [])
        conflicts = plot_data.get("conflicts", [])
        emotional_curve = plot_data.get("emotional_curve", [])
        pacing = plot_data.get("pacing", "中等")
        point_of_view = plot_data.get("point_of_view", "第三人称")
        chapter_title = plot_data.get("chapter_title", "未命名章节")
        estimated_length = plot_data.get("estimated_length", novel_input.target_length or 2000)

        # Create plot points
        plot_points = self._create_plot_points(plot_points_data, novel_input)

        # Create conflicts list
        conflict_descriptions = []
        for conflict in conflicts:
            if isinstance(conflict, dict):
                desc = conflict.get("description", "冲突")
                conflict_descriptions.append(desc)
            else:
                conflict_descriptions.append(str(conflict))

        # Create chapter draft
        chapter_draft = ChapterDraft(
            plot_structure=plot_structure,
            plot_points=plot_points,
            emotional_curve=emotional_curve,
            conflicts=conflict_descriptions,
            cliffhangers=plot_data.get("cliffhangers", []),
            character_arcs=plot_data.get("character_arcs", {}),
            character_interactions=plot_data.get("character_interactions", []),
            dialogue=[],
            scene_segments=[],
            scene_transitions=plot_data.get("scene_transitions", []),
            props_used=plot_data.get("props_used", []),
            symbolic_elements=plot_data.get("symbolic_elements", []),
            writing_style=plot_data.get("writing_style", {}),
            pacing=pacing,
            point_of_view=point_of_view,
            estimated_length=estimated_length,
            chapter_title=chapter_title,
        )

        return chapter_draft