"""
Novel Agent Worker - 基于 asyncio 的异步 Worker

每个 Worker 进程运行一个异步事件循环，实现高并发任务处理
"""

import asyncio
import logging
import os
import sys
import time
from multiprocessing import Queue
from pathlib import Path
from typing import Dict, Optional

# 添加 src 到路径（在子进程中）
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))


async def novel_agent_task(
    worker_id: str,
    task_id: str,
    novel_input,
    llm_provider: str = "deepseek",
) -> Dict:
    """小说生成任务（异步）

    Args:
        worker_id: Worker ID
        task_id: Task ID
        novel_input: NovelInput 数据
        llm_provider: LLM 提供商

    Returns:
        结果字典
    """
    logger = logging.getLogger("novel_agent.worker")
    logger.info(f"    [协程] {worker_id} 开始处理 {task_id}")

    try:
        from agents.novel_agent import NovelAgent

        # 创建 Agent（在协程中创建，避免序列化问题）
        agent = NovelAgent(llm_provider=llm_provider)

        # 生成章节
        result = await agent.generate_chapter(novel_input)

        logger.info(
            f"    [协程] {worker_id} {task_id} "
            f"{'✅ 成功' if result.success else '❌ 失败'}"
        )

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
            "content": "",
            "error": str(e),
            "execution_time": 0,
        }


async def async_worker_loop(
    worker_id: str,
    task_queue: Queue,
    result_queue: Queue,
    max_concurrent: int = 2,
):
    """
    Worker 进程的异步事件循环

    关键设计：
    1. 使用 loop.run_in_executor() 处理跨进程队列的阻塞操作
    2. 使用 asyncio.create_task() 实现非阻塞并发
    3. 限制并发数避免过载

    Args:
        worker_id: Worker ID
        task_queue: 任务队列（跨进程）
        result_queue: 结果队列（跨进程）
        max_concurrent: 最大并发任务数
    """
    logger = logging.getLogger("novel_agent.worker")
    logger.info(
        f"  [+] {worker_id} (PID: {os.getpid()}) 异步 Worker 启动, "
        f"max_concurrent={max_concurrent}"
    )

    active_tasks = []
    completed_count = 0
    loop = asyncio.get_running_loop()

    while True:
        # 首先检查是否有已完成的任务（在任何操作之前）
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
                    logger.info(
                        f"    [完成] {worker_id} 任务 {result['task_id']} "
                        f"已返回结果"
                    )
                except Exception as e:
                    logger.error(
                        f"    [错误] {worker_id} 任务结果获取失败: {e}"
                    )

        # 如果没有活跃任务，尝试从队列获取任务
        if len(active_tasks) == 0:
            try:
                # 尝试非阻塞获取任务
                task = task_queue.get_nowait()
            except:
                # 队列为空，没有任务在执行，可以退出了
                logger.info(f"Worker {worker_id} 所有任务已完成，退出")
                break

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

        # 有活跃任务时的处理
        else:
            # 尝试获取更多任务
            try:
                task = task_queue.get_nowait()

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
            except:
                # 队列为空，继续处理

                # 限制并发数：如果已达到最大值，等待任务完成
                if len(active_tasks) >= max_concurrent:
                    # 等待至少一个任务完成
                    done, pending = await asyncio.wait(
                        active_tasks,
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    active_tasks = list(pending)

                    # 立即处理刚完成的任务
                    for t in done:
                        try:
                            result = t.result()
                            completed_count += 1
                            # 将结果放入结果队列
                            result_queue.put({
                                "worker_id": worker_id,
                                **result,
                            })
                            logger.info(
                                f"    [完成] {worker_id} 任务 {result['task_id']} "
                                f"已返回结果"
                            )
                        except Exception as e:
                            logger.error(
                                f"    [错误] {worker_id} 任务结果获取失败: {e}"
                            )

                    # 回到循环开始，处理其他可能的已完成任务
                    continue
                else:
                    # 未达到最大并发数，短暂让出控制权
                    await asyncio.sleep(0.1)

    # 等待所有剩余任务完成
    if active_tasks:
        logger.info(f"Worker {worker_id} 等待 {len(active_tasks)} 个任务完成...")
        await asyncio.gather(*active_tasks, return_exceptions=True)

    logger.info(f"Worker {worker_id} 总共完成 {completed_count} 个任务")


def run_worker_process(
    worker_id: str,
    task_queue: Queue,
    result_queue: Queue,
    max_concurrent: int = 2,
):
    """子进程入口点

    Args:
        worker_id: Worker ID
        task_queue: 任务队列
        result_queue: 结果队列
        max_concurrent: 最大并发数
    """
    try:
        asyncio.run(async_worker_loop(
            worker_id,
            task_queue,
            result_queue,
            max_concurrent,
        ))
    finally:
        logging.getLogger("novel_agent.worker").info(
            f"Worker {worker_id} 进程退出"
        )
        os._exit(0)
