# 故障排查文档

本文档记录了 Novel Agent 项目开发和测试过程中遇到的主要问题及其解决方案。

## 目录

- [项目导入路径说明](#项目导入路径说明)
- [Scene 模型验证错误](#scene-模型验证错误)
- [NovelInput 导入路径不一致问题](#novelinput-导入路径不一致问题)
- [Pydantic 模型 JSON 序列化失败](#pydantic-模型-json-序列化失败)
- [NovelInput 字段访问错误](#novelinput-字段访问错误)

---

## 项目导入路径说明

### 为什么使用 `from src.utils import`？

在 Novel Agent 项目中，你可能注意到这样的导入语句：

```python
# src/agents/base_agent.py
from src.utils import get_llm_client, config

# examples/basic_usage.py
from src.models import NovelInput, Character, Scene
```

#### 项目采用 src 布局

Novel Agent 使用现代 Python 项目的**标准 src 布局**：

```
novel_agent/
├── src/                    # 源代码目录（包根目录）
│   ├── __init__.py
│   ├── agents/
│   ├── models/
│   ├── utils/              # 工具模块
│   └── workflows/
├── examples/
├── tests/
└── pyproject.toml
```

#### 绝对导入 vs 相对导入

**❌ 不推荐的相对导入：**
```python
from ..utils import get_llm_client  # 容易出错
from .models import NovelInput       # 路径依赖
```

**✅ 推荐的绝对导入：**
```python
from src.utils import get_llm_client, config
from src.models import NovelInput, Character, Scene
```

#### 绝对导入的优势

| 优势 | 说明 |
|------|------|
| **一致性** | 无论在项目哪个位置，导入路径都相同 |
| **可读性** | 清楚表明导入的是项目内部模块 |
| **可维护性** | 重构时不会影响导入路径 |
| **避免循环导入** | 绝对导入更容易发现和避免循环依赖 |
| **IDE 支持** | 更好的代码导航和自动补全 |
| **类型检查** | mypy 等工具能正确识别类型 |

#### Python 如何找到 src 模块？

**方法 1：通过 pyproject.toml 配置**

```toml
[tool.hatch.build.targets.wheel]
packages = ["src"]  # 声明 src 为包根目录
```

**方法 2：在 examples 脚本中动态添加**

```python
# examples/basic_usage.py
import sys
from pathlib import Path

# 将 src 目录添加到 Python 路径
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# 现在可以使用 from src.xxx import
from src.models import NovelInput
from src.workflows.novel_workflow import NovelWorkflow
```

**`sys.path.insert(0, str(src_dir))` 详解：**

```python
sys.path.insert(0, str(src_dir))
#           ↑  ↑
#           │  └─ 要插入的路径（转换为字符串）
#           └─ 插入位置（0 = 列表开头，最高优先级）
```

- **`sys.path`**：Python 模块搜索路径的列表
- **`insert(0, path)`**：在列表开头插入路径
- **参数 `0` 的作用**：让 `src` 目录的优先级最高，优先在此目录查找模块

**sys.path 工作原理：**

```python
# sys.path 是一个列表，包含所有模块搜索路径
import sys
print(sys.path)
# 输出示例：
# [
#   '/Users/zack/Desktop/agentic-ai/novel_agent/src',  # ← 我们添加的（位置 0）
#   '/usr/local/lib/python310.zip',
#   '/usr/local/lib/python3.10',
#   '/usr/local/lib/python3.10/lib-dynload',
#   ...
# ]

# Python 按顺序搜索模块：
# 1. 先搜索 sys.path[0]
# 2. 然后搜索 sys.path[1]
# 3. 以此类推...
```

**为什么使用 `insert(0, ...)` 而不是 `append(...)`？**

```python
# ❌ 使用 append（不推荐）
sys.path.append(str(src_dir))
# sys.path 变成：
# [..., ..., ..., '/path/to/src']  # 在末尾，优先级最低
# 问题：如果系统其他位置有同名模块，会优先加载系统的

# ✅ 使用 insert(0, ...)（推荐）
sys.path.insert(0, str(src_dir))
# sys.path 变成：
# ['/path/to/src', ..., ..., ...]  # 在开头，优先级最高
# 优势：确保项目的 src 模块优先被找到
```

**实际例子：**

假设项目结构：
```
novel_agent/
├── src/
│   └── models/
│       └── novel_input.py  # 我们的 NovelInput 类
└── examples/
    └── basic_usage.py
```

```python
# examples/basic_usage.py
import sys
from pathlib import Path

# 不添加 sys.path 时
# from models import NovelInput  # ❌ ModuleNotFoundError: No module named 'models'
# from src.models import NovelInput  # ❌ ModuleNotFoundError: No module named 'src'

# 添加后
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# 现在可以导入
from src.models import NovelInput  # ✅ 成功！
```

**`Path(__file__)` 详解：**

```python
# __file__ 是当前脚本的完整路径
# 假设当前文件：/Users/zack/Desktop/agentic-ai/novel_agent/examples/basic_usage.py

Path(__file__)
# => PosixPath('/Users/zack/Desktop/agentic-ai/novel_agent/examples/basic_usage.py')

Path(__file__).parent
# => PosixPath('/Users/zack/Desktop/agentic-ai/novel_agent/examples')

Path(__file__).parent.parent
# => PosixPath('/Users/zack/Desktop/agentic-ai/novel_agent')

Path(__file__).parent.parent / "src"
# => PosixPath('/Users/zack/Desktop/agentic-ai/novel_agent/src')

str(Path(__file__).parent.parent / "src")
# => '/Users/zack/Desktop/agentic-ai/novel_agent/src'
```

**方法 3：以可编辑模式安装项目**

```bash
# 开发模式安装
pip install -e .

# 或者使用 uv
uv pip install -e .
```

安装后，`src` 成为顶层包，可以在任何地方使用 `from src.xxx import`。

#### 与之前修复的导入问题对比

**❌ 问题代码（导致 isinstance 失败）：**
```python
# examples/basic_usage.py
from models.novel_input import NovelInput  # 路径不明确

# src/agents/director.py
from src.models import NovelInput

# 结果：两个导入指向不同的类对象！
# isinstance(context["novel_input"], NovelInput) 返回 False
```

**✅ 修复后（路径一致）：**
```python
# examples/basic_usage.py
from src.models import NovelInput  # 统一使用 src 路径

# src/agents/director.py
from src.models import NovelInput

# 结果：指向同一个类对象
# isinstance(context["novel_input"], NovelInput) 返回 True ✅
```

#### 导入路径最佳实践

```python
# ✅ 推荐：项目内部模块使用绝对导入
from src.utils import get_llm_client, config
from src.models import NovelInput, Character, Scene
from src.agents import DirectorAgent
from src.workflows.novel_workflow import NovelWorkflow

# ✅ 推荐：第三方库导入
import httpx
from pydantic import BaseModel

# ❌ 避免：相对导入（除非特殊情况）
from ..utils import get_llm_client
from .models import NovelInput

# ❌ 避免：不明确的导入路径
from models.novel_input import NovelInput  # 模糊，可能冲突
from workflows.novel_workflow import NovelWorkflow
```

#### 常见问题

**Q: 为什么不直接 `from utils import`？**
```python
# ❌ 这样导入会有问题
from utils import get_llm_client  # Python 找不到 utils 模块
```

因为 `utils` 在 `src/` 目录下，Python 模块搜索路径需要包含 `src/` 的父目录。

**Q: examples 目录为什么需要手动添加 src 到路径？**
```python
# examples/basic_usage.py
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))
```

因为 `examples/` 是独立目录，不在 `src/` 包内。示例脚本需要手动告诉 Python 去哪里找 `src` 模块。

**Q: 可以用 `from novel_agent.src.utils import` 吗？**
```python
# 如果项目名称是 novel-agent（pyproject.toml 中定义）
# 安装后可以这样导入：
from novel_agent.src.utils import get_llm_client  # ❌ 不推荐

# 更简洁的方式：
from src.utils import get_llm_client  # ✅ 推荐
```

安装后项目名称是 `novel_agent`，但通常直接使用 `from src.xxx import` 更简洁。

---

## Scene 模型验证错误

### 问题描述

运行 `examples/basic_usage.py` 时出现 Pydantic 验证错误：

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Scene
description
  Field required [type=missing, input_value={'name': '古庙相遇', ...烛光、神秘符文'}, input_type=dict]
```

### 根本原因

`examples/basic_usage.py` 中创建 `Scene` 对象时使用了错误的字段名，与 `src/models/novel_input.py` 中定义的 `Scene` 模型不匹配。

**错误的代码：**
```python
Scene(
    name="古庙相遇",
    location="深山古庙",        # ❌ 不存在
    time="夜晚",               # ❌ 不存在
    atmosphere="神秘、紧张",
    key_elements="..."         # ❌ 不存在
)
```

**Scene 模型定义（src/models/novel_input.py:48-87）：**
```python
class Scene(BaseModel):
    name: str = Field(..., description="Scene name")
    description: str = Field(..., description="Scene description")  # ✅ 必填
    atmosphere: str = Field(..., description="Atmosphere and mood")  # ✅ 必填
    location_type: Optional[str] = Field(None, ...)
    time_period: Optional[str] = Field(None, ...)
    # ...
```

### 解决方案

修改 `examples/basic_usage.py` 中的 Scene 创建代码，使用正确的字段名：

**修复后的代码：**
```python
Scene(
    name="古庙相遇",
    description="深山中的破败古庙，夜晚的烛光摇曳，墙上有神秘符文",  # ✅
    atmosphere="神秘、紧张",  # ✅
)
```

**涉及的文件：**
- `examples/basic_usage.py:53-67` - 三个 Scene 对象的创建
- `examples/basic_usage.py:231-235` - 测试代码中的 Scene 创建

### 预防措施

1. 严格按照 Pydantic 模型定义使用字段名
2. 使用 IDE 的类型检查和自动补全功能
3. 运行测试代码验证模型创建

---

## NovelInput 导入路径不一致问题

### 问题描述

Director agent 无法正确解析 context 中的 `NovelInput` 对象，`isinstance()` 检查失败：

```
novel_input is not a NovelInput instance: <class 'models.novel_input.NovelInput'>
Director agent execution failed: Object of type NovelInput is not JSON serializable
```

### 根本原因

不同的模块使用了不同的导入路径，导致创建了不同的类对象：

**examples/basic_usage.py：**
```python
from models.novel_input import NovelInput  # ❌ 错误的导入路径
```

**src/agents/director.py 和其他模块：**
```python
from src.models import NovelInput  # ✅ 正确的导入路径
```

Python 中，同一个模块通过不同路径导入时会创建不同的类对象，导致 `isinstance()` 检查失败。

### 解决方案

统一所有模块的导入路径，使用 `from src.models import`：

**修复后的代码：**
```python
# examples/basic_usage.py
from src.models import NovelInput, Character, Scene
from src.workflows.novel_workflow import NovelWorkflow, WorkflowConfig

# run_quick_test() 函数中
from src.models import NovelInput, Character, Scene
from src.workflows.novel_workflow import NovelWorkflow, WorkflowConfig
```

**涉及的文件：**
- `examples/basic_usage.py:16-17` - 主导入部分
- `examples/basic_usage.py:221-222` - 测试函数导入部分

### 预防措施

1. 在整个项目中使用一致的导入路径
2. 对于项目内部模块，使用从项目根目录开始的绝对导入路径
3. 使用 lint 工具检查导入一致性

---

## Pydantic 模型 JSON 序列化失败

### 问题描述

在准备 LLM 请求时，尝试序列化包含 Pydantic 模型的 context 字典时失败：

```
Director agent execution failed: Object of type NovelInput is not JSON serializable
```

### 根本原因

`src/agents/base_agent.py` 中的 `_prepare_messages` 方法直接使用 `json.dumps()` 序列化 context，但 Pydantic 模型对象不能直接被 JSON 序列化：

```python
# ❌ 原始代码
context_str = json.dumps(context, ensure_ascii=False, indent=2)
```

当 context 包含 `NovelInput`, `Character`, `Scene` 等 Pydantic 对象时，序列化会失败。

### 解决方案

修改 `_prepare_messages` 方法，在序列化前将 Pydantic 模型转换为字典：

**修复后的代码（src/agents/base_agent.py:78-152）：**
```python
def _prepare_messages(self, task: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
    # 处理 Pydantic 模型序列化
    serializable_context = {}
    for key, value in context.items():
        if hasattr(value, 'model_dump'):
            # Pydantic v2
            serializable_context[key] = value.model_dump()
        elif hasattr(value, 'dict'):
            # Pydantic v1
            serializable_context[key] = value.dict()
        elif isinstance(value, dict):
            # 递归处理嵌套字典
            serializable_context[key] = self._serialize_dict(value)
        else:
            serializable_context[key] = value

    context_str = json.dumps(serializable_context, ensure_ascii=False, indent=2, default=str)
    # ...
```

同时添加辅助方法 `_serialize_dict` 来处理嵌套结构：

```python
def _serialize_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
    """递归序列化包含 Pydantic 模型的字典"""
    result = {}
    for key, value in d.items():
        if hasattr(value, 'model_dump'):
            result[key] = value.model_dump()
        elif hasattr(value, 'dict'):
            result[key] = value.dict()
        elif isinstance(value, dict):
            result[key] = self._serialize_dict(value)
        elif isinstance(value, list):
            result[key] = [
                self._serialize_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    return result
```

**涉及的文件：**
- `src/agents/base_agent.py:78-152`

### 预防措施

1. 在设计 API 接口时考虑序列化需求
2. 使用 Pydantic 的 `model_dump()` 方法而不是直接序列化
3. 在单元测试中验证包含 Pydantic 对象的序列化

---

## NovelInput 字段访问错误

### 问题描述

`src/workflows/novel_workflow.py` 中访问了 `NovelInput` 模型中不存在的字段：

```python
target_style = novel_input.writing_style or f"{novel_input.genre}风格"  # ❌ writing_style 不存在
target_audience = novel_input.target_audience or "一般读者"  # ❌ target_audience 不存在
```

### 根本原因

`NovelInput` 模型使用 `style_preferences` 字典来存储风格偏好，而不是直接的 `writing_style` 和 `target_audience` 字段：

**NovelInput 模型定义（src/models/novel_input.py:144-147）：**
```python
style_preferences: Dict[str, Any] = Field(
    default_factory=dict,
    description="Style preferences (e.g., writing style, pacing, tone)",
)
```

### 解决方案

修改代码以从 `style_preferences` 字典中提取值：

**修复后的代码（src/workflows/novel_workflow.py:387-397）：**
```python
# 提取风格偏好
writing_style = novel_input.style_preferences.get("writing_style", f"{novel_input.genre}风格")
target_audience = novel_input.style_preferences.get("target_audience", "一般读者")

context = {
    "novel_input": novel_input,
    "text": chapter_draft.content,
    "chapter_content": chapter_draft.content,
    "target_style": writing_style,  # ✅
    "target_audience": target_audience,  # ✅
}
```

**对应的示例数据更新（examples/basic_usage.py:78-81）：**
```python
novel_input = NovelInput(
    # ...
    style_preferences={
        "writing_style": "网络小说风格，节奏明快，对话生动",
        "target_audience": "年轻读者，喜欢玄幻、冒险题材",
    },
)
```

**涉及的文件：**
- `src/workflows/novel_workflow.py:387-397`

### 预防措施

1. 严格按照 Pydantic 模型定义访问字段
2. 使用 IDE 的类型提示和自动补全
3. 定期运行类型检查工具（如 mypy）

---

## 总结

### 问题分类

1. **数据模型不匹配** - Scene 和 NovelInput 字段使用错误
2. **导入路径不一致** - 导致 isinstance 检查失败
3. **序列化问题** - Pydantic 模型无法直接 JSON 序列化
4. **字段访问错误** - 访问不存在的字段

### 修复文件清单

- `examples/basic_usage.py` - 修复 Scene 创建、导入路径、style_preferences
- `src/agents/base_agent.py` - 添加 Pydantic 模型序列化支持
- `src/workflows/novel_workflow.py` - 修复 style_preferences 访问

### 最佳实践

1. **保持导入一致性** - 使用统一的项目内导入路径
2. **严格遵循模型定义** - 按照Pydantic模型定义使用字段
3. **考虑序列化需求** - 在设计API时考虑对象序列化
4. **使用类型检查工具** - 利用IDE和lint工具及早发现问题
5. **编写测试验证** - 为关键功能编写单元测试

### 测试验证

所有修复已通过以下测试：

```bash
# 快速系统测试
uv run examples/basic_usage.py --test

# Director 解析测试
uv run test_director_parse.py
```

---

*文档创建日期：2025-12-24*
*最后更新：2025-12-24*
