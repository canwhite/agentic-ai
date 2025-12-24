"""
Scene Renderer Agent - Designs scene descriptions, atmosphere, and sensory details.
"""

import json
import time
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent, AgentResult
from src.models import NovelInput, ChapterDraft, Scene as SceneModel


class SceneRendererAgent(BaseAgent):
    """Scene renderer agent that designs scene descriptions and atmosphere."""

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """Initialize scene renderer agent.

        Args:
            llm_provider: LLM provider
            temperature: Sampling temperature
        """
        system_prompt = """你是小说场景渲染师，专门负责设计场景描述、氛围营造和感官细节。

你的职责：
1. 根据场景设定设计生动的场景描述
2. 营造合适的氛围和情绪
3. 添加丰富的感官细节（视觉、听觉、嗅觉、触觉、味觉）
4. 设计场景转换和空间布局
5. 确保场景服务于情节发展和人物塑造

设计原则：
1. 场景描述要具体、生动、有画面感
2. 氛围营造要符合情节情绪和人物心境
3. 感官细节要丰富多样，增强沉浸感
4. 空间布局要合理清晰，便于读者想象
5. 场景转换要自然流畅，有逻辑性
6. 场景要服务于情节推进和人物表现

请以专业、细腻的态度设计场景渲染方案。"""

        super().__init__(
            name="场景渲染师",
            role="小说场景渲染师",
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            temperature=temperature,
        )

    def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Execute scene rendering task.

        Args:
            task: Task description
            context: Context information

        Returns:
            AgentResult with scene rendering design
        """
        start_time = time.time()

        try:
            # Parse novel input from context
            novel_input = self._parse_novel_input(context)

            # Determine task type
            if "场景描述" in task or "description" in task.lower():
                result = self._design_scene_descriptions(novel_input, context)
            elif "氛围营造" in task or "atmosphere" in task.lower():
                result = self._design_atmosphere(novel_input, context)
            elif "感官细节" in task or "sensory" in task.lower():
                result = self._design_sensory_details(novel_input, context)
            elif "空间布局" in task or "layout" in task.lower():
                result = self._design_spatial_layout(novel_input, context)
            elif "场景转换" in task or "transition" in task.lower():
                result = self._design_scene_transitions(novel_input, context)
            else:
                # Default: design complete scene rendering
                result = self._design_complete_scene_rendering(novel_input, context)

            execution_time = time.time() - start_time
            self._record_execution(task, context, result, execution_time)

            return result

        except Exception as e:
            self.logger.error(f"Scene renderer agent execution failed: {str(e)}")
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

    def _design_scene_descriptions(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design detailed scene descriptions.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with scene descriptions
        """
        # Get plot information from context
        plot_structure = context.get("plot_structure", "引入→发展→高潮→结尾")
        emotional_curve = context.get("emotional_curve", ["平静", "紧张", "高潮", "回落"])
        character_info = context.get("character_info", "未知人物")

        task_description = f"""为以下小说章节设计场景描述：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
情节结构：{plot_structure}
情感曲线：{', '.join(emotional_curve)}
人物信息：{character_info}

场景设定：
{self._format_scenes_for_prompt(novel_input.scenes)}

设计要求：
1. 为每个场景设计详细的描述（200-300字）
2. 描述要具体、生动、有画面感
3. 突出场景的关键特征和独特之处
4. 描述要服务于情节发展和人物表现
5. 注意场景之间的连贯性和逻辑性
6. 符合{novel_input.genre}类型的场景特点

请以JSON格式返回场景描述设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2500)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "scene_descriptions",
                "scene_count": len(response.get("scenes", {})),
                "total_description_length": sum(len(desc) for desc in response.get("scenes", {}).values()),
                "avg_description_length": sum(len(desc) for desc in response.get("scenes", {}).values()) / len(response.get("scenes", {})) if response.get("scenes") else 0,
            },
        )

    def _format_scenes_for_prompt(self, scenes: List[SceneModel]) -> str:
        """Format scenes for prompt.

        Args:
            scenes: List of Scene objects

        Returns:
            Formatted string
        """
        if not scenes:
            return "无具体场景设定"

        formatted = []
        for scene in scenes:
            scene_info = f"- {scene.name}"
            scene_info += f"\n  地点：{scene.location}"
            scene_info += f"\n  时间：{scene.time}"
            if scene.atmosphere:
                scene_info += f"\n  氛围：{scene.atmosphere}"
            if scene.key_elements:
                scene_info += f"\n  关键元素：{scene.key_elements}"
            formatted.append(scene_info)

        return "\n\n".join(formatted)

    def _design_atmosphere(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design scene atmosphere and mood.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with atmosphere design
        """
        plot_points = context.get("plot_points", [])
        emotional_curve = context.get("emotional_curve", ["平静", "紧张", "高潮", "回落"])

        task_description = f"""为以下小说章节设计场景氛围：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
情感曲线：{', '.join(emotional_curve)}

场景设定：
{self._format_scenes_for_prompt(novel_input.scenes)}

情节点：
{json.dumps(plot_points[:5], ensure_ascii=False, indent=2) if plot_points else '无具体情节点'}

设计要求：
1. 为每个场景设计合适的氛围和情绪
2. 氛围要对应情感曲线和情节发展
3. 描述氛围的关键元素：光线、色彩、声音、温度、气味等
4. 氛围要服务于情节情绪和人物心境
5. 注意氛围的变化和过渡
6. 营造沉浸感和情绪感染力

请以JSON格式返回氛围设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "atmosphere",
                "scene_count": len(response.get("atmospheres", {})),
                "atmosphere_elements": list(set(element for scene_atmos in response.get("atmospheres", {}).values() for element in scene_atmos.get("elements", []))),
            },
        )

    def _design_sensory_details(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design sensory details for scenes.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with sensory details design
        """
        character_info = context.get("character_info", "未知人物")
        plot_points = context.get("plot_points", [])

        task_description = f"""为以下小说章节设计感官细节：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
人物信息：{character_info}

场景设定：
{self._format_scenes_for_prompt(novel_input.scenes)}

情节点：
{json.dumps(plot_points[:5], ensure_ascii=False, indent=2) if plot_points else '无具体情节点'}

设计要求（包含五种感官）：
1. 视觉细节：色彩、形状、光线、动作、表情等
2. 听觉细节：声音、对话、环境音、音乐等
3. 嗅觉细节：气味、芳香、臭味等
4. 触觉细节：温度、质地、压力、疼痛等
5. 味觉细节：味道、口感等（如适用）

设计原则：
1. 感官细节要具体、生动、有特色
2. 细节要服务于场景氛围和人物体验
3. 注意细节的多样性和层次感
4. 避免过度描述，保持自然流畅
5. 增强场景的沉浸感和真实感

请以JSON格式返回感官细节设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2500)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "sensory_details",
                "scene_count": len(response.get("sensory_details", {})),
                "senses_covered": list(set(sense for scene_senses in response.get("sensory_details", {}).values() for sense in scene_senses.keys())),
                "total_details": sum(len(details) for scene_senses in response.get("sensory_details", {}).values() for details in scene_senses.values()),
            },
        )

    def _design_spatial_layout(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design spatial layout and scene composition.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with spatial layout design
        """
        character_positions = context.get("character_positions", {})
        plot_points = context.get("plot_points", [])

        task_description = f"""为以下小说章节设计空间布局：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}

场景设定：
{self._format_scenes_for_prompt(novel_input.scenes)}

人物位置：
{json.dumps(character_positions, ensure_ascii=False, indent=2) if character_positions else '无预设位置'}

情节点：
{json.dumps(plot_points[:5], ensure_ascii=False, indent=2) if plot_points else '无具体情节点'}

设计要求：
1. 为每个场景设计清晰的空间布局
2. 描述场景的空间结构：大小、形状、分区、出入口等
3. 设计人物在空间中的位置和移动路线
4. 布局要服务于情节发展和人物互动
5. 注意空间的合理性和逻辑性
6. 便于读者想象场景空间

请以JSON格式返回空间布局设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "spatial_layout",
                "scene_count": len(response.get("layouts", {})),
                "contains_movement_paths": any("movement_paths" in layout for layout in response.get("layouts", {}).values()),
                "contains_spatial_structure": any("spatial_structure" in layout for layout in response.get("layouts", {}).values()),
            },
        )

    def _design_scene_transitions(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design scene transitions and connections.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with scene transition design
        """
        plot_structure = context.get("plot_structure", "引入→发展→高潮→结尾")
        time_progression = context.get("time_progression", "线性时间")

        task_description = f"""为以下小说章节设计场景转换：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
情节结构：{plot_structure}
时间推进：{time_progression}

场景设定：
{self._format_scenes_for_prompt(novel_input.scenes)}

设计要求：
1. 设计场景之间的转换方式和连接点
2. 转换要自然流畅，有逻辑性
3. 设计转换的提示词：时间变化、地点变化、视角变化等
4. 转换要服务于情节节奏和阅读体验
5. 注意转换的多样性和创造性
6. 避免生硬的场景切换

请以JSON格式返回场景转换设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "scene_transitions",
                "transition_count": len(response.get("transitions", [])),
                "transition_types": list(set(trans.get("type", "未知") for trans in response.get("transitions", []))),
                "contains_time_transitions": any(trans.get("type") == "时间转换" for trans in response.get("transitions", [])),
                "contains_space_transitions": any(trans.get("type") == "空间转换" for trans in response.get("transitions", [])),
            },
        )

    def _design_complete_scene_rendering(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design complete scene rendering including all elements.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with complete scene rendering design
        """
        # Get all relevant context
        plot_structure = context.get("plot_structure", "引入→发展→高潮→结尾")
        plot_points = context.get("plot_points", [])
        emotional_curve = context.get("emotional_curve", ["平静", "紧张", "高潮", "回落"])
        character_info = context.get("character_info", "未知人物")
        time_progression = context.get("time_progression", "线性时间")

        task_description = f"""为以下小说章节设计完整的场景渲染方案：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
情节结构：{plot_structure}
情感曲线：{', '.join(emotional_curve)}
时间推进：{time_progression}
人物信息：{character_info}

场景设定：
{self._format_scenes_for_prompt(novel_input.scenes)}

情节点：
{json.dumps(plot_points[:5], ensure_ascii=False, indent=2) if plot_points else '无具体情节点'}

设计要求（包含以下所有部分）：
1. 场景描述：详细的场景描写
2. 氛围营造：场景氛围和情绪
3. 感官细节：五种感官的细节描写
4. 空间布局：场景空间结构和人物位置
5. 场景转换：场景之间的过渡和连接
6. 渲染总结：本章场景渲染要点

请以JSON格式返回完整的场景渲染设计方案。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=3500)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "complete_scene_rendering",
                "design_elements": list(response.keys()),
                "scene_count": len(novel_input.scenes),
                "contains_descriptions": "scene_descriptions" in response,
                "contains_atmosphere": "atmosphere" in response,
                "contains_sensory": "sensory_details" in response,
                "contains_layout": "spatial_layout" in response,
                "contains_transitions": "scene_transitions" in response,
            },
        )

    def get_scene_by_name(
        self, novel_input: NovelInput, name: str
    ) -> Optional[SceneModel]:
        """Get scene by name.

        Args:
            novel_input: Novel input data
            name: Scene name

        Returns:
            Scene object if found, None otherwise
        """
        for scene in novel_input.scenes:
            if scene.name == name:
                return scene
        return None

    def validate_scene_coherence(
        self, scene: SceneModel, rendering: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate scene rendering coherence.

        Args:
            scene: Scene object
            rendering: Scene rendering to validate
            context: Context information

        Returns:
            Validation results
        """
        validation_result = {
            "scene": scene.name,
            "rendering_type": rendering.get("type", "未知"),
            "is_coherent": True,
            "issues": [],
            "suggestions": [],
        }

        # Check if rendering matches scene setting
        scene_location = scene.location.lower()
        rendering_description = rendering.get("description", "").lower()

        # Simple coherence checks
        if scene.time and "时间" in context:
            # Check if time description is consistent
            pass

        if scene.atmosphere:
            rendering_atmosphere = rendering.get("atmosphere", {}).get("mood", "")
            if scene.atmosphere.lower() not in rendering_atmosphere.lower():
                validation_result["issues"].append(
                    f"氛围渲染'{rendering_atmosphere}'与场景设定氛围'{scene.atmosphere}'不完全匹配"
                )
                validation_result["suggestions"].append(
                    f"调整氛围渲染以更好地体现'{scene.atmosphere}'"
                )

        # Check sensory details completeness
        sensory_details = rendering.get("sensory_details", {})
        expected_senses = ["视觉", "听觉", "嗅觉", "触觉"]
        missing_senses = [sense for sense in expected_senses if sense not in sensory_details]

        if missing_senses:
            validation_result["issues"].append(f"缺少感官细节：{', '.join(missing_senses)}")
            validation_result["suggestions"].append(f"补充{', '.join(missing_senses)}细节以增强沉浸感")

        return validation_result