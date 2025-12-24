# Novel Agent

一个基于Agentic AI多智能体系统的小说章节生成工具，能够根据大纲、人物设定、场景描述等信息，生成具有剧情张力且情节连贯的小说章节。

## 特性

- 🎭 **多智能体协作**：6个专门Agent分工协作，确保章节质量
- 📖 **剧情张力生成**：自动设计冲突、悬念、情感起伏点
- 👥 **人物一致性**：防OOC、防崩人设、防水文"三板斧"机制
- 🎨 **场景渲染**：生动描述场景，营造氛围
- 🔄 **连贯性检查**：确保情节逻辑一致，与大纲相符
- 📊 **灵活输出**：支持纯文本和JSON格式输出
- 🚀 **高性能**：并行执行，快速生成

## 支持的创作类型

- 网络小说/爽文
- 科幻/奇幻
- 玄幻
- （未来扩展：悬疑、言情等）

## 快速开始

### 1. 安装

使用uv（推荐）或pip：

```bash
# 使用uv
uv pip install -e .

# 或使用pip
pip install -e .
```

### 2. 配置

复制环境变量文件并配置DeepSeek API密钥：

```bash
cp .env.example .env
# 编辑.env文件，填入你的DeepSeek API密钥
```

### 3. 基本使用

```python
from novel_agent import NovelAgent
from novel_agent.models import NovelInput, Character, Scene

# 创建输入数据
input_data = NovelInput(
    overall_outline="一个少年在玄幻世界修炼成神的故事",
    chapter_outline="主角在秘境中意外获得上古传承，引发各方势力争夺",
    characters=[
        Character(
            name="林风",
            role="主角",
            personality="坚韧不拔，机智勇敢",
            background="普通山村少年",
            special_abilities=["修炼天赋异禀"]
        )
    ],
    scenes=[
        Scene(
            name="上古秘境",
            description="充满神秘能量的古老遗迹",
            atmosphere="神秘、危险、机遇并存"
        )
    ],
    genre="玄幻",
    style_preferences={"文风": "热血激昂", "节奏": "快"}
)

# 创建Agent并生成章节
agent = NovelAgent()
result = agent.generate_chapter(input_data)

# 输出结果
print(f"生成的章节（{result.metadata.word_count}字）：")
print(result.content)

# 或者获取JSON格式
json_result = result.to_dict()
print(json_result)
```

## 架构设计

### 智能体分工

1. **导演Agent**：总协调者，负责整体剧情把控
2. **情节设计Agent**：剧情架构师，设计情节发展
3. **人物塑造Agent**：人物设计师，生成人物对话和行为
4. **场景渲染Agent**：场景描绘师，生动描述场景环境
5. **文笔优化Agent**：文字润色师，优化语言表达
6. **连贯性检查Agent**：质量检查员，确保一致性

### 工作流程

```
输入解析 → 任务规划 → 并行创作 → 初步合成 → 优化检查 → 最终输出
```

## 高级功能

### 情感曲线控制
```python
input_data.style_preferences = {
    "情感曲线": ["平静", "紧张", "高潮", "回落"],
    "节奏控制": "快慢结合"
}
```

### 风格模仿
```python
input_data.style_preferences = {
    "模仿作者": "金庸",
    "文风特点": "武侠风格，人物鲜明"
}
```

### 多线叙事
```python
input_data.chapter_outline = """
主线：主角修炼突破
副线1：反派阴谋策划
副线2：女主角家族危机
"""
```

### 伏笔设置
```python
input_data.props = [
    {"name": "神秘玉佩", "description": "蕴含上古秘密", "is_foreshadowing": True}
]
```

## API参考

### NovelAgent类

```python
class NovelAgent:
    def __init__(self, config: Optional[Dict] = None):
        """初始化小说Agent"""

    def generate_chapter(
        self,
        input_data: NovelInput,
        output_format: str = "text"  # "text" 或 "json"
    ) -> ChapterResult:
        """生成小说章节"""

    def batch_generate(
        self,
        input_data_list: List[NovelInput],
        parallel: bool = True
    ) -> List[ChapterResult]:
        """批量生成章节"""
```

### 数据模型

- `NovelInput`: 小说创作输入数据
- `Character`: 人物设定
- `Scene`: 场景描述
- `ChapterResult`: 章节生成结果
- `ChapterMetadata`: 章节元数据

## 配置选项

### 环境变量
- `DEEPSEEK_API_KEY`: DeepSeek API密钥（必需）
- `DEEPSEEK_MODEL`: 使用的模型（默认：deepseek-chat）
- `AGENT_TEMPERATURE`: 生成温度（默认：0.7）
- `DEFAULT_CHAPTER_LENGTH`: 默认章节长度（默认：2000字）

### 运行时配置
```python
config = {
    "llm_provider": "deepseek",  # 或 "openai"
    "max_retries": 3,
    "timeout": 30,
    "cache_enabled": True,
    "parallel_execution": True
}
agent = NovelAgent(config=config)
```

## 示例

查看 `examples/` 目录获取完整示例：

- `basic_usage.py`: 基础使用示例
- `fantasy_novel.py`: 奇幻小说生成示例
- `web_novel.py`: 网络小说生成示例

## 开发

### 安装开发依赖
```bash
uv pip install -e ".[dev]"
```

### 运行测试
```bash
pytest tests/
```

### 代码格式化
```bash
black src/
isort src/
ruff check --fix src/
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

Apache License 2.0

## 致谢

本项目基于Agentic AI设计模式，特别感谢相关教程的启发。

## 支持

如有问题，请：
1. 查看 `examples/` 目录中的示例
2. 查阅代码文档
3. 提交Issue