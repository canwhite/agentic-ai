"""
Novel Agent - 小说生成 Agent

基于 asyncio 的异步小说生成 Agent
"""

import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# 添加 src 到路径（在子进程中）
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


@dataclass
class NovelInput:
    """小说输入数据"""
    genre: str  # 类型：玄幻、仙侠、科幻等
    chapter_outline: str  # 章节大纲
    characters: List[str] = field(default_factory=list)  # 人物列表
    target_length: int = 2000  # 目标字数


@dataclass
class ChapterResult:
    """章节生成结果"""
    content: str
    success: bool
    error: Optional[str] = None
    execution_time: float = 0.0


class NovelAgent:
    """小说生成 Agent - 异步版本"""

    def __init__(self, llm_provider: str = "deepseek"):
        """初始化 Agent

        Args:
            llm_provider: LLM 提供商名称
        """
        from utils.async_llm_client import AsyncLLMClient

        self.llm_client = AsyncLLMClient(provider=llm_provider)
        self.logger = logging.getLogger("novel_agent.agent")

    async def generate_chapter(self, novel_input: NovelInput) -> ChapterResult:
        """生成一章小说内容

        Args:
            novel_input: 小说输入数据

        Returns:
            章节生成结果
        """
        start_time = time.time()

        try:
            self.logger.info(
                f"[Agent] 开始生成章节，类型={novel_input.genre}"
            )

            # Step 1: 制定创作计划
            plan = await self._create_creation_plan(novel_input)

            # Step 2: 生成章节
            content = await self._write_chapter(novel_input, plan)

            execution_time = time.time() - start_time

            return ChapterResult(
                content=content,
                success=True,
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"[Agent] 生成失败: {e}")
            return ChapterResult(
                content="",
                success=False,
                error=str(e),
                execution_time=execution_time,
            )

    async def _create_creation_plan(self, novel_input: NovelInput) -> str:
        """制定创作计划

        Args:
            novel_input: 小说输入数据

        Returns:
            创作计划文本
        """
        prompt = f"""请为以下小说制定创作计划：

类型：{novel_input.genre}
章节大纲：{novel_input.chapter_outline}
人物：{', '.join(novel_input.characters)}
目标字数：{novel_input.target_length}

请提供创作计划，包括：
1. 章节结构
2. 情节要点
3. 人物安排

请用200字左右简要说明。"""

        messages = [
            {"role": "system", "content": "你是一个专业的小说创作策划。"},
            {"role": "user", "content": prompt}
        ]

        plan = await self.llm_client.achat_completion(
            messages=messages,
            max_tokens=500,
        )

        self.logger.info(f"[Agent] 创作计划完成")
        return plan

    async def _write_chapter(
        self,
        novel_input: NovelInput,
        plan: str,
    ) -> str:
        """撰写章节内容

        Args:
            novel_input: 小说输入数据
            plan: 创作计划

        Returns:
            章节内容
        """
        prompt = f"""请根据以下创作计划撰写章节：

类型：{novel_input.genre}
章节大纲：{novel_input.chapter_outline}
人物：{', '.join(novel_input.characters)}

创作计划：
{plan}

请直接开始撰写章节内容，目标字数约{novel_input.target_length}字。
注意：直接输出正文，不要有其他说明文字。"""

        messages = [
            {
                "role": "system",
                "content": f"你是一个{novel_input.genre}类型小说的专业作家。"
            },
            {"role": "user", "content": prompt}
        ]

        content = await self.llm_client.achat_completion(
            messages=messages,
            max_tokens=novel_input.target_length * 2,  # 给一些余量
        )

        self.logger.info(f"[Agent] 章节撰写完成，长度={len(content)}")
        return content
