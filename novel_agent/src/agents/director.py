"""
Director Agent - Coordinates all other agents for novel chapter generation.
"""

import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from src.agents.base_agent import BaseAgent, AgentResult
from src.models import NovelInput, ChapterDraft


@dataclass
class TaskAssignment:
    """Task assignment for subordinate agents."""

    agent_type: str  # plot_designer, character, scene_renderer, etc.
    task_description: str
    priority: int = 1  # 1=highest, 3=lowest
    dependencies: List[str] = None  # List of agent types this task depends on
    expected_output_format: str = "json"  # json or text

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class DirectorAgent(BaseAgent):
    """Director agent that coordinates all other agents."""

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """Initialize director agent.

        Args:
            llm_provider: LLM provider
            temperature: Sampling temperature
        """
        system_prompt = """你是小说创作团队的总导演，负责协调所有专业Agent的工作。

你的职责：
1. 分析小说创作需求，制定详细的创作计划
2. 将任务分配给最合适的专业Agent
3. 协调各Agent的输出，确保整体一致性
4. 监督创作质量，实施"三板斧"防崩机制
5. 最终合成高质量的小说章节

"三板斧"防崩机制：
1. 防"水"：确保每段文字都有推进剧情或塑造人物的作用
2. 防崩人设：确保人物行为符合设定，性格一致
3. 防OOC：防止人物行为不符合设定（Out of Character）

请以严谨、专业的态度执行导演工作。"""

        super().__init__(
            name="导演",
            role="小说创作总导演",
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            temperature=temperature,
        )

        # Available agent types
        self.available_agents = [
            "plot_designer",  # 情节设计
            "character",  # 人物塑造
            "scene_renderer",  # 场景渲染
            "writing_optimizer",  # 文笔优化
            "consistency_checker",  # 连贯性检查
        ]

    def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Execute director task.

        Args:
            task: Task description
            context: Context information (should include NovelInput)

        Returns:
            AgentResult with execution plan or coordination results
        """
        start_time = time.time()

        try:
            # Parse novel input from context
            novel_input = self._parse_novel_input(context)

            # Determine task type
            if "制定创作计划" in task or "plan" in task.lower():
                result = self._create_creation_plan(novel_input, context)
            elif "协调" in task or "coordinate" in task.lower():
                result = self._coordinate_agents(task, context)
            elif "合成" in task or "synthesize" in task.lower():
                result = self._synthesize_chapter(task, context)
            elif "质量检查" in task or "quality" in task.lower():
                result = self._perform_quality_check(task, context)
            else:
                # Default: create creation plan
                result = self._create_creation_plan(novel_input, context)

            execution_time = time.time() - start_time
            self._record_execution(task, context, result, execution_time)

            return result

        except Exception as e:
            self.logger.error(f"Director agent execution failed: {str(e)}")
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

    def _create_creation_plan(
        self, novel_input: NovelInput, context: Dict[str, Any]
    ) -> AgentResult:
        """Create detailed creation plan.

        Args:
            novel_input: Novel input data
            context: Additional context

        Returns:
            AgentResult with creation plan
        """
        task_description = f"""为以下小说创作需求制定详细的创作计划：

小说类型：{novel_input.genre}
整体大纲：{novel_input.overall_outline}
本章提纲：{novel_input.chapter_outline}
人物数量：{len(novel_input.characters)}
场景数量：{len(novel_input.scenes)}

请制定包含以下内容的创作计划：
1. 创作阶段划分（输入解析、并行创作、合成优化等）
2. 各阶段的具体任务
3. 任务分配给哪些专业Agent
4. 任务优先级和依赖关系
5. 质量检查点
6. "三板斧"防崩机制的具体实施措施

请以JSON格式返回创作计划。"""

        messages = self._prepare_messages(task_description, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=1500)

        # Validate and format response
        creation_plan = self._validate_creation_plan(response)

        return AgentResult(
            content=json.dumps(creation_plan, ensure_ascii=False, indent=2),
            metadata={
                "plan_type": "creation_plan",
                "novel_genre": novel_input.genre,
                "character_count": len(novel_input.characters),
                "scene_count": len(novel_input.scenes),
                "plan_details": creation_plan,
            },
        )

    def _validate_creation_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate creation plan structure.

        Args:
            plan_data: Raw plan data from LLM

        Returns:
            Validated and formatted plan
        """
        # Ensure required fields
        required_sections = [
            "创作阶段",
            "任务分配",
            "质量检查",
            "防崩机制",
        ]

        validated_plan = {
            "plan_id": f"plan_{int(time.time())}",
            "creation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        for section in required_sections:
            if section in plan_data:
                validated_plan[section] = plan_data[section]
            else:
                validated_plan[section] = f"待完善：{section}"

        # Add default task assignments if not present
        if "任务分配" not in validated_plan or not validated_plan["任务分配"]:
            validated_plan["任务分配"] = self._create_default_task_assignments()

        return validated_plan

    def _create_default_task_assignments(self) -> List[Dict[str, Any]]:
        """Create default task assignments.

        Returns:
            List of task assignments
        """
        return [
            {
                "agent": "plot_designer",
                "task": "设计章节情节结构，包括冲突、悬念、情感曲线",
                "priority": 1,
                "dependencies": [],
                "output_format": "json",
            },
            {
                "agent": "character",
                "task": "设计人物对话、行为和情感变化，确保人物一致性",
                "priority": 1,
                "dependencies": ["plot_designer"],
                "output_format": "json",
            },
            {
                "agent": "scene_renderer",
                "task": "设计场景描述、氛围营造和感官细节",
                "priority": 2,
                "dependencies": ["plot_designer"],
                "output_format": "json",
            },
            {
                "agent": "writing_optimizer",
                "task": "优化文笔、语言表达和文学性",
                "priority": 3,
                "dependencies": ["plot_designer", "character", "scene_renderer"],
                "output_format": "text",
            },
            {
                "agent": "consistency_checker",
                "task": "检查情节逻辑、人物一致性和整体连贯性",
                "priority": 3,
                "dependencies": ["writing_optimizer"],
                "output_format": "json",
            },
        ]

    def _coordinate_agents(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Coordinate multiple agents.

        Args:
            task: Coordination task description
            context: Context with agent outputs

        Returns:
            AgentResult with coordination results
        """
        # Extract agent outputs from context
        agent_outputs = context.get("agent_outputs", {})
        creation_plan = context.get("creation_plan", {})

        coordination_task = f"""协调以下专业Agent的输出：

任务：{task}

可用Agent输出：
{json.dumps(agent_outputs, ensure_ascii=False, indent=2)}

创作计划：
{json.dumps(creation_plan, ensure_ascii=False, indent=2)}

请执行以下协调工作：
1. 检查各Agent输出是否符合创作计划要求
2. 识别输出之间的不一致性
3. 提出解决不一致性的方案
4. 确定下一步行动建议

请以JSON格式返回协调结果。"""

        messages = self._prepare_messages(coordination_task, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=2000)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "coordination_type": "agent_coordination",
                "agents_involved": list(agent_outputs.keys()),
                "coordination_result": response,
            },
        )

    def _synthesize_chapter(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Synthesize final chapter from agent outputs.

        Args:
            task: Synthesis task description
            context: Context with agent outputs and intermediate results

        Returns:
            AgentResult with synthesized chapter
        """
        # Extract data from context
        agent_outputs = context.get("agent_outputs", {})
        intermediate_results = context.get("intermediate_results", {})
        novel_input = self._parse_novel_input(context)

        synthesis_task = f"""根据以下材料合成最终小说章节：

小说信息：
- 类型：{novel_input.genre}
- 本章提纲：{novel_input.chapter_outline}

专业Agent输出：
{json.dumps(agent_outputs, ensure_ascii=False, indent=2)}

中间结果：
{json.dumps(intermediate_results, ensure_ascii=False, indent=2)}

合成要求：
1. 整合所有材料，形成连贯的章节
2. 确保情节逻辑合理，人物行为一致
3. 保持文笔优美，符合{novel_input.genre}风格
4. 实施"三板斧"防崩机制
5. 章节长度约{novel_input.target_length or 2000}字

请直接输出完整的小说章节内容，不需要额外说明。"""

        messages = self._prepare_messages(synthesis_task, context)
        chapter_content = self._call_llm(messages, expect_json=False, max_tokens=4000)

        return AgentResult(
            content=chapter_content,
            metadata={
                "synthesis_type": "chapter_synthesis",
                "source_agents": list(agent_outputs.keys()),
                "estimated_length": len(chapter_content),
                "genre": novel_input.genre,
            },
        )

    def _perform_quality_check(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Perform quality check on chapter.

        Args:
            task: Quality check task description
            context: Context with chapter content

        Returns:
            AgentResult with quality assessment
        """
        chapter_content = context.get("chapter_content", "")
        novel_input = self._parse_novel_input(context)

        quality_task = f"""对以下小说章节进行质量检查：

小说类型：{novel_input.genre}
本章提纲：{novel_input.chapter_outline}

章节内容：
{chapter_content[:5000]}  # Limit content length

检查维度：
1. 情节连贯性：情节发展是否合理，逻辑是否通顺
2. 人物一致性：人物行为是否符合设定，有无OOC
3. 文笔质量：语言表达是否优美，描写是否生动
4. 剧情张力：是否有足够的冲突、悬念和情感起伏
5. "三板斧"检查：
   - 防"水"：有无无意义的内容填充
   - 防崩人设：人物性格是否崩坏
   - 防OOC：人物行为是否不符合设定

请对每个维度进行评分（0-10分），指出具体问题，提出改进建议。
请以JSON格式返回质量检查结果。"""

        messages = self._prepare_messages(quality_task, context)
        response = self._call_llm(messages, expect_json=True, max_tokens=1500)

        return AgentResult(
            content=json.dumps(response, ensure_ascii=False, indent=2),
            metadata={
                "quality_check_type": "chapter_quality",
                "check_dimensions": list(response.keys()) if isinstance(response, dict) else [],
                "chapter_length": len(chapter_content),
            },
        )

    def create_task_assignments(
        self, novel_input: NovelInput, plan_type: str = "standard"
    ) -> List[TaskAssignment]:
        """Create task assignments based on novel input.

        Args:
            novel_input: Novel input data
            plan_type: Type of plan ("standard", "fast", "detailed")

        Returns:
            List of task assignments
        """
        assignments = []

        # Always include plot designer
        assignments.append(
            TaskAssignment(
                agent_type="plot_designer",
                task_description=f"为{novel_input.genre}小说设计章节情节结构，大纲：{novel_input.chapter_outline}",
                priority=1,
                dependencies=[],
                expected_output_format="json",
            )
        )

        # Include character agent if there are characters
        if novel_input.characters:
            char_names = [char.name for char in novel_input.characters]
            assignments.append(
                TaskAssignment(
                    agent_type="character",
                    task_description=f"设计人物表现，人物：{', '.join(char_names)}，确保人物一致性",
                    priority=1,
                    dependencies=["plot_designer"],
                    expected_output_format="json",
                )
            )

        # Include scene renderer if there are scenes
        if novel_input.scenes:
            scene_names = [scene.name for scene in novel_input.scenes]
            assignments.append(
                TaskAssignment(
                    agent_type="scene_renderer",
                    task_description=f"设计场景描述，场景：{', '.join(scene_names)}，营造合适氛围",
                    priority=2,
                    dependencies=["plot_designer"],
                    expected_output_format="json",
                )
            )

        # Always include writing optimizer and consistency checker
        assignments.append(
            TaskAssignment(
                agent_type="writing_optimizer",
                task_description=f"优化文笔，确保符合{novel_input.genre}风格，语言优美",
                priority=3,
                dependencies=["plot_designer", "character", "scene_renderer"],
                expected_output_format="text",
            )
        )

        assignments.append(
            TaskAssignment(
                agent_type="consistency_checker",
                task_description="检查整体连贯性，实施'三板斧'防崩机制",
                priority=3,
                dependencies=["writing_optimizer"],
                expected_output_format="json",
            )
        )

        return assignments