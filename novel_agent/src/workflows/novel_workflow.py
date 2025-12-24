"""
Main workflow for novel chapter generation using multi-agent collaboration.
"""

import json
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from src.models import NovelInput, ChapterResult, ChapterDraft
from src.agents import (
    DirectorAgent,
    PlotDesignAgent,
    CharacterAgent,
    SceneRendererAgent,
    WritingOptimizerAgent,
    ConsistencyCheckerAgent,
)


@dataclass
class WorkflowConfig:
    """Configuration for novel workflow."""

    # Agent configurations
    llm_provider: str = "deepseek"  # "deepseek" or "openai"
    temperature: float = 0.7
    max_retries: int = 3
    timeout_seconds: int = 300  # 5 minutes

    # Workflow settings
    enable_parallel_execution: bool = True
    enable_quality_checks: bool = True
    enable_anti_collapse: bool = True
    output_format: str = "text"  # "text" or "json"

    # Performance settings
    max_chapter_length: int = 5000  # characters
    min_chapter_length: int = 1000  # characters


@dataclass
class WorkflowResult:
    """Result of workflow execution."""

    success: bool
    chapter_result: Optional[ChapterResult] = None
    execution_time: float = 0.0
    agent_executions: Dict[str, Dict[str, Any]] = None
    errors: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.agent_executions is None:
            self.agent_executions = {}
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "execution_time": self.execution_time,
            "chapter_length": len(self.chapter_result.content) if self.chapter_result else 0,
            "agent_count": len(self.agent_executions),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }


class NovelWorkflow:
    """Main workflow for novel chapter generation."""

    def __init__(self, config: Optional[WorkflowConfig] = None):
        """Initialize novel workflow.

        Args:
            config: Workflow configuration
        """
        self.config = config or WorkflowConfig()
        self.logger = logging.getLogger("novel_agent.workflow")

        # Initialize agents
        self._initialize_agents()

        # Execution tracking
        self.execution_history: List[Dict[str, Any]] = []

    def _initialize_agents(self) -> None:
        """Initialize all agents."""
        agent_kwargs = {
            "llm_provider": self.config.llm_provider,
            "temperature": self.config.temperature,
        }

        self.director = DirectorAgent(**agent_kwargs)
        self.plot_designer = PlotDesignAgent(**agent_kwargs)
        self.character_agent = CharacterAgent(**agent_kwargs)
        self.scene_renderer = SceneRendererAgent(**agent_kwargs)
        self.writing_optimizer = WritingOptimizerAgent(**agent_kwargs)
        self.consistency_checker = ConsistencyCheckerAgent(**agent_kwargs)

        self.agents = {
            "director": self.director,
            "plot_designer": self.plot_designer,
            "character_agent": self.character_agent,
            "scene_renderer": self.scene_renderer,
            "writing_optimizer": self.writing_optimizer,
            "consistency_checker": self.consistency_checker,
        }

        self.logger.info(f"Initialized {len(self.agents)} agents")

    def execute(self, novel_input: NovelInput) -> WorkflowResult:
        """Execute complete novel chapter generation workflow.

        Args:
            novel_input: Novel input data

        Returns:
            WorkflowResult with execution results
        """
        start_time = time.time()
        result = WorkflowResult(success=False)

        try:
            self.logger.info(f"Starting novel workflow for genre: {novel_input.genre}")

            # Step 1: Director creates creation plan
            creation_plan = self._create_creation_plan(novel_input, result)
            if not creation_plan:
                return result

            # Step 2: Execute agent tasks based on plan
            agent_outputs = self._execute_agent_tasks(novel_input, creation_plan, result)
            if not agent_outputs:
                return result

            # Step 3: Synthesize chapter from agent outputs
            chapter_draft = self._synthesize_chapter(novel_input, agent_outputs, result)
            if not chapter_draft:
                return result

            # Step 4: Optimize writing style
            optimized_content = self._optimize_writing(novel_input, chapter_draft, result)
            if not optimized_content:
                return result

            # Step 5: Perform consistency checks
            if self.config.enable_quality_checks:
                quality_ok = self._perform_quality_checks(novel_input, optimized_content, result)
                if not quality_ok and self.config.enable_anti_collapse:
                    # If quality check fails, try to fix issues
                    optimized_content = self._fix_quality_issues(novel_input, optimized_content, result)

            # Step 6: Create final result
            final_result = self._create_final_result(novel_input, optimized_content, result)
            result.chapter_result = final_result
            result.success = True

            execution_time = time.time() - start_time
            result.execution_time = execution_time

            self._record_execution(novel_input, result, execution_time)

            self.logger.info(
                f"Workflow completed successfully in {execution_time:.2f}s. "
                f"Chapter length: {len(final_result.content)} characters"
            )

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            result.errors.append(f"Workflow execution failed: {str(e)}")
            self.logger.error(f"Workflow execution failed: {str(e)}")

            self._record_execution(novel_input, result, execution_time)

            return result

    def _create_creation_plan(
        self, novel_input: NovelInput, result: WorkflowResult
    ) -> Optional[Dict[str, Any]]:
        """Create creation plan using director agent.

        Args:
            novel_input: Novel input data
            result: Workflow result to update

        Returns:
            Creation plan or None if failed
        """
        self.logger.info("Step 1: Creating creation plan")

        try:
            task = "制定详细的创作计划，包括任务分配、优先级和依赖关系"
            context = {"novel_input": novel_input}

            agent_result = self.director.execute(task, context)

            if not agent_result.success:
                result.errors.append(f"Director agent failed: {agent_result.error}")
                return None

            creation_plan = json.loads(agent_result.content)
            result.agent_executions["director"] = {
                "success": True,
                "execution_time": agent_result.metadata.get("execution_time", 0),
                "plan_type": agent_result.metadata.get("plan_type", "unknown"),
            }

            self.logger.info(f"Creation plan created with {len(creation_plan.get('任务分配', []))} tasks")
            return creation_plan

        except Exception as e:
            result.errors.append(f"Failed to create creation plan: {str(e)}")
            self.logger.error(f"Failed to create creation plan: {str(e)}")
            return None

    def _execute_agent_tasks(
        self,
        novel_input: NovelInput,
        creation_plan: Dict[str, Any],
        result: WorkflowResult,
    ) -> Optional[Dict[str, Any]]:
        """Execute agent tasks based on creation plan.

        Args:
            novel_input: Novel input data
            creation_plan: Creation plan from director
            result: Workflow result to update

        Returns:
            Agent outputs or None if failed
        """
        self.logger.info("Step 2: Executing agent tasks")

        agent_outputs = {}
        task_assignments = creation_plan.get("任务分配", [])

        # Group tasks by dependency level for sequential execution
        # For now, execute in fixed order: plot -> character -> scene -> writing -> consistency
        execution_order = [
            ("plot_designer", "设计章节情节结构"),
            ("character_agent", "设计人物表现和对话"),
            ("scene_renderer", "设计场景渲染"),
            ("writing_optimizer", "优化文笔"),
            ("consistency_checker", "检查连贯性"),
        ]

        context = {"novel_input": novel_input, "creation_plan": creation_plan}

        for agent_name, default_task in execution_order:
            if agent_name not in self.agents:
                self.logger.warning(f"Agent {agent_name} not found, skipping")
                continue

            agent = self.agents[agent_name]
            self.logger.info(f"Executing {agent_name}")

            try:
                # Find specific task from plan, or use default
                task_description = default_task
                for assignment in task_assignments:
                    if assignment.get("agent") == agent_name:
                        task_description = assignment.get("task", default_task)
                        break

                agent_result = agent.execute(task_description, context)

                if not agent_result.success:
                    result.warnings.append(f"Agent {agent_name} had issues: {agent_result.error}")
                    # Continue with other agents even if one fails
                    agent_outputs[agent_name] = {"error": agent_result.error}
                else:
                    agent_outputs[agent_name] = {
                        "content": agent_result.content,
                        "metadata": agent_result.metadata,
                    }

                    # Update context for next agents
                    context[agent_name + "_output"] = agent_result.content
                    context[agent_name + "_metadata"] = agent_result.metadata

                result.agent_executions[agent_name] = {
                    "success": agent_result.success,
                    "task": task_description,
                    "execution_time": agent_result.metadata.get("execution_time", 0)
                    if agent_result.metadata else 0,
                }

            except Exception as e:
                error_msg = f"Agent {agent_name} execution failed: {str(e)}"
                result.errors.append(error_msg)
                self.logger.error(error_msg)
                agent_outputs[agent_name] = {"error": str(e)}
                result.agent_executions[agent_name] = {
                    "success": False,
                    "error": str(e),
                }

        self.logger.info(f"Agent tasks completed. Outputs from {len(agent_outputs)} agents")
        return agent_outputs

    def _synthesize_chapter(
        self,
        novel_input: NovelInput,
        agent_outputs: Dict[str, Any],
        result: WorkflowResult,
    ) -> Optional[ChapterDraft]:
        """Synthesize chapter from agent outputs.

        Args:
            novel_input: Novel input data
            agent_outputs: Outputs from all agents
            result: Workflow result to update

        Returns:
            Chapter draft or None if failed
        """
        self.logger.info("Step 3: Synthesizing chapter from agent outputs")

        try:
            task = "根据专业Agent输出合成最终小说章节"
            context = {
                "novel_input": novel_input,
                "agent_outputs": agent_outputs,
                "intermediate_results": {},  # Could be populated from previous steps
            }

            agent_result = self.director.execute(task, context)

            if not agent_result.success:
                result.errors.append(f"Chapter synthesis failed: {agent_result.error}")
                return None

            # Create chapter draft
            chapter_draft = ChapterDraft(
                content=agent_result.content,
                metadata={
                    "synthesis_source": "director_agent",
                    "agent_outputs_used": list(agent_outputs.keys()),
                    "synthesis_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    **agent_result.metadata,
                },
            )

            result.agent_executions["synthesis"] = {
                "success": True,
                "execution_time": agent_result.metadata.get("execution_time", 0),
                "chapter_length": len(agent_result.content),
            }

            self.logger.info(f"Chapter synthesized: {len(agent_result.content)} characters")
            return chapter_draft

        except Exception as e:
            result.errors.append(f"Chapter synthesis failed: {str(e)}")
            self.logger.error(f"Chapter synthesis failed: {str(e)}")
            return None

    def _optimize_writing(
        self,
        novel_input: NovelInput,
        chapter_draft: ChapterDraft,
        result: WorkflowResult,
    ) -> Optional[str]:
        """Optimize writing style.

        Args:
            novel_input: Novel input data
            chapter_draft: Chapter draft to optimize
            result: Workflow result to update

        Returns:
            Optimized content or None if failed
        """
        self.logger.info("Step 4: Optimizing writing style")

        try:
            task = "对章节进行完整的文笔优化，包括语言表达、文学性和阅读体验"
            # Extract style preferences
            writing_style = novel_input.style_preferences.get("writing_style", f"{novel_input.genre}风格")
            target_audience = novel_input.style_preferences.get("target_audience", "一般读者")

            context = {
                "novel_input": novel_input,
                "text": chapter_draft.content,
                "chapter_content": chapter_draft.content,
                "target_style": writing_style,
                "target_audience": target_audience,
            }

            agent_result = self.writing_optimizer.execute(task, context)

            if not agent_result.success:
                result.warnings.append(f"Writing optimization had issues: {agent_result.error}")
                # Return original content if optimization fails
                return chapter_draft.content

            # Parse optimized content from response
            if agent_result.metadata.get("optimization_type") == "complete_optimization":
                # Response is JSON with optimized_text field
                try:
                    response_data = json.loads(agent_result.content)
                    optimized_content = response_data.get("optimized_text", chapter_draft.content)
                except:
                    optimized_content = agent_result.content
            else:
                optimized_content = agent_result.content

            result.agent_executions["writing_optimization"] = {
                "success": True,
                "execution_time": agent_result.metadata.get("execution_time", 0),
                "original_length": len(chapter_draft.content),
                "optimized_length": len(optimized_content),
                "length_change": len(optimized_content) - len(chapter_draft.content),
            }

            self.logger.info(
                f"Writing optimized: {len(chapter_draft.content)} -> {len(optimized_content)} characters"
            )
            return optimized_content

        except Exception as e:
            result.warnings.append(f"Writing optimization failed: {str(e)}")
            self.logger.warning(f"Writing optimization failed: {str(e)}")
            # Return original content if optimization fails
            return chapter_draft.content

    def _perform_quality_checks(
        self,
        novel_input: NovelInput,
        chapter_content: str,
        result: WorkflowResult,
    ) -> bool:
        """Perform quality checks on chapter.

        Args:
            novel_input: Novel input data
            chapter_content: Chapter content to check
            result: Workflow result to update

        Returns:
            True if quality is acceptable, False otherwise
        """
        self.logger.info("Step 5: Performing quality checks")

        try:
            task = "对章节进行完整的连贯性检查，实施'三板斧'防崩机制"
            context = {
                "novel_input": novel_input,
                "chapter_content": chapter_content,
                "content_length": len(chapter_content),
            }

            agent_result = self.consistency_checker.execute(task, context)

            if not agent_result.success:
                result.warnings.append(f"Quality check had issues: {agent_result.error}")
                return True  # Continue even if check fails

            # Parse check results
            try:
                check_results = json.loads(agent_result.content)
            except:
                check_results = {"summary": "Check completed but results not parseable"}

            # Calculate coherence score
            coherence_score = self.consistency_checker.calculate_coherence_score(
                check_results, context
            )

            result.agent_executions["quality_check"] = {
                "success": True,
                "execution_time": agent_result.metadata.get("execution_time", 0),
                "coherence_score": coherence_score.get("adjusted_score", 0),
                "coherence_level": coherence_score.get("coherence_level", "未知"),
                "total_issues": coherence_score.get("total_issues", 0),
            }

            # Check if quality is acceptable
            score = coherence_score.get("adjusted_score", 0)
            is_acceptable = score >= 70  # Accept if score >= 70

            if not is_acceptable:
                result.warnings.append(
                    f"Chapter quality below threshold: score={score:.1f}, "
                    f"level={coherence_score.get('coherence_level', '未知')}"
                )
                # Store check results for potential fixing
                result.agent_executions["quality_check"]["check_results"] = check_results
                result.agent_executions["quality_check"]["needs_fixing"] = True

            self.logger.info(
                f"Quality check completed: score={score:.1f}, acceptable={is_acceptable}"
            )
            return is_acceptable

        except Exception as e:
            result.warnings.append(f"Quality check failed: {str(e)}")
            self.logger.warning(f"Quality check failed: {str(e)}")
            return True  # Continue even if check fails

    def _fix_quality_issues(
        self,
        novel_input: NovelInput,
        chapter_content: str,
        result: WorkflowResult,
    ) -> str:
        """Attempt to fix quality issues.

        Args:
            novel_input: Novel input data
            chapter_content: Chapter content with issues
            result: Workflow result to update

        Returns:
            Fixed content (or original if fixing fails)
        """
        self.logger.info("Attempting to fix quality issues")

        try:
            # Get check results from previous step
            check_results = result.agent_executions.get("quality_check", {}).get("check_results", {})

            task = "根据质量检查结果修复章节问题，重点解决'三板斧'防崩机制发现的问题"
            context = {
                "novel_input": novel_input,
                "chapter_content": chapter_content,
                "check_results": check_results,
                "fix_priority": "解决严重问题，保持原文核心内容",
            }

            # Use director agent to coordinate fixes
            agent_result = self.director.execute(task, context)

            if not agent_result.success:
                result.warnings.append(f"Quality fixing failed: {agent_result.error}")
                return chapter_content

            fixed_content = agent_result.content

            result.agent_executions["quality_fixing"] = {
                "success": True,
                "execution_time": agent_result.metadata.get("execution_time", 0),
                "original_length": len(chapter_content),
                "fixed_length": len(fixed_content),
            }

            self.logger.info(f"Quality issues fixed: {len(chapter_content)} -> {len(fixed_content)} characters")
            return fixed_content

        except Exception as e:
            result.warnings.append(f"Quality fixing failed: {str(e)}")
            self.logger.warning(f"Quality fixing failed: {str(e)}")
            return chapter_content

    def _create_final_result(
        self,
        novel_input: NovelInput,
        chapter_content: str,
        result: WorkflowResult,
    ) -> ChapterResult:
        """Create final chapter result.

        Args:
            novel_input: Novel input data
            chapter_content: Final chapter content
            result: Workflow result to update

        Returns:
            ChapterResult object
        """
        # Calculate readability score
        readability_score = self.writing_optimizer.calculate_readability_score(chapter_content)

        # Create metadata
        metadata = {
            "workflow_version": "1.0",
            "generation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "novel_genre": novel_input.genre,
            "chapter_outline": novel_input.chapter_outline,
            "character_count": len(novel_input.characters),
            "scene_count": len(novel_input.scenes),
            "content_length": len(chapter_content),
            "readability_score": readability_score,
            "agent_executions": result.agent_executions,
            "warnings": result.warnings,
            "errors": result.errors,
        }

        # Add quality check results if available
        if "quality_check" in result.agent_executions:
            metadata["quality_check"] = result.agent_executions["quality_check"]

        chapter_result = ChapterResult(
            content=chapter_content,
            format=self.config.output_format,
            metadata=metadata,
        )

        return chapter_result

    def _record_execution(
        self,
        novel_input: NovelInput,
        result: WorkflowResult,
        execution_time: float,
    ) -> None:
        """Record workflow execution.

        Args:
            novel_input: Novel input data
            result: Workflow result
            execution_time: Total execution time
        """
        record = {
            "timestamp": time.time(),
            "execution_time": execution_time,
            "novel_genre": novel_input.genre,
            "success": result.success,
            "chapter_length": len(result.chapter_result.content) if result.chapter_result else 0,
            "agent_count": len(result.agent_executions),
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
        }

        self.execution_history.append(record)

        # Keep only last 100 records
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get workflow execution statistics.

        Returns:
            Execution statistics
        """
        if not self.execution_history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "avg_chapter_length": 0,
            }

        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r["success"])
        avg_time = sum(r["execution_time"] for r in self.execution_history) / total
        avg_length = sum(r["chapter_length"] for r in self.execution_history) / total

        return {
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "avg_execution_time": avg_time,
            "avg_chapter_length": avg_length,
        }

    def reset_history(self) -> None:
        """Reset execution history."""
        self.execution_history.clear()
        self.logger.info("Workflow execution history reset")

        # Also reset agent histories
        for agent_name, agent in self.agents.items():
            agent.reset_history()