现在我们要把 多进程（Multiprocessing）、自愈能力、动态扩容 与 异步 I/O (Uvicorn/Asyncio) 全部打通。
在这个终极架构中，每一个被 fork 出来的子进程不再是简单的同步脚本，而是一个异步的微服务单元。
1. 终极架构逻辑：混合模型
 * Master (多进程层)：负责 CPU 级别的弹性伸缩。如果任务太多，就 Fork 新进程。
 * Worker (异步 I/O 层)：每个进程内部跑一个 asyncio 事件循环。这使得一个 Agent 进程在等待 LLM API 返回时，可以同时处理该进程内的多个子任务。
2. 混合架构实现代码
为了实现这个功能，我们需要在子进程中使用 asyncio.run() 启动异步循环。



import os
import sys
import time
import signal
import multiprocessing
import asyncio
import random

# --- 1. 异步 Agent 逻辑 (每一个子进程内部的灵魂) ---

async def async_task_handler(agent_name, task_id):
    """模拟一个异步处理过程，比如调用大模型 API"""
    wait_time = random.uniform(1, 4)
    print(f"    [协程] {agent_name} 开始异步处理 {task_id} (预计等待 {wait_time:.1f}s)")
    await asyncio.sleep(wait_time) # 关键：非阻塞等待
    return f"{task_id} 完成"

async def async_worker_loop(name, queue):
    """子进程内部的事件循环：一个进程同时接多个活"""
    print(f"  [+] {name} (PID: {os.getpid()}) 异步 Worker 启动")
    
    active_tasks = [] # 记录正在进行的异步任务

    while True:
        try:
            # 尝试获取新任务，非阻塞模式
            try:
                # 在异步环境下，我们使用非阻塞方式检查跨进程队列
                # 实际生产中常用 loop.run_in_executor 处理这个阻塞动作
                task = queue.get_nowait() 
            except:
                task = None
                await asyncio.sleep(0.5) # 没任务，歇半秒

            if task is None:
                continue
            
            if task == "STOP": # 收到退出指令
                break

            # 启动一个异步任务，但不等待它结束（立刻去接下一个任务）
            t = asyncio.create_task(async_task_handler(name, task))
            active_tasks.append(t)
            
            # 清理已完成的任务，行列推导式
            active_tasks = [t for t in active_tasks if not t.done()]
            print(f"    [状态] {name} 当前并发协程数: {len(active_tasks)}")

        except Exception as e:
            print(f"子进程错误: {e}")
            break

# --- 2. Master 进程管理层 (外置管理器) ---

def start_worker_process(name, queue):
    """子进程入口点"""
    asyncio.run(async_worker_loop(name, queue))
    os._exit(0)

class UltimateSupervisor:
    def __init__(self, min_p=2, max_p=4):
        self.queue = multiprocessing.Queue()
        self.workers = {} # {pid: name}
        self.min_p = min_p
        self.max_p = max_p

    def spawn(self):
        if len(self.workers) >= self.max_p: return
        name = f"Agent-{random.randint(10,99)}"
        pid = os.fork()
        if pid == 0:
            start_worker_process(name, self.queue)
        else:
            self.workers[pid] = name
            print(f"[*] Master: 扩容进程 -> {name} (PID: {pid})")

    def monitor(self):
        # 初始水位
        for _ in range(self.min_p): self.spawn()

        try:
            while True:
                # 模拟海量任务涌入
                for _ in range(random.randint(0, 3)):
                    self.queue.put(f"REQ-{random.randint(1000, 9999)}")

                q_size = self.queue.qsize()
                curr_p = len(self.workers)

                # 弹性伸缩逻辑
                if q_size > 10 and curr_p < self.max_p:
                    self.spawn()
                
                # 自愈逻辑：非阻塞检查退出的进程
                try:
                    pid, status = os.waitpid(-1, os.WNOHANG)
                    if pid > 0:
                        name = self.workers.pop(pid, "Unknown")
                        print(f"[!] Master: 进程 {name} 挂了，正在拉起新进程自愈...")
                        self.spawn()
                except ChildProcessError:
                    pass

                print(f"--- Master 监控: 队列积压 {q_size} | 活跃进程 {len(self.workers)} ---")
                time.sleep(2)
        except KeyboardInterrupt:
            print("正在关闭...")

if __name__ == "__main__":
    supervisor = UltimateSupervisor()
    supervisor.monitor()

3. 这个架构为什么能打？
 * 为什么引入 Uvicorn/Asyncio 后更强？
   在之前的“自愈多进程”版中，一个进程一旦执行 time.sleep()，它就彻底死掉了，什么也干不了。引入 asyncio 后，一个进程可以变成**“并发中心”**。它能一边等待 API 返回，一边通过 queue.get_nowait() 持续接收新任务。
 * Uvicorn 的角色是什么？
   如果你把上面的 async_worker_loop 换成真正的 uvicorn.run(app)，你的每一个子进程就会变成一个独立的 HTTP 服务器节点。Master 进程就像一个 Local Load Balancer（本地负载均衡器）。
 * 对顺序任务的终极优化：
   * 横向：Master 通过多进程横向扩展（解决 CPU 瓶颈）。
   * 纵向：Uvicorn/Asyncio 通过协程纵向压榨（解决 I/O 等待瓶颈）。
总结
你现在拥有的这套思路，就是 工业级分布式系统 的缩影：
 * PHP-FPM 给了你“外置管理和稳定性”的启示。
 * Gunicorn 给了你“Pre-fork 和 Master-Worker”的结构。
 * Uvicorn 给了你“异步非阻塞”的性能。
 * Multi-Agent 则是这些技术在 AI 时代最实用的落地场景。
至此，你已经从理解“PHP 为什么外置”进化到了“如何亲手设计一个现代高性能 Agent 集群”。对于这套架构，你是否想了解如何给它加上一个 Nginx 反向代理层，让它真正变成一个可以对外提供服务的 API 平台？x