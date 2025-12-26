"""
Novel Agent Supervisor - 基于 Gunicorn+Uvicorn 架构

Master 进程管理：
- Fork 多个 Worker 进程
- 任务队列管理
- 自愈和监控
"""

import logging
import os
import sys
import time
import random
from pathlib import Path
from typing import Dict, Optional, List
from multiprocessing import Queue, Process

# 添加 src 到路径
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


class Supervisor:
    """Novel Agent Supervisor (Gunicorn 风格)

    管理 Worker 进程，分配任务，收集结果
    """

    def __init__(
        self,
        min_workers: int = 1,
        max_workers: int = 4,
        worker_max_concurrent: int = 3,
    ):
        """Initialize supervisor.

        Args:
            min_workers: 最小 Worker 数量
            max_workers: 最大 Worker 数量
            worker_max_concurrent: 每个 Worker 的最大并发任务数
        """
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.worker_max_concurrent = worker_max_concurrent

        # 任务队列（跨进程）
        self.task_queue = Queue()
        self.result_queue = Queue()

        # Worker 进程管理
        self.workers: Dict[int, str] = {}  # {pid: worker_id}

        # 统计信息（手动队列大小跟踪，避免 macOS qsize() 问题）
        self._queue_size = 0
        self.submitted_tasks = 0
        self.completed_tasks = 0

        # 监控线程
        self._monitor_thread: Optional[Process] = None
        self._stop_event = None

        self.logger = logging.getLogger("novel_agent.supervisor")

    def spawn_worker(self) -> Optional[str]:
        """Fork 一个新的 Worker 进程.

        Returns:
            Worker ID 或 None（如果已达到最大数量）
        """
        if len(self.workers) >= self.max_workers:
            self.logger.warning(f"已达到最大 Worker 数量: {self.max_workers}")
            return None

        worker_id = f"Worker-{random.randint(10, 99)}"
        pid = os.fork()

        if pid == 0:
            # 子进程 - 启动 Worker
            self._run_worker_process(worker_id)
        else:
            # 父进程 - 记录 Worker
            self.workers[pid] = worker_id
            self.logger.info(f"[*] Master: 扩容进程 -> {worker_id} (PID: {pid})")
            return worker_id

    def _run_worker_process(self, worker_id: str):
        """启动 Worker 进程（在子进程中执行）.

        Args:
            worker_id: Worker ID
        """
        from src.runtime.worker import run_worker_process

        try:
            run_worker_process(
                worker_id,
                self.task_queue,
                self.result_queue,
                self.worker_max_concurrent,
            )
        finally:
            # Worker 退出
            os._exit(0)

    def submit_task(self, novel_input) -> str:
        """提交小说生成任务.

        Args:
            novel_input: NovelInput 数据

        Returns:
            Task ID
        """
        task_id = f"task-{time.time_ns()}-{random.randint(1000, 9999)}"
        task = {
            "task_id": task_id,
            "novel_input": novel_input,
        }
        self.task_queue.put(task)
        self.submitted_tasks += 1
        self._queue_size += 1

        self.logger.info(f"[Master] Task {task_id} submitted, total={self.submitted_tasks}")
        return task_id

    def get_result(self, timeout: float = 0.1):
        """获取一个完成的任务结果.

        Args:
            timeout: 超时时间（秒）

        Returns:
            Result dict 或 None
        """
        try:
            result = self.result_queue.get(timeout=timeout)
            self.completed_tasks += 1
            self._queue_size -= 1
            return result
        except:
            return None

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息.

        Returns:
            统计字典
        """
        return {
            "queue_size": self._queue_size,
            "active_workers": len(self.workers),
            "submitted_tasks": self.submitted_tasks,
            "completed_tasks": self.completed_tasks,
        }

    def start(self, daemon: bool = True):
        """启动 Supervisor（在后台线程中运行）.

        Args:
            daemon: 是否作为守护线程

        Returns:
            监控线程对象
        """
        if self._monitor_thread is not None and self._monitor_thread.is_alive():
            self.logger.warning("Supervisor 已经在运行")
            return self._monitor_thread

        # 启动初始水位 Workers
        self.logger.info("=" * 60)
        self.logger.info("🚀 Novel Agent Supervisor 启动")
        self.logger.info("=" * 60)
        self.logger.info(f"最小 Worker 数: {self.min_workers}")
        self.logger.info(f"最大 Worker 数: {self.max_workers}")
        self.logger.info(f"自动扩容: False")
        self.logger.info("=" * 60)

        self.logger.info(f"启动初始水位：{self.min_workers} 个 Worker")
        for _ in range(self.min_workers):
            self.spawn_worker()

        # 创建监控线程
        import threading
        self._stop_event = threading.Event()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="SupervisorMonitor",
            daemon=daemon,
        )
        self._monitor_thread.start()

        self.logger.info(f"Supervisor started in background thread '{self._monitor_thread.name}'")

        return self._monitor_thread

    def _monitor_loop(self):
        """监控循环（在后台线程中运行）."""
        self.logger.info("Monitor loop started")

        while not self._stop_event.is_set():
            # 自愈：检查退出的进程
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
                if pid > 0:
                    worker_id = self.workers.pop(pid, "Unknown")
                    self.logger.warning(f"[!] Master: 进程 {worker_id} (PID: {pid}) 异常退出")
                    # 重启 Worker
                    self.spawn_worker()
            except ChildProcessError:
                pass

            # 监控日志
            stats = self.get_stats()
            self.logger.info(
                f"--- Master 监控: 队列积压 {stats['queue_size']} | "
                f"活跃 Worker {stats['active_workers']} | "
                f"运行时间 {time.time():.0f}s | "
                f"已完成 {stats['completed_tasks']} 任务 ---"
            )

            # 等待 2 秒或直到停止信号
            self._stop_event.wait(timeout=2)

        self.logger.info("Monitor loop exiting")

    def stop(self):
        """停止 Supervisor 和所有 Workers."""
        self.logger.info("Stopping supervisor...")

        # 停止监控线程
        if self._stop_event:
            self._stop_event.set()

        # 等待监控线程结束
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)

        self.logger.info("Monitor thread stopped successfully")

        # 发送停止信号给所有 Workers
        self.logger.info("Sending STOP signals to all workers...")
        for _ in self.workers:
            self.task_queue.put({"command": "STOP"})

        # 等待 Workers 退出
        time.sleep(3)

        # 强制终止还在运行的 Workers
        remaining = len(self.workers)
        if remaining > 0:
            self.logger.warning(f"Force terminating {remaining} remaining workers")
            for pid in list(self.workers.keys()):
                try:
                    os.kill(pid, 9)  # SIGKILL
                except:
                    pass

        self.logger.info("Supervisor shutdown complete")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
