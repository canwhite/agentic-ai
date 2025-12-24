# 第1章学习指南：Agentic 工作流简介

> **学习目标**：理解什么是 Agentic AI，掌握任务分解方法，学会构建基础的多步骤工作流
>
> **前置知识**：基本的 Python 知识（函数、列表、字典）
>
> **预计时间**：60-90 分钟

---

## 目录

1. [什么是 Agentic AI？](#1-什么是-agentic-ai)
2. [第一个 Agentic 工作流：写论文](#2-第一个-agentic-工作流写论文)
3. [任务分解的核心方法](#3-任务分解的核心方法)
4. [实践项目：客户邮件自动回复系统](#4-实践项目客户邮件自动回复系统)
5. [评估：如何知道系统好不好用？](#5-评估如何知道系统好不好用)
6. [四大设计模式概览](#6-四大设计模式概览)

---

## 1. 什么是 Agentic AI？

### 1.1 对比理解

**传统方式（零样本 Zero-shot）**：
```python
# 用户一次性提问，LLM 直接回答
user_input = "写一篇关于黑洞的文章"
response = llm.generate(user_input)  # 一次性生成
# 问题：质量不高，容易遗漏重要信息
```

**Agentic 方式（多步骤工作流）**：
```python
# 第1步：生成大纲
outline = llm.generate("为'黑洞'这篇文章写一个大纲")

# 第2步：根据大纲搜索资料
for section in outline:
    search_results = search_tool(section['topic'])
    section['content'] = search_results

# 第3步：撰写初稿
draft = llm.generate(f"根据大纲和资料写文章: {outline}")

# 第4步：反思改进
feedback = llm.generate(f"检查这篇文章的问题: {draft}")
final_article = llm.generate(f"根据反馈改进文章: {feedback}")

# 结果：质量更高，内容更全面
```

### 1.2 核心要点

| 特性 | 传统方式 | Agentic 方式 |
|------|---------|-------------|
| 步骤数 | 1步 | 多步（3-10步） |
| 质量 | 基础 | 高质量 |
| 工具使用 | 无 | 多种工具（搜索、数据库等） |
| 复杂度 | 简单 | 复杂但可控 |

---

## 2. 第一个 Agentic 工作流：写论文

让我们从最简单的例子开始：用 Agentic 工作流写一篇文章。

### 2.1 环境准备

```bash
# 安装必要的库
pip install openai python-dotenv
```

### 2.2 配置 API

创建文件 `.env`：
```bash
# .env 文件
OPENAI_API_KEY=your_api_key_here
```

### 2.3 完整代码示例

创建文件 `essay_agent.py`：

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化 OpenAI 客户端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_outline(topic):
    """
    第1步：生成文章大纲
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"为'{topic}'写一个文章大纲，包含3-5个主要部分"}
        ]
    )
    return response.choices[0].message.content

def web_search(keyword):
    """
    第2步：网络搜索（模拟）
    实际应用中可以使用真实的搜索API
    """
    # 这里我们用模拟数据
    mock_results = {
        "黑洞": "黑洞是时空中的一个区域，引力极强，连光都无法逃脱。",
        "事件视界": "事件视界是黑洞的边界，越过这个边界就无法返回。",
        "霍金辐射": "霍金辐射是黑洞由于量子效应发出的辐射。"
    }
    return mock_results.get(keyword, f"关于{keyword}的搜索结果")

def write_draft(outline, research_data):
    """
    第3步：撰写初稿
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"""
根据以下大纲和研究资料，写一篇文章：

大纲：
{outline}

研究资料：
{research_data}

要求：内容详细，逻辑清晰
            """}
        ]
    )
    return response.choices[0].message.content

def reflect_and_improve(draft):
    """
    第4步：反思与改进
    """
    # 先反思
    feedback = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"""
请评估以下文章，指出需要改进的地方：
{draft}
            """}
        ]
    )

    # 根据反馈改进
    improved = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"""
根据以下反馈，改进文章：
原始文章：
{draft}

反馈意见：
{feedback.choices[0].message.content}
            """}
        ]
    )

    return improved.choices[0].message.content

def write_essay_agent(topic):
    """
    完整的 Agentic 工作流
    """
    print(f"🚀 开始写关于'{topic}'的文章...")
    print("-" * 50)

    # 第1步：生成大纲
    print("📝 第1步：生成大纲...")
    outline = generate_outline(topic)
    print(f"大纲已生成：\n{outline}\n")

    # 第2步：搜索资料
    print("🔍 第2步：搜索相关资料...")
    research_data = web_search(topic)
    print(f"找到资料：{research_data}\n")

    # 第3步：撰写初稿
    print("✍️  第3步：撰写初稿...")
    draft = write_draft(outline, research_data)
    print(f"初稿已生成（{len(draft)}字）\n")

    # 第4步：反思与改进
    print("🔄 第4步：反思与改进...")
    final_article = reflect_and_improve(draft)
    print(f"✅ 最终文章已完成！（{len(final_article)}字）\n")

    return final_article

# 使用示例
if __name__ == "__main__":
    article = write_essay_agent("黑洞")
    print("\n" + "="*50)
    print("最终文章：")
    print("="*50)
    print(article)
```

### 2.4 运行代码

```bash
python essay_agent.py
```

### 2.5 代码讲解

**关键概念**：
1. **每个步骤都是一个独立的函数**：清晰、可测试
2. **步骤之间传递数据**：上一步的输出是下一步的输入
3. **可以随时插入新步骤**：比如添加"人工审核"

**扩展练习**：
- 添加第5步：格式化输出（Markdown、HTML）
- 添加第6步：保存到文件
- 尝试不同的主题

---

## 3. 任务分解的核心方法

### 3.1 黄金法则

> **"如果某一步骤效果不好，就把它再拆成更小的子步骤"**

### 3.2 实践案例：从发票提取信息

**任务**：从 PDF 发票中提取关键信息（开票方、金额、到期日）

#### 版本1：1步完成（太简单）

```python
def extract_invoice_info(pdf_text):
    # 一次完成所有提取
    result = llm.generate(f"从发票文本中提取开票方、金额、到期日：{pdf_text}")
    return result
# 问题：容易出错，不准确
```

#### 版本2：3步工作流（较好）

```python
def extract_invoice_info_v2(pdf_text):
    # 第1步：判断是否为发票
    is_invoice = llm.generate(f"这是发票吗？{pdf_text}")

    if is_invoice == "是":
        # 第2步：提取信息
        info = llm.generate(f"提取开票方、金额、到期日：{pdf_text}")

        # 第3步：格式化输出
        formatted = format_output(info)
        return formatted
```

#### 版本3：5步工作流（最佳）

```python
def extract_invoice_info_v3(pdf_text):
    # 第1步：判断是否为发票
    is_invoice = validate_invoice(pdf_text)

    if not is_invoice:
        return "这不是发票"

    # 第2步：提取开票方
    biller = extract_field(pdf_text, "开票方")

    # 第3步：提取金额
    amount = extract_field(pdf_text, "应付金额")

    # 第4步：提取到期日
    due_date = extract_field(pdf_text, "到期日")

    # 第5步：验证数据完整性
    if not all([biller, amount, due_date]):
        return "信息不完整，请人工检查"

    # 第6步：保存到数据库
    save_to_database({
        "biller": biller,
        "amount": amount,
        "due_date": due_date
    })

    return "信息已保存"
```

### 3.3 任务分解练习

**任务**：回复客户邮件

尝试分解这个任务，然后看下面的答案：

<details>
<summary>查看答案</summary>

```python
def handle_customer_email(email_text):
    # 第1步：提取关键信息
    info = extract_key_info(email_text)
    # 订单号、产品、问题描述

    # 第2步：查询订单详情
    order_details = query_database(info['order_id'])

    # 第3步：分析问题类型
    problem_type = classify_problem(info, order_details)
    # 发错货、质量问题、退款等

    # 第4步：生成回复草稿
    draft = generate_response(info, order_details, problem_type)

    # 第5步：检查回复质量
    quality_score = check_quality(draft)

    if quality_score < 0.8:
        # 第6步：人工审核（如果质量不高）
        draft = human_review(draft)

    # 第7步：发送邮件
    send_email(info['customer_email'], draft)

    return "邮件已发送"
```
</details>

---

## 4. 实践项目：客户邮件自动回复系统

现在让我们做一个完整的实践项目。

### 4.1 项目结构

```
customer_service_agent/
├── config.py           # 配置文件
├── tools.py            # 工具函数
├── workflow.py         # 主工作流
└── main.py             # 入口文件
```

### 4.2 完整代码

#### config.py

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-3.5-turbo"

# 数据库配置（模拟）
DATABASE = {
    "orders": {
        "#8847": {
            "customer": "Susan Jones",
            "product": "KitchenPro 搅拌机",
            "color": "蓝色",
            "status": "已发货"
        }
    }
}

# 竞争对手列表（用于检查）
COMPETITORS = ["CompCo", "RivalCo", "CompetitorInc"]
```

#### tools.py

```python
# tools.py
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL, DATABASE, COMPETITORS

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_key_info(email_text):
    """
    第1步：从邮件中提取关键信息
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个信息提取专家。请从邮件中提取：订单号、产品、问题。"},
            {"role": "user", "content": email_text}
        ]
    )

    # 简单解析（实际应该用更复杂的方法）
    result = {
        "order_id": "#8847",
        "product": "搅拌机",
        "problem": "收到错误商品"
    }

    return result

def query_order(order_id):
    """
    第2步：查询订单详情
    """
    return DATABASE["orders"].get(order_id, None)

def classify_problem(info, order):
    """
    第3步：分类问题
    """
    return "发错货"

def generate_response(info, order, problem_type):
    """
    第4步：生成回复草稿
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个专业的客服代表。生成礼貌、专业的回复。"},
            {"role": "user", "content": f"""
客户信息：{info}
订单详情：{order}
问题类型：{problem_type}

请生成一封回复邮件：
1. 表达歉意
2. 说明解决方案
3. 提供后续步骤
            """}
        ]
    )

    return response.choices[0].message.content

def check_competitor_mentions(text):
    """
    第5步：检查是否提及竞争对手
    """
    mentioned = []
    for competitor in COMPETITORS:
        if competitor in text:
            mentioned.append(competitor)

    return mentioned

def check_response_quality(draft):
    """
    第6步：检查回复质量
    """
    # 检查竞争对手
    competitors = check_competitor_mentions(draft)

    # 检查长度
    word_count = len(draft.split())

    # 检查礼貌用语
    polite_words = ["请", "谢谢", "抱歉"]
    has_polite = any(word in draft for word in polite_words)

    score = {
        "competitor_mentions": competitors,
        "word_count": word_count,
        "is_polite": has_polite,
        "pass": len(competitors) == 0 and has_polite
    }

    return score

def improve_response(draft, quality_score):
    """
    第7步：改进回复（如果质量不达标）
    """
    if quality_score["pass"]:
        return draft

    # 如果不达标，让 LLM 改进
    feedback = []

    if quality_score["competitor_mentions"]:
        feedback.append(f"不要提及竞争对手：{quality_score['competitor_mentions']}")

    if not quality_score["is_polite"]:
        feedback.append("请使用更礼貌的语言")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个专业的客服代表。"},
            {"role": "user", "content": f"""
原回复：
{draft}

需要改进的地方：
{chr(10).join(feedback)}

请生成改进后的回复：
            """}
        ]
    )

    return response.choices[0].message.content

def send_email(to, subject, body):
    """
    第8步：发送邮件（模拟）
    """
    print(f"\n📧 发送邮件到：{to}")
    print(f"主题：{subject}")
    print(f"内容：{body}")
    return True
```

#### workflow.py

```python
# workflow.py
from tools import (
    extract_key_info,
    query_order,
    classify_problem,
    generate_response,
    check_response_quality,
    improve_response,
    send_email
)

def customer_service_workflow(email_text):
    """
    客户服务完整工作流
    """
    print("🎯 开始处理客户邮件...")
    print("=" * 50)

    # 第1步：提取关键信息
    print("📋 第1步：提取关键信息...")
    info = extract_key_info(email_text)
    print(f"   提取结果：{info}")

    # 第2步：查询订单
    print("\n🔍 第2步：查询订单详情...")
    order = query_order(info["order_id"])
    if not order:
        print("   ❌ 订单不存在")
        return None
    print(f"   订单详情：{order}")

    # 第3步：分类问题
    print("\n🏷️  第3步：分类问题...")
    problem_type = classify_problem(info, order)
    print(f"   问题类型：{problem_type}")

    # 第4步：生成回复
    print("\n✍️  第4步：生成回复草稿...")
    draft = generate_response(info, order, problem_type)
    print(f"   草稿已生成（{len(draft)} 字）")

    # 第5步：检查质量
    print("\n🔎 第5步：检查回复质量...")
    quality_score = check_response_quality(draft)
    print(f"   质量评分：{quality_score}")

    # 第6步：改进（如果需要）
    if not quality_score["pass"]:
        print("\n🔄 第6步：改进回复...")
        final_response = improve_response(draft, quality_score)
        print(f"   改进完成")
    else:
        final_response = draft
        print("\n✅ 回复质量合格，无需改进")

    # 第7步：发送邮件
    print("\n📧 第7步：发送邮件...")
    send_email(
        to=order["customer"],
        subject=f"关于您的订单 {info['order_id']}",
        body=final_response
    )

    print("\n" + "=" * 50)
    print("✨ 邮件处理完成！")

    return final_response
```

#### main.py

```python
# main.py
from workflow import customer_service_workflow

# 测试邮件
test_email = """
您好，

我订购了蓝色 KitchenPro 搅拌机（订单 #8847），
但收到的是红色烤面包机。

请帮我解决这个问题。

谢谢，
Susan Jones
"""

# 运行工作流
if __name__ == "__main__":
    response = customer_service_workflow(test_email)
```

### 4.3 运行项目

```bash
python main.py
```

### 4.4 项目讲解

**关键概念**：

1. **模块化设计**：每个功能独立文件，易于维护
2. **工作流清晰**：从提取信息到发送邮件，步骤明确
3. **质量控制**：自动检查回复质量，不合格则改进
4. **可扩展**：容易添加新功能（如情感分析、优先级分类）

**练习**：
- 添加情感分析功能（判断客户是否生气）
- 添加优先级分类（紧急问题优先处理）
- 添加日志记录功能

---

## 5. 评估：如何知道系统好不好用？

### 5.1 为什么评估很重要？

**核心观点**：能否进行严格评估，是区分"做得好"与"做得差"的最大预测因素。

### 5.2 两种评估类型

#### 5.2.1 端到端评估

评估整个系统的最终输出质量。

```python
def evaluate_end_to_end(test_cases):
    """
    端到端评估示例
    """
    results = []

    for case in test_cases:
        # 运行系统
        output = customer_service_workflow(case["input"])

        # 评估输出
        score = evaluate_output_quality(output, case["expected"])

        results.append({
            "case_id": case["id"],
            "score": score,
            "output": output
        })

    # 计算平均分
    avg_score = sum(r["score"] for r in results) / len(results)

    print(f"平均得分：{avg_score:.2f}")
    return results

def evaluate_output_quality(output, expected):
    """
    评估输出质量（简化版）
    """
    # 检查关键词
    required_keywords = expected.get("keywords", [])
    score = sum(1 for kw in required_keywords if kw in output)

    return score / len(required_keywords) if required_keywords else 0
```

#### 5.2.2 组件级评估

评估单个组件的输出质量。

```python
def evaluate_extract_component():
    """
    评估信息提取组件
    """
    test_cases = [
        {
            "input": "我的订单 #8847 有问题",
            "expected_order_id": "#8847"
        },
        {
            "input": "订单 #9999 需要退款",
            "expected_order_id": "#9999"
        }
    ]

    correct = 0

    for case in test_cases:
        result = extract_key_info(case["input"])
        if result["order_id"] == case["expected_order_id"]:
            correct += 1

    accuracy = correct / len(test_cases)
    print(f"信息提取准确率：{accuracy:.2%}")

    return accuracy
```

### 5.3 实战：构建评估数据集

```python
# evals.py

# 评估数据集
EVAL_DATASET = [
    {
        "id": 1,
        "input": "我订购了蓝色搅拌机，收到红色烤面包机",
        "expected": {
            "order_id": "#8847",
            "problem_type": "发错货",
            "should_apologize": True
        }
    },
    {
        "id": 2,
        "input": "我想退款",
        "expected": {
            "problem_type": "退款",
            "should_apologize": True
        }
    }
]

def run_evaluation(dataset):
    """
    运行评估
    """
    results = []

    for case in dataset:
        print(f"\n评估案例 {case['id']}...")

        # 提取信息
        info = extract_key_info(case["input"])

        # 评估提取准确度
        order_match = info.get("order_id") == case["expected"].get("order_id")
        problem_match = info.get("problem") == case["expected"].get("problem_type")

        score = {
            "case_id": case["id"],
            "order_id_match": order_match,
            "problem_match": problem_match,
            "total_score": sum([order_match, problem_match]) / 2
        }

        results.append(score)

    # 打印结果
    print("\n" + "="*50)
    print("评估结果：")
    for result in results:
        print(f"案例 {result['case_id']}: {result['total_score']:.2%}")

    avg_score = sum(r["total_score"] for r in results) / len(results)
    print(f"\n平均得分: {avg_score:.2%}")

    return results

# 运行评估
if __name__ == "__main__":
    run_evaluation(EVAL_DATASET)
```

### 5.4 评估最佳实践

1. **从简单开始**：先用10-20个测试案例
2. **迭代改进**：根据评估结果调整系统
3. **客观指标**：使用代码可检查的指标（如准确率）
4. **主观指标**：必要时用 LLM 作为裁判

### 5.5 自主性等级评估标准

**自主性等级体系**：

| 等级 | 特征 | 示例 | 代码复杂度 |
|------|------|------|------------|
| **低自主性** | 所有步骤预设，硬编码工具调用 | 固定流程的发票处理 | ⭐ |
| **中自主性** | 部分决策由AI做出 | 根据内容选择不同回复模板 | ⭐⭐ |
| **高自主性** | AI自主决定步骤和工具调用 | 动态规划研究路径 | ⭐⭐⭐⭐ |

**评估标准**：
- 步骤规划的灵活性
- 工具选择的自主性
- 错误处理的能力
- 学习改进的程度

### 5.6 工作流代码实现细节

**核心工作流模式**：

```python
# 论文写作工作流（4步）
def essay_workflow(topic):
    # 第1步：生成大纲
    outline = generate_outline(topic)

    # 第2步：搜索资料
    research_data = web_search(topic)

    # 第3步：撰写初稿
    draft = write_draft(outline, research_data)

    # 第4步：反思改进
    final = reflect_and_improve(draft)

    return final

# 客户服务工作流（7步）
def customer_service_workflow(email_text):
    # 第1步：提取关键信息
    info = extract_key_info(email_text)

    # 第2步：查询订单详情
    order_details = query_database(info['order_id'])

    # 第3步：分类问题
    problem_type = classify_problem(info, order_details)

    # 第4步：生成回复草稿
    draft = generate_response(info, order_details, problem_type)

    # 第5步：检查回复质量
    quality_score = check_quality(draft)

    # 第6步：人工审核（如果质量不高）
    if quality_score < 0.8:
        draft = human_review(draft)

    # 第7步：发送邮件
    send_email(info['customer_email'], draft)

    return "邮件已发送"
```

**关键实现原则**：
1. **每个步骤都是独立函数**：便于测试和维护
2. **步骤间通过数据传递连接**：上一步的输出是下一步的输入
3. **包含错误处理和质量控制**：确保系统稳定性
4. **可扩展性设计**：易于添加新步骤或修改现有步骤

### 5.7 四大设计模式选择框架

**模式选择决策树**：

```
简单任务 → 反思模式
需要外部数据 → 工具使用模式
步骤不确定 → 规划模式
复杂协作 → 多智能体模式
```

**详细对比表**：

| 模式 | 核心思想 | 适用场景 | 实现复杂度 | 质量提升 |
|------|----------|----------|------------|----------|
| **反思** | 自我检查改进 | 文本生成、代码编写 | ⭐⭐ | 20-50% |
| **工具使用** | 调用外部工具 | 信息检索、数据处理 | ⭐⭐⭐ | 30-80% |
| **规划** | 动态决定步骤 | 复杂任务处理 | ⭐⭐⭐⭐ | 40-100% |
| **多智能体** | 角色协同工作 | 大型复杂项目 | ⭐⭐⭐⭐⭐ | 50-200% |

### 5.8 性能优化指标

**系统性能评估**：

```python
def evaluate_system_performance():
    """评估系统整体性能"""
    metrics = {
        'accuracy': 0.0,        # 准确性
        'response_time': 0.0,   # 响应时间
        'cost_efficiency': 0.0, # 成本效率
        'user_satisfaction': 0.0 # 用户满意度
    }

    # 信息提取准确率
    test_cases = [
        {"input": "订单#8847有问题", "expected_order_id": "#8847"},
        {"input": "我想退款订单#9999", "expected_order_id": "#9999"}
    ]

    correct_extractions = 0
    for case in test_cases:
        result = extract_key_info(case["input"])
        if result["order_id"] == case["expected_order_id"]:
            correct_extractions += 1

    metrics['accuracy'] = correct_extractions / len(test_cases)

    return metrics
```

### 5.9 实际应用案例库

**完整案例对比**：

1. **发票处理工作流**（PDF→文本→提取→数据库）
   - 复杂性：高（需要OCR、数据验证、错误处理）
   - 准确性要求：极高（涉及财务）
   - 推荐模式：工具使用 + 反思

2. **客户邮件回复**（提取→查询→生成→发送）
   - 复杂性：中等（需要情感分析、质量控制）
   - 准确性要求：高（影响客户体验）
   - 推荐模式：反思 + 工具使用

3. **库存查询系统**（解析→多工具调用→综合回复）
   - 复杂性：中等（需要数据库查询、逻辑推理）
   - 准确性要求：高（影响业务决策）
   - 推荐模式：工具使用 + 规划

4. **视觉计算机使用**（浏览器自动化）
   - 复杂性：极高（需要图像识别、动作规划）
   - 准确性要求：中等（可重试）
   - 推荐模式：规划 + 多智能体

---

## 6. 四大设计模式概览

Agentic AI 的四大核心设计模式：

### 6.1 反思 (Reflection)

**核心思想**：让模型检查并改进自己的输出

```python
def reflection_pattern(task):
    # 第1步：生成初稿
    draft = llm.generate(f"完成以下任务：{task}")

    # 第2步：反思
    feedback = llm.generate(f"检查以下输出的问题：{draft}")

    # 第3步：改进
    improved = llm.generate(f"根据反馈改进：{feedback}")

    return improved
```

### 6.2 工具使用 (Tool Use)

**核心思想**：让模型调用外部工具

```python
def tool_use_pattern(question):
    # 模型决定是否需要工具
    if needs_tool(question):
        # 调用工具
        result = tool.execute(question)
        # 基于工具结果回答
        answer = llm.generate(f"基于工具结果回答：{result}")
    else:
        # 直接回答
        answer = llm.generate(question)

    return answer
```

### 6.3 规划 (Planning)

**核心思想**：模型自主决定执行步骤

```python
def planning_pattern(goal):
    # 第1步：生成计划
    plan = llm.generate(f"为以下目标制定计划：{goal}")

    # 第2步：执行计划
    for step in plan:
        result = execute_step(step)

    return result
```

### 6.4 多智能体协作 (Multi-agent)

**核心思想**：多个专长角色协同工作

```python
def multi_agent_pattern(task):
    # 研究员 Agent
    research = researcher_agent.work(task)

    # 写作 Agent
    draft = writer_agent.work(research)

    # 编辑 Agent
    final = editor_agent.work(draft)

    return final
```

---

## 本章小结

### 核心要点回顾

1. **Agentic AI = 多步骤工作流**
   - 不是一次性生成，而是分步骤完成
   - 每一步都可以调用工具、进行检查

2. **任务分解是核心技能**
   - 从简单开始（1-3步）
   - 效果不好就继续拆分
   - 直到每步都能良好执行

3. **评估驱动改进**
   - 端到端评估：看整体质量
   - 组件级评估：看单个步骤
   - 没有评估就无法进步

4. **四大设计模式**
   - 反思：自我检查改进
   - 工具使用：扩展能力
   - 规划：自主决策
   - 多智能体：角色分工

### 下一步学习

- 第2章：深入理解反思模式
- 第3章：学习工具使用
- 第4章：掌握评估和错误分析
- 第5章：构建高度自治的 Agent

### 练习建议

1. **修改客户邮件系统**：
   - 添加情感分析
   - 添加优先级分类
   - 添加多种回复模板

2. **构建新系统**：
   - 从发票提取信息
   - 生成社交媒体文案
   - 自动生成会议纪要

3. **优化现有系统**：
   - 添加评估指标
   - 改进错误处理
   - 提升响应速度

---

## 7. 如何写出完整初始版本 Agent

基于本章所学，以下是构建完整初始版本 Agent 的 7 步流程：

### 7.1 第1步：明确 Agent 的目标
```python
# 清晰定义 Agent 要解决什么问题
AGENT_GOAL = """
目标：构建一个客户邮件自动回复 Agent
输入：客户邮件文本
输出：专业、准确的回复邮件
要求：提取订单信息、查询数据库、生成回复、质量检查
"""
```

### 7.2 第2步：设计工作流步骤
```python
# 将目标分解为具体步骤
WORKFLOW_STEPS = [
    "1. 提取邮件关键信息（订单号、问题类型）",
    "2. 查询订单数据库",
    "3. 分类问题类型（发错货、退款、咨询等）",
    "4. 生成回复草稿",
    "5. 检查回复质量（礼貌性、准确性）",
    "6. 改进回复（如果需要）",
    "7. 发送邮件"
]
```

### 7.3 第3步：创建项目结构
```bash
# 标准 Agent 项目结构
my_agent/
├── config.py           # 配置文件（API密钥、模型设置）
├── tools/              # 工具函数目录
│   ├── __init__.py
│   ├── extractor.py    # 信息提取工具
│   ├── database.py     # 数据库查询工具
│   └── validator.py    # 验证工具
├── workflow.py         # 主工作流逻辑
├── evaluator.py        # 评估模块
├── main.py             # 入口文件
├── requirements.txt    # 依赖包
└── tests/              # 测试文件
```

### 7.4 第4步：实现核心工作流
```python
# workflow.py - 核心工作流模板
def agent_workflow(input_data):
    """Agent 主工作流"""

    # 步骤1：预处理输入
    processed_input = preprocess(input_data)

    # 步骤2：提取关键信息
    extracted_info = extract_key_info(processed_input)

    # 步骤3：查询外部数据
    external_data = query_external_sources(extracted_info)

    # 步骤4：生成响应
    response_draft = generate_response(extracted_info, external_data)

    # 步骤5：质量检查
    quality_score = check_quality(response_draft)

    # 步骤6：改进（如果需要）
    if quality_score < QUALITY_THRESHOLD:
        response_draft = improve_response(response_draft)

    # 步骤7：后处理
    final_output = postprocess(response_draft)

    return final_output
```

### 7.5 第5步：添加评估模块
```python
# evaluator.py - 评估模板
def evaluate_agent(test_cases):
    """评估 Agent 性能"""
    results = []

    for case in test_cases:
        # 运行 Agent
        output = agent_workflow(case["input"])

        # 评估指标
        accuracy = calculate_accuracy(output, case["expected"])
        relevance = calculate_relevance(output, case["context"])
        completeness = calculate_completeness(output)

        results.append({
            "case_id": case["id"],
            "accuracy": accuracy,
            "relevance": relevance,
            "completeness": completeness,
            "overall_score": (accuracy + relevance + completeness) / 3
        })

    return results
```

### 7.6 第6步：调试与优化
```python
# 调试检查清单
DEBUG_CHECKLIST = [
    "1. API密钥是否正确配置？",
    "2. 输入数据格式是否正确？",
    "3. 每个步骤是否按预期执行？",
    "4. 错误处理是否完善？",
    "5. 评估分数是否达标？"
]

# 常见问题解决方案
TROUBLESHOOTING_GUIDE = {
    "Agent 不工作": "检查 config.py 中的 API 配置",
    "输出质量差": "增加反思步骤或改进提示词",
    "响应时间慢": "优化数据库查询或添加缓存",
    "准确率低": "增加训练数据或改进提取算法"
}
```

### 7.7 第7步：部署与迭代
```python
# 部署检查清单
DEPLOYMENT_CHECKLIST = [
    "1. 代码通过所有测试",
    "2. 评估分数达到要求（如 >0.8）",
    "3. 错误处理完善",
    "4. 日志记录配置",
    "5. 监控指标设置"
]

# 迭代改进流程
def iterative_improvement(agent_version, feedback_data):
    """迭代改进 Agent"""
    # 收集反馈
    issues = analyze_feedback(feedback_data)

    # 优先级排序
    prioritized_issues = prioritize_issues(issues)

    # 实施改进
    for issue in prioritized_issues[:3]:  # 每次解决前3个问题
        fixed_agent = fix_issue(agent_version, issue)

        # 重新评估
        new_score = evaluate_agent(TEST_CASES)

        if new_score > agent_version.score:
            agent_version = fixed_agent

    return agent_version
```

### 7.8 快速启动模板
```bash
# 使用模板快速开始
git clone https://github.com/example/agent-template.git my-agent
cd my-agent
cp .env.example .env  # 配置环境变量
pip install -r requirements.txt
python main.py --test  # 测试运行
```

### 7.9 从零开始的 30 分钟指南
```python
# 30分钟构建简单 Agent
# 分钟 0-5：定义目标
# 分钟 5-10：设计3步工作流
# 分钟 10-20：编写核心代码
# 分钟 20-25：添加基本评估
# 分钟 25-30：测试和调试
```

**恭喜你完成第1章学习！** 🎉

你已经掌握了 Agentic AI 的基础概念，可以构建简单的多步骤工作流了。

**记住**：从简单开始，逐步迭代，用评估驱动改进。

**现在你可以**：
1. 使用第7节的模板快速构建你的第一个 Agent
2. 运行客户邮件回复系统的完整示例
3. 开始设计你自己的 Agent 项目
