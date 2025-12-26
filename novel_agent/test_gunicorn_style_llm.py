"""
单文件 Novel Agent 实现 - 基于 Gunicorn+Uvicorn 架构

这是一个完整的、单文件的小说生成系统，包含：
1. Master-Worker 架构（多进程）
2. 异步 LLM 调用（aiohttp + asyncio）
3. 并发任务处理
4. 自愈和监控

关键设计：
- 使用 loop.run_in_executor() 处理跨进程队列阻塞
- 每个任务独立执行，避免长连接问题
- Worker 进程内部使用异步事件循环实现高并发
"""
import os
import sys
import time
import asyncio
import multiprocessing
import random
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# 添加 src 到路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s (PID %(process)d): %(message)s'
)
logger = logging.getLogger(__name__)


# ============= 数据模型 =============

@dataclass
class NovelInput:
    """小说输入数据"""
    genre: str  # 类型：玄幻、仙侠、科幻等
    chapter_outline: str  # 章节大纲
    characters: List[str]  # 人物列表
    target_length: int = 2000  # 目标字数


@dataclass
class ChapterResult:
    """章节生成结果"""
    content: str
    success: bool
    error: Optional[str] = None
    execution_time: float = 0.0


# ============= Async LLM Client =============

class AsyncLLMClient:
    """异步 LLM 客户端 - 使用 aiohttp"""

    def __init__(self, provider: str = "deepseek"):
        from src.utils.config import config
        self.provider = provider
        self.config = config.get_llm_config(provider)
        self.logger = logging.getLogger("novel_agent.llm_client")

    async def achat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """异步调用 LLM API"""
        import aiohttp
        import json

        url = f"{self.config['base_url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        self.logger.info(f"[LLM] 调用 API，model={self.config['model']}")

        # 每次请求创建新的 session（避免 multiprocessing 问题）
        session = aiohttp.ClientSession()
        try:
            resp = await session.post(url, json=payload, headers=headers)

            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(f"API 返回 {resp.status}: {error_text}")

            response_text = await resp.text()
            response_data = json.loads(response_text)

            content = response_data["choices"][0]["message"]["content"]
            self.logger.info(f"[LLM] 成功! 响应长度={len(content)}")

            return content

        finally:
            await session.close()


# ============= Novel Agent (异步) =============

class NovelAgent:
    """小说生成 Agent - 异步版本"""

    def __init__(self, llm_provider: str = "deepseek"):
        self.llm_client = AsyncLLMClient(llm_provider)
        self.logger = logging.getLogger("novel_agent.agent")

    async def generate_chapter(self, novel_input: NovelInput) -> ChapterResult:
        """生成一章小说内容"""
        start_time = time.time()

        try:
            self.logger.info(f"[Agent] 开始生成章节，类型={novel_input.genre}")

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
        """制定创作计划"""
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

    async def _write_chapter(self, novel_input: NovelInput, plan: str) -> str:
        """撰写章节内容"""
        prompt = f"""请根据以下创作计划撰写章节：

类型：{novel_input.genre}
章节大纲：{novel_input.chapter_outline}
人物：{', '.join(novel_input.characters)}

创作计划：
{plan}

请直接开始撰写章节内容，目标字数约{novel_input.target_length}字。
注意：直接输出正文，不要有其他说明文字。"""

        messages = [
            {"role": "system", "content": f"你是一个{novel_input.genre}类型小说的专业作家。"},
            {"role": "user", "content": prompt}
        ]

        content = await self.llm_client.achat_completion(
            messages=messages,
            max_tokens=novel_input.target_length * 2,  # 给一些余量
        )

        self.logger.info(f"[Agent] 章节撰写完成，长度={len(content)}")
        return content


# ============= Worker (异步) =============

async def novel_agent_task(worker_id: str, task_id: str, novel_input: NovelInput) -> Dict:
    """小说生成任务（异步）"""
    logger.info(f"    [协程] {worker_id} 开始处理 {task_id}")

    try:
        # 创建 Agent
        agent = NovelAgent(llm_provider="deepseek")

        # 生成章节
        result = await agent.generate_chapter(novel_input)

        logger.info(f"    [协程] {worker_id} {task_id} {'✅ 成功' if result.success else '❌ 失败'}")

        return {
            "task_id": task_id,
            "success": result.success,
            "content": result.content,
            "error": result.error,
            "execution_time": result.execution_time,
        }

    except Exception as e:
        logger.error(f"    [协程] {worker_id} {task_id} 异常: {e}")
        return {
            "task_id": task_id,
            "success": False,
            "error": str(e),
            "execution_time": 0,
        }


async def async_worker_loop(
    worker_id: str,
    task_queue: multiprocessing.Queue,
    result_queue: multiprocessing.Queue,
    max_concurrent: int = 2,
):
    """
    Worker 进程的异步事件循环

    关键：使用 loop.run_in_executor() 处理队列阻塞
    """
    logger.info(f"  [+] {worker_id} (PID: {os.getpid()}) 异步 Worker 启动, max_concurrent={max_concurrent}")

    active_tasks = []
    completed_count = 0
    loop = asyncio.get_running_loop()

    while True:
        try:
            # 关键：使用 run_in_executor 在线程池中处理队列的阻塞操作
            task = await loop.run_in_executor(None, task_queue.get_nowait)

            if task.get("command") == "STOP":
                logger.info(f"Worker {worker_id} 收到 STOP 指令")
                break

            task_id = task.get("task_id", f"TASK-{int(time.time())}")
            novel_input = task.get("novel_input")

            logger.info(f"Worker {worker_id} 收到任务: {task_id}")

            # 创建异步任务（非阻塞）
            t = asyncio.create_task(
                novel_agent_task(worker_id, task_id, novel_input)
            )
            active_tasks.append(t)

            # 检查已完成的任务
            for t in active_tasks[:]:
                if t.done():
                    active_tasks.remove(t)
                    try:
                        result = t.result()
                        completed_count += 1
                        # 将结果放入结果队列
                        result_queue.put({
                            "worker_id": worker_id,
                            **result,
                        })
                        logger.info(f"    [完成] {worker_id} 任务 {result['task_id']} 已返回结果")
                    except Exception as e:
                        logger.error(f"    [错误] {worker_id} 任务结果获取失败: {e}")

            logger.info(f"    [状态] {worker_id} 当前并发任务数: {len(active_tasks)} | 已完成: {completed_count}")

            # 限制并发数
            if len(active_tasks) >= max_concurrent:
                logger.info(f"    [限流] {worker_id} 达到最大并发数，等待任务完成...")
                # 等待至少一个任务完成
                done, pending = await asyncio.wait(active_tasks, return_when=asyncio.FIRST_COMPLETED)
                active_tasks = list(pending)

        except Exception:
            # 队列为空或其他错误，继续下一轮
            await asyncio.sleep(0.5)

    # 等待所有剩余任务完成
    if active_tasks:
        logger.info(f"Worker {worker_id} 等待 {len(active_tasks)} 个任务完成...")
        await asyncio.gather(*active_tasks, return_exceptions=True)

    logger.info(f"Worker {worker_id} 总共完成 {completed_count} 个任务")


def start_worker_process(
    worker_id: str,
    task_queue: multiprocessing.Queue,
    result_queue: multiprocessing.Queue,
    max_concurrent: int = 2,
):
    """子进程入口点"""
    try:
        asyncio.run(async_worker_loop(
            worker_id,
            task_queue,
            result_queue,
            max_concurrent,
        ))
    finally:
        logger.info(f"Worker {worker_id} 进程退出")
        os._exit(0)


# ============= Master Supervisor =============

class NovelAgentSupervisor:
    """Novel Agent Supervisor - Gunicorn 风格"""

    def __init__(self, min_workers=1, max_workers=2, max_concurrent=2):
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.workers = {}  # {pid: worker_id}
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.max_concurrent = max_concurrent

        # 统计信息（手动队列大小跟踪）
        self.submitted_tasks = 0
        self.completed_tasks = 0
        self._queue_size = 0

    def spawn_worker(self):
        """Fork 新的 Worker 进程"""
        if len(self.workers) >= self.max_workers:
            return

        worker_id = f"Worker-{random.randint(10, 99)}"
        pid = os.fork()

        if pid == 0:
            # 子进程
            start_worker_process(
                worker_id,
                self.task_queue,
                self.result_queue,
                self.max_concurrent,
            )
        else:
            # 父进程
            self.workers[pid] = worker_id
            logger.info(f"[*] Master: 扩容进程 -> {worker_id} (PID: {pid})")

    def submit_task(self, novel_input: NovelInput) -> str:
        """提交小说生成任务"""
        task_id = f"TASK-{self.submitted_tasks + 1}"
        task = {
            "task_id": task_id,
            "novel_input": novel_input,
        }
        self.task_queue.put(task)
        self.submitted_tasks += 1
        self._queue_size += 1
        logger.info(f"[Master] 提交任务: {task_id}")
        return task_id

    def collect_results(self) -> List[Dict]:
        """收集已完成的结果"""
        results = []
        try:
            while True:
                result = self.result_queue.get_nowait()
                results.append(result)
                self.completed_tasks += 1
                self._queue_size -= 1
                logger.info(
                    f"[Master] 收到结果: {result['task_id']} "
                    f"{'✅' if result['success'] else '❌'} "
                    f"长度={len(result.get('content', ''))}"
                )
        except:
            pass
        return results

    def monitor(self, duration: int = 120):
        """监控循环"""
        logger.info("=" * 60)
        logger.info("Novel Agent Supervisor (单文件版本)")
        logger.info(f"配置: Worker={self.min_workers}-{self.max_workers}, "
                   f"max_concurrent={self.max_concurrent}")
        logger.info("=" * 60)

        # 初始水位
        for _ in range(self.min_workers):
            self.spawn_worker()

        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                # 收集结果
                self.collect_results()

                # 监控队列状态（使用手动计数）
                q_size = self._queue_size
                worker_count = len(self.workers)

                # 自愈：检查退出的进程
                try:
                    pid, status = os.waitpid(-1, os.WNOHANG)
                    if pid > 0:
                        worker_id = self.workers.pop(pid, "Unknown")
                        logger.warning(f"[!] Master: Worker {worker_id} 挂了，自愈中...")
                        self.spawn_worker()
                except ChildProcessError:
                    pass

                logger.info(
                    f"--- Master: 队列={q_size} | Worker={worker_count} | "
                    f"已提交={self.submitted_tasks} | 已完成={self.completed_tasks} ---"
                )

                # 如果所有任务完成，退出
                if self.completed_tasks >= self.submitted_tasks and self.submitted_tasks > 0:
                    logger.info("[Master] 所有任务已完成!")
                    break

                time.sleep(2)

        except KeyboardInterrupt:
            logger.info("\n[*] Master 收到停止信号")
        finally:
            self.shutdown()

    def shutdown(self):
        """优雅关闭"""
        logger.info("\n[*] Master 正在关闭...")

        # 发送停止信号
        for _ in self.workers:
            self.task_queue.put({"command": "STOP"})

        time.sleep(3)

        # 强制杀死
        for pid in list(self.workers.keys()):
            try:
                os.kill(pid, 9)
            except:
                pass

        logger.info(f"\n最终统计: 提交 {self.submitted_tasks} | 完成 {self.completed_tasks}")


# ============= 主程序 =============

if __name__ == "__main__":
    # 创建测试任务
    test_tasks = [
        NovelInput(
            genre="玄幻",
            chapter_outline="第一章：少年觉醒",
            characters=["张三", "李四"],
            target_length=1000,
        ),
        NovelInput(
            genre="科幻",
            chapter_outline="第一章：星际启程",
            characters=["王五", "赵六"],
            target_length=1000,
        ),
    ]

    # 创建 Supervisor
    supervisor = NovelAgentSupervisor(
        min_workers=1,
        max_workers=2,
        max_concurrent=2,
    )

    # 提交任务
    logger.info("\n提交测试任务...")
    for task in test_tasks:
        supervisor.submit_task(task)

    # 运行监控
    try:
        supervisor.monitor(duration=120)  # 2分钟超时
    except KeyboardInterrupt:
        logger.info("\n程序结束")
