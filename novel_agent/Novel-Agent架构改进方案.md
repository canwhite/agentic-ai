# 🚀 Novel Agent 架构改进方案

## 📊 现状分析

### 当前 novel_agent 架构

**优点：**
- ✅ 完整的多 Agent 协作系统（6 个专业 Agent）
- ✅ 清晰的串行工作流（Director → Plot → Character → Scene → Synthesis → Optimize → QualityCheck）
- ✅ 良好的数据模型设计（Pydantic 模型）

**痛点：**
- ❌ **完全同步阻塞**：每个 Agent 执行时，整个进程被阻塞
- ❌ **单进程执行**：无法并发处理多个小说生成请求
- ❌ **LLM API 等待时间长**：6 个 Agent 串行调用，每个 3-10 秒，总共 18-60 秒
- ❌ **无自愈能力**：进程崩溃需要手动重启
- ❌ **无动态扩容**：无法根据负载调整进程数

### 当前架构代码分析

```python
# 当前执行流程（novel_workflow.py）
def execute(self, novel_input: NovelInput) -> WorkflowResult:
    # 步骤 1: Director 创建计划（阻塞 3-10 秒）
    creation_plan = self._create_creation_plan(...)

    # 步骤 2: 串行执行所有 Agent（阻塞 15-50 秒）
    agent_outputs = self._execute_agent_tasks(...)  # 串行！
    #   - Plot Designer（3-5 秒）
    #   - Character Agent（3-5 秒）
    #   - Scene Renderer（3-5 秒）
    #   - Writing Optimizer（3-5 秒）
    #   - Consistency Checker（3-5 秒）

    # 步骤 3: 合成章节（阻塞 3-10 秒）
    chapter_draft = self._synthesize_chapter(...)

    # 步骤 4: 优化文笔（阻塞 3-10 秒）
    optimized_content = self._optimize_writing(...)

    # 步骤 5: 质量检查（阻塞 3-10 秒）
    quality_ok = self._perform_quality_checks(...)

    # 总耗时：30-90 秒
```

**问题总结：**
1. 每个步骤都是同步阻塞调用
2. 6 个 Agent 串行执行，无法并行
3. 单进程只能处理一个请求
4. 进程崩溃 = 服务不可用

---

## 🎯 改进方案 Plan

### **核心思路：将 Gunicorn + Uvicorn 架构应用到 novel_agent**

将同步的单进程小说生成系统，改造为：
- **多进程（Gunicorn 风格）**：横向扩展，弹性伸缩
- **异步协程（Uvicorn 风格）**：纵向压榨，并发执行
- **智能并行**：识别可并行的 Agent，减少串行等待

---

## 📋 改进计划（按优先级）

### **Phase 1: 基础异步化改造** ⭐⭐⭐⭐⭐

**目标：** 将同步 Agent 改为异步 Agent，利用并发加速单个请求

#### 具体任务

##### 1. 改造 BaseAgent 为异步

**当前代码（base_agent.py）：**
```python
class BaseAgent:
    def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        # 同步调用 LLM
        response = self.llm_client.call(prompt)
        return AgentResult(...)
```

**改造后：**
```python
class BaseAgent:
    async def aexecute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        # 异步调用 LLM
        response = await self.async_llm_client.acall(prompt)
        return AgentResult(...)

    # 保留同步接口（向后兼容）
    def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        return asyncio.run(self.aexecute(task, context))
```

##### 2. 添加异步 LLM Client

**新建文件：`src/utils/async_llm_client.py`**
```python
import httpx
import asyncio
from typing import Dict, Any, Optional

class AsyncLLMClient:
    """异步 LLM 客户端"""

    def __init__(self, provider: str = "deepseek"):
        self.provider = provider
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(300.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )

    async def acall(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """异步调用 LLM API"""

        if self.provider == "deepseek":
            url = "https://api.deepseek.com/v1/chat/completions"
            api_key = os.getenv("DEEPSEEK_API_KEY")

        response = await self.client.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

        return response.json()["choices"][0]["message"]["content"]

    async def aclose(self):
        """关闭客户端"""
        await self.client.aclose()
```

##### 3. 改造 NovelWorkflow 为异步

**关键改动：**
```python
class NovelWorkflow:
    async def aexecute(self, novel_input: NovelInput) -> WorkflowResult:
        """异步执行小说生成工作流"""

        # 步骤 1: Director 创建计划（异步）
        creation_plan = await self._async_create_creation_plan(...)

        # 步骤 2: 并行执行 Agent（关键优化！）
        agent_outputs = await self._async_execute_agent_tasks(...)

        # 步骤 3-5: 后续步骤（异步）
        chapter_draft = await self._async_synthesize_chapter(...)
        optimized_content = await self._async_optimize_writing(...)
        quality_ok = await self._async_perform_quality_checks(...)

        return result

    async def _async_execute_agent_tasks(
        self,
        novel_input: NovelInput,
        creation_plan: Dict[str, Any],
        result: WorkflowResult,
    ) -> Dict[str, Any]:
        """异步执行 Agent 任务（支持并行）"""

        agent_outputs = {}

        # Level 1: Plot（必须先执行）
        plot_result = await self.plot_designer.aexecute(...)
        agent_outputs["plot_designer"] = plot_result

        # Level 2: Character + Scene（可以并行！）
        character_task = self.character_agent.aexecute(...)
        scene_task = self.scene_renderer.aexecute(...)

        # 并行等待
        character_result, scene_result = await asyncio.gather(
            character_task,
            scene_task,
            return_exceptions=True
        )

        agent_outputs["character_agent"] = character_result
        agent_outputs["scene_renderer"] = scene_result

        return agent_outputs
```

##### 4. 使用 asyncio.gather() 并行执行

**并行策略：**
```python
# 场景 1: Character 和 Scene 可以并行
async def parallel_level_3(self, context):
    tasks = [
        self.character_agent.aexecute("设计人物表现", context),
        self.scene_renderer.aexecute("设计场景渲染", context),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# 场景 2: Writing Optimization 和 Quality Check 可以并行
async def parallel_level_5(self, content, context):
    optimize_task = self.writing_optimizer.aexecute("优化文笔", context)
    quality_task = self.consistency_checker.aexecute("质量检查", context)

    optimized, quality = await asyncio.gather(
        optimize_task,
        quality_task,
        return_exceptions=True
    )

    return optimized, quality
```

#### 预期收益

| 指标 | 改造前 | 改造后 | 提升 |
|------|--------|--------|------|
| 单个请求延迟 | 60 秒 | 20 秒 | **3 倍** |
| 并发处理数 | 1 个 | 5 个（协程） | **5 倍** |
| LLM API 调用 | 串行 | 部分并行 | **2 倍** |

---

### **Phase 2: Master-Worker 多进程架构** ⭐⭐⭐⭐

**目标：** 引入 Gunicorn 风格的 Master-Worker 模式

#### 具体任务

##### 1. 实现 NovelSupervisor（Master 进程）

**新建文件：`src/supervisor/novel_supervisor.py`**
```python
import os
import time
import signal
import multiprocessing
from typing import Dict, Optional

class NovelSupervisor:
    """小说生成系统的 Master 进程"""

    def __init__(self, min_workers: int = 2, max_workers: int = 4):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.workers: Dict[int, str] = {}  # {pid: worker_name}

    def spawn_worker(self):
        """Fork 一个新的 Worker 进程"""
        if len(self.workers) >= self.max_workers:
            return

        worker_id = f"Worker-{len(self.workers) + 1}"
        pid = os.fork()

        if pid == 0:
            # 子进程（Worker）
            self._run_worker(worker_id)
            os._exit(0)
        else:
            # 父进程（Master）
            self.workers[pid] = worker_id
            print(f"[Master] 启动 Worker: {worker_id} (PID: {pid})")

    def _run_worker(self, worker_id: str):
        """Worker 进程的主循环"""
        import asyncio
        from src.workflows.novel_workflow import NovelWorkflow

        # 每个 Worker 内部运行 asyncio 事件循环
        workflow = NovelWorkflow()

        async def worker_loop():
            print(f"  [{worker_id}] (PID: {os.getpid()}) 异步 Worker 启动")

            active_tasks = []

            while True:
                try:
                    # 非阻塞获取任务
                    try:
                        task = self.task_queue.get_nowait()
                    except:
                        await asyncio.sleep(0.5)
                        continue

                    if task == "STOP":
                        break

                    # 创建异步任务
                    novel_input = task["novel_input"]
                    task_id = task["task_id"]

                    # 异步执行小说生成
                    t = asyncio.create_task(
                        self._process_task(workflow, novel_input, task_id)
                    )
                    active_tasks.append(t)

                    # 清理已完成的任务
                    active_tasks = [t for t in active_tasks if not t.done()]

                    print(f"    [{worker_id}] 当前并发任务数: {len(active_tasks)}")

                except Exception as e:
                    print(f"  [{worker_id}] 错误: {e}")

        asyncio.run(worker_loop())

    async def _process_task(self, workflow, novel_input, task_id):
        """处理单个任务"""
        try:
            result = await workflow.aexecute(novel_input)

            # 将结果放入结果队列
            self.result_queue.put({
                "task_id": task_id,
                "success": result.success,
                "chapter_content": result.chapter_result.content if result.chapter_result else None,
                "execution_time": result.execution_time,
            })

            print(f"    [Task {task_id}] 完成，耗时 {result.execution_time:.2f}s")

        except Exception as e:
            self.result_queue.put({
                "task_id": task_id,
                "success": False,
                "error": str(e),
            })

    def monitor(self):
        """Master 监控循环"""
        # 初始水位：启动最小数量的 Worker
        for _ in range(self.min_workers):
            self.spawn_worker()

        try:
            while True:
                # 模拟任务提交
                for _ in range(random.randint(0, 2)):
                    task = {
                        "task_id": f"task-{random.randint(1000, 9999)}",
                        "novel_input": self._create_sample_input(),
                    }
                    self.task_queue.put(task)

                # 弹性伸缩逻辑
                queue_size = self.task_queue.qsize()
                current_workers = len(self.workers)

                if queue_size > 10 and current_workers < self.max_workers:
                    print(f"[Master] 队列积压 {queue_size}，扩容 Worker")
                    self.spawn_worker()

                # 自愈逻辑：检查退出的 Worker
                try:
                    pid, status = os.waitpid(-1, os.WNOHANG)
                    if pid > 0:
                        worker_name = self.workers.pop(pid, "Unknown")
                        print(f"[Master] Worker {worker_name} (PID: {pid}) 挂了，正在重启...")
                        self.spawn_worker()
                except ChildProcessError:
                    pass

                # 处理结果队列
                while not self.result_queue.empty():
                    result = self.result_queue.get()
                    print(f"[Master] 任务完成: {result['task_id']}")

                print(f"--- [Master] 队列: {queue_size} | Worker: {current_workers} ---")
                time.sleep(2)

        except KeyboardInterrupt:
            print("[Master] 正在关闭...")
            # 发送停止信号给所有 Worker
            for _ in range(len(self.workers)):
                self.task_queue.put("STOP")

    def _create_sample_input(self):
        """创建示例输入"""
        from src.models import NovelInput

        return NovelInput(
            overall_outline="一个少年在玄幻世界修炼成神的故事",
            chapter_outline="主角在秘境中意外获得上古传承",
            genre="玄幻",
        )
```

##### 2. 任务队列系统

**使用 Redis 实现分布式队列（可选）：**
```python
import redis.asyncio as aioredis
import json

class RedisTaskQueue:
    """基于 Redis 的异步任务队列"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        """连接 Redis"""
        self.redis = await aioredis.from_url(self.redis_url)

    async def submit_task(self, novel_input: NovelInput, priority: int = 0) -> str:
        """提交任务到队列"""
        task_id = f"task-{uuid.uuid4()}"

        task_data = {
            "task_id": task_id,
            "novel_input": novel_input.dict(),
            "priority": priority,
            "status": "pending",
            "created_at": time.time(),
        }

        # 根据优先级放入不同的队列
        queue_name = f"tasks:priority_{priority}"
        await self.redis.lpush(queue_name, json.dumps(task_data))

        return task_id

    async def get_task(self) -> Optional[Dict]:
        """从队列获取任务（非阻塞）"""
        # 从高优先级队列开始检查
        for priority in range(10):
            queue_name = f"tasks:priority_{priority}"
            task_data = await self.redis.rpop(queue_name)

            if task_data:
                return json.loads(task_data)

        return None

    async def update_task_status(self, task_id: str, status: str, result: Dict = None):
        """更新任务状态"""
        key = f"task:{task_id}"
        await self.redis.hset(key, "status", status)

        if result:
            await self.redis.hset(key, "result", json.dumps(result))

    async def get_task_status(self, task_id: str) -> Dict:
        """获取任务状态"""
        key = f"task:{task_id}"
        data = await self.redis.hgetall(key)

        return {
            "task_id": task_id,
            "status": data.get(b"status", b"unknown").decode(),
            "result": json.loads(data.get(b"result", b"{}").decode()),
        }
```

##### 3. 启动脚本

**新建文件：`scripts/start_novel_cluster.py`**
```python
#!/usr/bin/env python3
"""
启动 Novel Agent 集群
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.supervisor.novel_supervisor import NovelSupervisor

if __name__ == "__main__":
    supervisor = NovelSupervisor(
        min_workers=2,  # 最小 2 个 Worker
        max_workers=4,  # 最大 4 个 Worker
    )

    print("=" * 60)
    print("🚀 Novel Agent 集群启动")
    print("=" * 60)
    print(f"最小 Worker 数: {supervisor.min_workers}")
    print(f"最大 Worker 数: {supervisor.max_workers}")
    print("=" * 60)

    try:
        supervisor.monitor()
    except KeyboardInterrupt:
        print("\n👋 Novel Agent 集群已关闭")
```

#### 预期收益

| 指标 | 改造前 | 改造后 | 提升 |
|------|--------|--------|------|
| 进程数 | 1 个 | 2-4 个（动态） | **弹性伸缩** |
| 并发处理数 | 1 个 | 10-20 个（4 进程 × 5 协程） | **20 倍** |
| 系统可用性 | 崩溃需手动重启 | 自动自愈 | **99.9%** |
| 系统吞吐 | 1 QPS | 20 QPS | **20 倍** |

---

### **Phase 3: 写作类 Agent 的特殊优化** ⭐⭐⭐⭐⭐

**目标：** 针对小说生成的特点，优化执行顺序和并发策略

#### 关键洞察：写作类 Agent 的依赖关系

```
当前执行顺序（完全串行）：
Director → Plot → Character → Scene → Synthesis → Optimize → QualityCheck

问题：很多步骤其实可以并行！
```

#### 优化后的执行顺序（DAG 依赖图）

```
Level 1: Director（制定计划）
         ↓
Level 2: Plot（情节设计，必选）
         ↓
Level 3: Character + Scene（可以并行！）
         ├→ Character Agent（人物表现）
         └→ Scene Agent（场景渲染）
         ↓
Level 4: Synthesis（合成章节）
         ↓
Level 5: Optimize + QualityCheck（可以并行！）
         ├→ Writing Optimizer（文笔优化）
         └→ Consistency Checker（连贯性检查）
         ↓
Level 6: Final Result（如果有问题，修复）
```

#### 具体优化策略

##### 1. Level 3 并行化（Character + Scene）

```python
async def _async_execute_agent_tasks_level_3(
    self,
    novel_input: NovelInput,
    creation_plan: Dict[str, Any],
    result: WorkflowResult,
) -> Dict[str, Any]:
    """Level 3: 并行执行 Character 和 Scene Agent"""

    context = {
        "novel_input": novel_input,
        "creation_plan": creation_plan,
        "plot_output": plot_output,  # Level 2 的输出
    }

    # 并行启动两个 Agent
    character_task = asyncio.create_task(
        self.character_agent.aexecute("设计人物表现和对话", context)
    )
    scene_task = asyncio.create_task(
        self.scene_renderer.aexecute("设计场景渲染", context)
    )

    # 并行等待
    character_result, scene_result = await asyncio.gather(
        character_task,
        scene_task,
        return_exceptions=True
    )

    # 处理结果
    agent_outputs = {}
    if not isinstance(character_result, Exception):
        agent_outputs["character_agent"] = character_result
    if not isinstance(scene_result, Exception):
        agent_outputs["scene_renderer"] = scene_result

    return agent_outputs
```

##### 2. Level 5 并行化（Optimize + QualityCheck）

```python
async def _async_optimize_and_check(
    self,
    novel_input: NovelInput,
    chapter_content: str,
    result: WorkflowResult,
) -> tuple:
    """Level 5: 并行执行优化和质检"""

    # 准备两个任务
    optimize_task = asyncio.create_task(
        self.writing_optimizer.aexecute("优化文笔", {
            "novel_input": novel_input,
            "text": chapter_content,
        })
    )

    quality_task = asyncio.create_task(
        self.consistency_checker.aexecute("质量检查", {
            "novel_input": novel_input,
            "chapter_content": chapter_content,
        })
    )

    # 并行执行
    optimized_result, quality_result = await asyncio.gather(
        optimize_task,
        quality_task,
        return_exceptions=True
    )

    # 处理结果
    if not isinstance(optimized_result, Exception):
        optimized_content = optimized_result.content
    else:
        optimized_content = chapter_content  # 失败则使用原文

    quality_ok = True
    if not isinstance(quality_result, Exception):
        # 解析质检结果
        score = quality_result.metadata.get("coherence_score", 0)
        quality_ok = score >= 70

    return optimized_content, quality_ok
```

##### 3. 流式生成（Streaming Generation）

**添加 FastAPI 接口：**
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/api/novel/generate/stream")
async def generate_chapter_stream(request: NovelInput):
    """流式生成小说章节"""

    async def generate():
        # Step 1: 生成计划（快速）
        yield f"data: {{'step': 'plan', 'status': 'started'}}\n\n"

        creation_plan = await director.aexecute("制定计划", {...})
        yield f"data: {{'step': 'plan', 'status': 'completed'}}\n\n"

        # Step 2: 生成情节（流式）
        yield f"data: {{'step': 'plot', 'status': 'started'}}\n\n"

        async for chunk in plot_designer.aexecute_stream(...):
            yield f"data: {{'step': 'plot', 'chunk': '{chunk}'}}\n\n"

        yield f"data: {{'step': 'plot', 'status': 'completed'}}\n\n"

        # ... 其他步骤

    return StreamingResponse(generate(), media_type="text/event-stream")
```

**用户体验提升：**
- 3 秒内看到第一批内容
- 不用等 60 秒才看到完整结果
- 类似 ChatGPT 的流式体验

##### 4. 预取策略（Prefetching）

```python
class NovelPrefetcher:
    """预取管理器"""

    def __init__(self):
        self.cache = {}

    async def prefetch_context(self, user_id: str, novel_input: NovelInput):
        """预取可能需要的上下文"""

        # 根据用户历史，预测可能的场景
        user_history = await self.get_user_history(user_id)

        # 预加载常用场景
        common_scenes = ["战斗场景", "对话场景", "修炼场景"]
        for scene_name in common_scenes:
            if scene_name not in self.cache:
                scene_template = await self.load_scene_template(scene_name)
                self.cache[scene_name] = scene_template

        # 预加载角色对话风格
        for character in novel_input.characters:
            if character.name not in self.cache:
                dialogue_style = await self.load_dialogue_style(character.name)
                self.cache[character.name] = dialogue_style

    async def get_prefetched_data(self, key: str):
        """获取预取的数据"""
        return self.cache.get(key)
```

#### 预期收益

| 指标 | Phase 2 | Phase 3 | 提升 |
|------|---------|---------|------|
| 单个请求延迟 | 20 秒 | 12 秒 | **1.7 倍** |
| 首字延迟（TTFB） | 12 秒 | 3 秒 | **4 倍** |
| 用户满意度 | 70% | 95% | **1.4 倍** |

---

### **Phase 4: 生产环境增强** ⭐⭐⭐

**目标：** 生产级别的稳定性、可观测性和可扩展性

#### 具体任务

##### 1. 添加 FastAPI 接口层

**新建文件：`src/api/novel_api.py`**
```python
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.models import NovelInput
from src.supervisor.novel_supervisor import NovelSupervisor

app = FastAPI(
    title="Novel Agent API",
    description="高性能异步小说生成系统",
    version="2.0",
)

# 全局 Supervisor 实例
supervisor = NovelSupervisor(min_workers=2, max_workers=4)

class GenerateRequest(BaseModel):
    novel_input: NovelInput
    priority: int = 0  # 0-9，9 最高

class GenerateResponse(BaseModel):
    task_id: str
    status: str
    message: str

@app.on_event("startup")
async def startup():
    """应用启动时初始化"""
    # 启动 Master 进程监控（后台任务）
    import asyncio
    asyncio.create_task(supervisor_monitor())

@app.post("/api/novel/generate", response_model=GenerateResponse)
async def generate_chapter(request: GenerateRequest, background_tasks: BackgroundTasks):
    """提交小说生成任务"""

    # 提交任务到队列
    task_id = await supervisor.submit_task(
        novel_input=request.novel_input,
        priority=request.priority,
    )

    return GenerateResponse(
        task_id=task_id,
        status="pending",
        message="任务已提交，请稍后查询结果",
    )

@app.get("/api/novel/status/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""

    status = await supervisor.get_task_status(task_id)

    if not status:
        raise HTTPException(status_code=404, detail="任务不存在")

    return JSONResponse(content=status)

@app.get("/api/novel/result/{task_id}")
async def get_task_result(task_id: str):
    """获取任务结果"""

    result = await supervisor.get_task_result(task_id)

    if not result:
        raise HTTPException(status_code=404, detail="任务不存在")

    if result["status"] == "completed":
        return {
            "task_id": task_id,
            "status": "completed",
            "chapter_content": result["chapter_content"],
            "execution_time": result["execution_time"],
        }
    else:
        return {"task_id": task_id, "status": result["status"]}

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "workers": len(supervisor.workers),
        "queue_size": supervisor.task_queue.qsize(),
    }

@app.get("/api/metrics")
async def get_metrics():
    """获取系统指标"""
    stats = supervisor.get_execution_stats()

    return {
        "total_executions": stats["total_executions"],
        "success_rate": stats["success_rate"],
        "avg_execution_time": stats["avg_execution_time"],
        "active_workers": len(supervisor.workers),
        "queue_size": supervisor.task_queue.qsize(),
    }
```

##### 2. 引入 Redis

**使用 Redis 实现分布式锁和缓存：**
```python
import redis.asyncio as aioredis
import uuid

class RedisDistributedLock:
    """分布式锁"""

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def acquire(self, lock_name: str, expire_time: int = 60) -> str:
        """获取锁"""
        lock_id = str(uuid.uuid4())
        acquired = await self.redis.set(
            f"lock:{lock_name}",
            lock_id,
            nx=True,  # 仅当 key 不存在时设置
            ex=expire_time,  # 过期时间
        )

        return lock_id if acquired else None

    async def release(self, lock_name: str, lock_id: str):
        """释放锁"""
        # 使用 Lua 脚本确保原子性
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        await self.redis.eval(script, 1, f"lock:{lock_name}", lock_id)

# 使用示例
async def generate_with_lock(novel_input: NovelInput):
    redis = await aioredis.from_url("redis://localhost:6379")
    lock = RedisDistributedLock(redis)

    # 防止重复任务
    task_hash = hashlib.md5(json.dumps(novel_input.dict()).encode()).hexdigest()
    lock_id = await lock.acquire(f"generate:{task_hash}")

    if not lock_id:
        return {"error": "任务正在执行中"}

    try:
        result = await workflow.aexecute(novel_input)
        return result
    finally:
        await lock.release(f"generate:{task_hash}", lock_id)
```

##### 3. 监控和日志

**添加 Prometheus 指标：**
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# 定义指标
request_counter = Counter(
    "novel_generation_requests_total",
    "Total number of novel generation requests",
    ["status"]
)

execution_time_histogram = Histogram(
    "novel_generation_duration_seconds",
    "Novel generation execution time",
    buckets=[1, 5, 10, 20, 30, 60, 120]
)

active_workers_gauge = Gauge(
    "novel_active_workers",
    "Number of active workers"
)

queue_size_gauge = Gauge(
    "novel_queue_size",
    "Number of tasks in queue"
)

# 使用示例
@execution_time_histogram.time()
async def generate_with_metrics(novel_input: NovelInput):
    start_time = time.time()

    try:
        result = await workflow.aexecute(novel_input)
        request_counter.labels(status="success").inc()
        return result
    except Exception as e:
        request_counter.labels(status="error").inc()
        raise
```

**结构化日志：**
```python
import structlog

logger = structlog.get_logger()

async def generate_with_logging(novel_input: NovelInput):
    logger.info(
        "novel_generation_started",
        genre=novel_input.genre,
        chapter_outline=novel_input.chapter_outline,
    )

    try:
        result = await workflow.aexecute(novel_input)

        logger.info(
            "novel_generation_completed",
            execution_time=result.execution_time,
            chapter_length=len(result.chapter_result.content),
        )

        return result

    except Exception as e:
        logger.error(
            "novel_generation_failed",
            error=str(e),
            genre=novel_input.genre,
        )
        raise
```

##### 4. Nginx 反向代理配置

**新建文件：`nginx.conf`**
```nginx
upstream novel_backend {
    least_conn;  # 最少连接负载均衡

    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    server 127.0.0.1:8004;

    keepalive 32;
}

server {
    listen 80;
    server_name novel.example.com;

    # 限流配置
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://novel_backend;
        proxy_http_version 1.1;

        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Connection "";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 300s;  # 5 分钟（因为 LLM 调用慢）

        # Chunked transfer encoding（支持流式）
        proxy_buffering off;
    }

    # 健康检查
    location /api/health {
        proxy_pass http://novel_backend/api/health;
        access_log off;
    }
}
```

#### 预期收益

| 指标 | Phase 3 | Phase 4 | 提升 |
|------|---------|---------|------|
| 并发用户数 | 50 | 1000+ | **20 倍** |
| 系统可用性 | 95% | 99.9% | **1.05 倍** |
| 可观测性 | 无 | 完整监控 | **✓** |
| 分布式支持 | 单机 | 支持集群 | **✓** |

---

## 🎯 总结：完整改进路线图

### 改进阶段对比

| Phase | 核心改动 | 难度 | 收益 | 优先级 | 预计工期 |
|-------|---------|------|------|--------|---------|
| **Phase 1** | 同步 → 异步 | ⭐⭐⭐ | **3 倍性能提升** | ⭐⭐⭐⭐⭐ | 2-3 天 |
| **Phase 2** | 单进程 → 多进程 | ⭐⭐⭐⭐ | **弹性伸缩 + 自愈** | ⭐⭐⭐⭐ | 3-4 天 |
| **Phase 3** | 完全串行 → 智能并行 | ⭐⭐⭐⭐⭐ | **再提升 1.7 倍** | ⭐⭐⭐⭐⭐ | 4-5 天 |
| **Phase 4** | 开发 → 生产级 | ⭐⭐⭐ | **高可用 + 可观测** | ⭐⭐⭐ | 3-4 天 |

### 性能提升预期

```
改造前：
- 单进程同步
- 60 秒/请求
- 1 QPS
- 崩溃需手动重启

↓ Phase 1 (异步化)

- 单进程异步（5 协程）
- 20 秒/请求
- 5 QPS
- 崩溃需手动重启

↓ Phase 2 (多进程)

- 4 进程异步（4 × 5 协程）
- 20 秒/请求
- 20 QPS
- 自动自愈

↓ Phase 3 (智能并行)

- 4 进程异步（智能并行）
- 12 秒/请求
- 33 QPS
- 自动自愈 + 流式返回

↓ Phase 4 (生产级)

- 4 进程异步（生产级）
- 12 秒/请求
- 1000+ 并发用户
- 99.9% 可用性 + 完整监控
```

---

## 💡 立即可做的 Quick Win

### Quick Win 1: 改造一个 Agent（1 小时）

```python
# Step 1: 改造 CharacterAgent
class CharacterAgent(BaseAgent):
    async def aexecute(self, task: str, context: Dict) -> AgentResult:
        prompt = self._build_prompt(task, context)
        response = await self.async_llm_client.acall(prompt)
        return self._parse_response(response)

# Step 2: 测试
import asyncio

agent = CharacterAgent(llm_provider="deepseek")
result = asyncio.run(agent.aexecute("设计人物对话", {...}))
print(result.content)
```

### Quick Win 2: 并行执行两个 Agent（2 小时）

```python
async def parallel_agents():
    character_task = character_agent.aexecute(...)
    scene_task = scene_renderer.aexecute(...)

    character_result, scene_result = await asyncio.gather(
        character_task,
        scene_task
    )

    return character_result, scene_result

# 测试
results = asyncio.run(parallel_agents())
```

### Quick Win 3: 添加简单的 Master-Worker（3 小时）

```python
# 启动脚本
supervisor = NovelSupervisor(min_workers=2, max_workers=4)

# 提交任务
supervisor.task_queue.put({
    "task_id": "test-001",
    "novel_input": NovelInput(...),
})

# 启动监控
supervisor.monitor()
```

**预期结果：**
- 性能提升 **5-10 倍**
- 可以同时处理多个小说生成请求
- 系统具备基本的自愈能力

---

## 📖 参考资料

### 技术文档
- [Gunicorn 官方文档](https://docs.gunicorn.org/)
- [Uvicorn 官方文档](https://www.uvicorn.org/)
- [FastAPI 异步编程指南](https://fastapi.tiangolo.com/async/)
- [Python asyncio 官方文档](https://docs.python.org/3/library/asyncio.html)

### 架构模式
- [Master-Worker 模式](https://en.wikipedia.org/wiki/Master-worker)
- [Pre-fork 模型](https://httpd.apache.org/docs/2.4/en/prefork.html)
- [异步 I/O 模型](https://en.wikipedia.org/wiki/Asynchronous_I/O)

### 生产实践
- [Redis 任务队列最佳实践](https://redis.io/topics/lru-cache)
- [Nginx 负载均衡配置](https://docs.nginx.com/nginx/admin-guide/load-balancer/)
- [Prometheus 监控实践](https://prometheus.io/docs/practices/)

---

## 🎓 总结

这个改进方案的核心思想是：

1. **Phase 1（异步化）**：从同步阻塞改为异步非阻塞，提升单个请求的性能
2. **Phase 2（多进程）**：引入 Master-Worker 模式，实现横向扩展和高可用
3. **Phase 3（智能并行）**：识别可并行的 Agent，进一步优化性能
4. **Phase 4（生产级）**：添加监控、日志、负载均衡等生产特性

**最终目标：**
- 从 **60 秒/请求** 优化到 **12 秒/请求**（5 倍提升）
- 从 **1 QPS** 提升到 **33 QPS**（33 倍提升）
- 从 **手动重启** 升级到 **自动自愈**（99.9% 可用性）
- 从 **单机** 扩展到 **可分布式部署**（支持 1000+ 并发用户）

---

**开始行动吧！** 🚀

建议从 **Phase 1** 开始，先完成异步化改造，验证效果后再进行后续优化。
