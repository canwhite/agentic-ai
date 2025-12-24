"""
Character Agent - Designs character interactions, dialogue, and development.
"""

import json
import time
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent, AgentResult
from src.models import NovelInput, ChapterDraft, DialogueLine, Character as CharacterModel


class CharacterAgent(BaseAgent):
    """Character agent that designs character interactions and dialogue."""

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """Initialize character agent.

        Args:
            llm_provider: LLM provider
            temperature: Sampling temperature
        """
        system_prompt = """你是小说人物设计师，专门负责设计人物表现、对话和情感发展。

你的职责：
1. 根据人物设定设计具体的对话和行为
2. 确保人物性格一致性，防止OOC（Out of Character）
3. 设计人物情感变化和成长弧线
4. 处理人物关系和互动
5. 创造生动、真实的人物表现

设计原则：
1. 人物对话要符合性格、背景和当前情境
2. 人物行为要有合理的动机和逻辑
3. 情感变化要自然流畅，有层次感
4. 人物关系要真实可信，有发展变化
5. 防止人物崩坏，保持设定一致性

请以专业、细腻的态度设计人物表现。"""

        super().__init__(
            name="人物设计师",
            role="小说人物设计师",
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            temperature=temperature,
        )

    def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Execute character design task.

        Args:
            task: Task description
            context: Context information

        Returns:
            AgentResult with character design
        """
        start_time = time.time()

        try:
            # Parse novel input from context
            novel_input = self._parse_novel_input(context)

            # Determine task type
            if "对话设计" in task or "dialogue" in task.lower():
                result = self._design_dialogue(novel_input, context)
            elif "人物行为" in task or "behavior" in task.lower():
                result = self._design_character_behavior(novel_input, context)
            elif "情感发展" in task or "emotional" in task.lower():
                result = self._design_emotional_development(novel_input, context)
            elif "人物关系" in task or "relationship" in task.lower():
                result = self._design_relationships(novel_input, context)
            elif "防OOC" in task or "consistency" in task.lower():
                result = self._check_character_consistency(novel_input, context)
            else:
                # Default: design complete character performance
                result = self._design_complete_character_performance(novel_input, context)

            execution_time = time.time() - start_time
            self._record_execution(task, context, result, execution_time)

            return result

        except Exception as e:
            self.logger.error(f"Character agent execution failed: {str(e)}")
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

    def _design_dialogue(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design character dialogue.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with dialogue design
        """
        # Get plot structure from context if available
        plot_structure = context.get("plot_structure", "引入→发展→高潮→结尾")
        scene_info = context.get("scene_info", "未知场景")

        task_description = f"""为以下小说章节设计人物对话：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
情节结构：{plot_structure}
场景信息：{scene_info}

人物设定：
{self._format_characters_for_prompt(novel_input.characters)}

设计要求：
1. 设计5-10段关键对话
2. 每段对话包含：说话人物、对话内容、情感/语气、伴随动作
3. 对话要符合人物性格、背景和当前情境
4. 对话要推进情节发展或揭示人物性格
5. 注意对话节奏和自然度
6. 防止OOC（人物行为不符合设定）

请以JSON格式返回对话设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2000)

        # Convert to DialogueLine models
        dialogue_lines = self._create_dialogue_lines(response, novel_input)

        return AgentResult(
            content=json.dumps(
                [line.model_dump() for line in dialogue_lines], ensure_ascii=False, indent=2
            ),
            metadata={
                "design_type": "dialogue",
                "dialogue_count": len(dialogue_lines),
                "characters_involved": list(set(line.character for line in dialogue_lines)),
                "avg_dialogue_length": sum(len(line.content) for line in dialogue_lines) / len(dialogue_lines) if dialogue_lines else 0,
            },
        )

    def _format_characters_for_prompt(self, characters: List[CharacterModel]) -> str:
        """Format characters for prompt.

        Args:
            characters: List of Character objects

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
            if char.speech_style:
                char_info += f"\n  说话风格：{char.speech_style}"
            formatted.append(char_info)

        return "\n\n".join(formatted)

    def _create_dialogue_lines(
        self, dialogue_data: List[Dict[str, Any]], novel_input: NovelInput
    ) -> List[DialogueLine]:
        """Create DialogueLine objects from raw data.

        Args:
            dialogue_data: Raw dialogue data
            novel_input: Novel input for validation

        Returns:
            List of DialogueLine objects
        """
        dialogue_lines = []

        for i, line_data in enumerate(dialogue_data):
            try:
                # Ensure required fields
                line_data.setdefault("character", f"人物{i+1}")
                line_data.setdefault("content", "待完善的对话")
                line_data.setdefault("emotion", None)
                line_data.setdefault("action", None)

                # Validate character exists
                character_name = line_data["character"]
                character = novel_input.get_character_by_name(character_name)
                if not character:
                    self.logger.warning(f"Character {character_name} not found in novel input")

                dialogue_line = DialogueLine(**line_data)
                dialogue_lines.append(dialogue_line)

            except Exception as e:
                self.logger.warning(f"Failed to create dialogue line {i+1}: {str(e)}")
                # Create a default dialogue line
                default_line = DialogueLine(
                    character="未知人物",
                    content="待完善的对话",
                    emotion=None,
                    action=None,
                )
                dialogue_lines.append(default_line)

        return dialogue_lines

    def _design_character_behavior(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design character behavior and actions.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with behavior design
        """
        plot_points = context.get("plot_points", [])
        scene_info = context.get("scene_info", "未知场景")

        task_description = f"""为以下小说章节设计人物行为：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
场景信息：{scene_info}

人物设定：
{self._format_characters_for_prompt(novel_input.characters)}

情节点：
{json.dumps(plot_points[:5], ensure_ascii=False, indent=2) if plot_points else '无具体情节点'}

设计要求：
1. 为每个人物设计在本章中的关键行为
2. 每个行为包含：行为描述、动机、结果、情感状态
3. 行为要符合人物性格和当前情境
4. 行为要推动情节发展或揭示人物性格
5. 注意行为的合理性和连贯性
6. 防止人物行为崩坏（防崩人设）

请以JSON格式返回人物行为设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "character_behavior",
                "character_count": len(response.get("behaviors", {})),
                "total_behaviors": sum(len(behaviors) for behaviors in response.get("behaviors", {}).values()),
            },
        )

    def _design_emotional_development(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design character emotional development.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with emotional development design
        """
        plot_structure = context.get("plot_structure", "引入→发展→高潮→结尾")
        emotional_curve = context.get("emotional_curve", ["平静", "紧张", "高潮", "回落"])

        task_description = f"""为以下小说章节设计人物情感发展：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
情节结构：{plot_structure}
情感曲线：{', '.join(emotional_curve)}

人物设定：
{self._format_characters_for_prompt(novel_input.characters)}

设计要求：
1. 为每个人物设计情感发展弧线
2. 情感发展要对应情节结构和情感曲线
3. 描述每个情感阶段：情感状态、原因、表现、变化
4. 情感变化要自然合理，有层次感
5. 情感发展要服务于人物塑造和情节推进
6. 注意情感的真实性和感染力

请以JSON格式返回情感发展设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "emotional_development",
                "character_count": len(response.get("emotional_arcs", {})),
                "emotional_stages": len(emotional_curve),
            },
        )

    def _design_relationships(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design character relationships and interactions.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with relationship design
        """
        # Extract existing relationships from characters
        existing_relationships = {}
        for char in novel_input.characters:
            if char.relationships:
                existing_relationships[char.name] = char.relationships

        task_description = f"""为以下小说章节设计人物关系发展：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}

人物设定：
{self._format_characters_for_prompt(novel_input.characters)}

现有关系：
{json.dumps(existing_relationships, ensure_ascii=False, indent=2) if existing_relationships else '无预设关系'}

设计要求：
1. 设计人物之间的互动和关系变化
2. 重点设计2-3对关键人物关系
3. 每对关系包含：关系类型、当前状态、互动内容、变化发展
4. 关系发展要自然合理，有戏剧性
5. 关系要服务于情节发展和人物塑造
6. 注意关系的真实性和复杂性

请以JSON格式返回人物关系设计。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "relationships",
                "key_relationships": len(response.get("key_relationships", [])),
                "relationship_types": list(set(rel.get("type", "未知") for rel in response.get("key_relationships", []))),
            },
        )

    def _check_character_consistency(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Check character consistency and prevent OOC.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with consistency check results
        """
        # Get character performance data from context
        character_performance = context.get("character_performance", {})
        plot_points = context.get("plot_points", [])

        task_description = f"""检查以下小说章节中的人物一致性：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}

人物设定：
{self._format_characters_for_prompt(novel_input.characters)}

人物表现：
{json.dumps(character_performance, ensure_ascii=False, indent=2) if character_performance else '无具体表现数据'}

情节点：
{json.dumps(plot_points[:5], ensure_ascii=False, indent=2) if plot_points else '无具体情节点'}

检查要点（"三板斧"防崩机制）：
1. 防OOC：人物行为是否符合设定？
2. 防崩人设：人物性格是否崩坏？
3. 防水：人物表现是否空洞无物？

请对每个人物进行检查，指出问题，提出改进建议。
请以JSON格式返回一致性检查结果。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=1500)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "consistency_check",
                "characters_checked": len(response.get("checks", {})),
                "issues_found": sum(len(check.get("issues", [])) for check in response.get("checks", {}).values()),
                "suggestions_count": sum(len(check.get("suggestions", [])) for check in response.get("checks", {}).values()),
            },
        )

    def _design_complete_character_performance(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Design complete character performance including all elements.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with complete character performance design
        """
        # Get plot information from context
        plot_structure = context.get("plot_structure", "引入→发展→高潮→结尾")
        plot_points = context.get("plot_points", [])
        emotional_curve = context.get("emotional_curve", ["平静", "紧张", "高潮", "回落"])
        scene_info = context.get("scene_info", "未知场景")

        task_description = f"""为以下小说章节设计完整的人物表现：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}
情节结构：{plot_structure}
情感曲线：{', '.join(emotional_curve)}
场景信息：{scene_info}

人物设定：
{self._format_characters_for_prompt(novel_input.characters)}

情节点：
{json.dumps(plot_points[:5], ensure_ascii=False, indent=2) if plot_points else '无具体情节点'}

设计要求（包含以下所有部分）：
1. 对话设计：关键对话片段
2. 行为设计：人物关键行为
3. 情感发展：情感变化弧线
4. 关系互动：人物关系发展
5. 一致性检查：防OOC、防崩人设检查
6. 表现总结：本章人物表现要点

请以JSON格式返回完整的人物表现设计方案。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=3000)

        # Add dialogue lines to ChapterDraft if provided in context
        chapter_draft = context.get("chapter_draft")
        if chapter_draft and isinstance(chapter_draft, ChapterDraft) and "dialogue" in response:
            dialogue_lines = self._create_dialogue_lines(response["dialogue"], novel_input)
            # Note: We can't modify chapter_draft here as it's from context
            # This would need to be handled by the workflow

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "design_type": "complete_character_performance",
                "design_elements": list(response.keys()),
                "character_count": len(novel_input.characters),
                "contains_dialogue": "dialogue" in response,
                "contains_behavior": "behavior" in response,
                "contains_emotional": "emotional_development" in response,
            },
        )

    def get_character_by_name(
        self, novel_input: NovelInput, name: str
    ) -> Optional[CharacterModel]:
        """Get character by name.

        Args:
            novel_input: Novel input data
            name: Character name

        Returns:
            Character object if found, None otherwise
        """
        return novel_input.get_character_by_name(name)

    def validate_character_consistency(
        self, character: CharacterModel, behavior: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate character behavior consistency.

        Args:
            character: Character object
            behavior: Behavior to validate
            context: Context information

        Returns:
            Validation results
        """
        validation_result = {
            "character": character.name,
            "behavior": behavior.get("description", "未知行为"),
            "is_consistent": True,
            "issues": [],
            "suggestions": [],
        }

        # Check personality consistency
        behavior_description = behavior.get("description", "").lower()
        character_personality = character.personality.lower()

        # Simple keyword checking (could be enhanced)
        conflicting_keywords = {
            "勇敢": ["胆小", "懦弱", "退缩"],
            "聪明": ["愚蠢", "笨拙", "糊涂"],
            "善良": ["邪恶", "残忍", "恶毒"],
            "冷静": ["冲动", "暴躁", "急躁"],
        }

        for trait, conflicts in conflicting_keywords.items():
            if trait in character_personality:
                for conflict in conflicts:
                    if conflict in behavior_description:
                        validation_result["is_consistent"] = False
                        validation_result["issues"].append(
                            f"行为'{conflict}'与性格特质'{trait}'冲突"
                        )
                        validation_result["suggestions"].append(
                            f"调整行为使其更符合'{trait}'的特质"
                        )

        # Check background consistency
        if character.background and "背景" in context.get("scene_info", ""):
            # Simple check: if behavior seems inappropriate for background
            # This could be enhanced with more sophisticated checks
            pass

        return validation_result