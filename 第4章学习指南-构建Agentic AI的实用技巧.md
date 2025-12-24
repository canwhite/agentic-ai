# 第4章学习指南：构建Agentic AI的实用技巧

> **学习目标**：掌握评估和优化Agentic AI系统的核心方法，学会构建可测量、可改进的AI系统
>
> **前置知识**：完成第1-3章，熟悉基础工作流、反思模式和工具使用
>
> **预计时间**：100-130 分钟

---

## 目录

0. [前置知识回顾](#0-前置知识回顾)
1. [评估体系构建](#1-评估体系构建)
2. [错误分析与优先级制定](#2-错误分析与优先级制定)
3. [组件级评估实践](#3-组件级评估实践)
4. [实战项目1：发票处理系统优化](#4-实战项目1发票处理系统优化)
5. [实战项目2：客户邮件回复质量提升](#5-实战项目2客户邮件回复质量提升)
6. [延迟与成本优化](#6-延迟与成本优化)
7. [开发流程最佳实践](#7-开发流程最佳实践)
8. [学习路径建议](#8-学习路径建议)

---

## 0. 前置知识回顾

如果你跳过了第1-3章，或者需要快速回顾核心概念，这里是你需要了解的基础知识：

### 0.1 Agentic AI 核心概念

**什么是 Agentic AI？**
- **传统方式**：用户一次性提问，LLM 直接回答（零样本）
- **Agentic 方式**：将复杂任务分解为多个步骤，每个步骤可以调用工具、进行反思、查询数据等

**关键特点**：
- **多步骤工作流**：3-10个步骤，而不是1步完成
- **工具使用**：可以调用外部函数和API
- **自我改进**：通过反思模式检查并改进输出
- **可评估**：每个步骤和整体输出都可以测量质量

### 0.2 三大核心模式回顾

| 模式 | 核心思想 | 简单示例 |
|------|----------|----------|
| **工作流模式** | 将任务分解为多个步骤 | 写论文：大纲 → 搜索 → 写作 → 改进 |
| **反思模式** | 自我检查并改进输出 | 生成初稿 → 检查问题 → 改进 → 最终版 |
| **工具使用模式** | 调用外部函数扩展能力 | 查询时间、搜索网络、执行代码 |

### 0.3 基础代码结构

一个典型的 Agentic 工作流代码结构：
```python
def agent_workflow(input_data):
    # 第1步：预处理
    processed = preprocess(input_data)

    # 第2步：提取信息
    extracted = extract_info(processed)

    # 第3步：查询数据（工具使用）
    external_data = query_database(extracted)

    # 第4步：生成响应
    response = generate_response(extracted, external_data)

    # 第5步：反思改进
    improved = reflect_and_improve(response)

    return improved
```

### 0.4 快速检查：你准备好了吗？

如果你对以下概念有基本理解，就可以开始第4章的学习：
- ✅ 知道如何调用 OpenAI API 或其他 LLM API
- ✅ 理解 Python 函数和类的基本用法
- ✅ 知道什么是"多步骤工作流"
- ✅ 了解"评估"在软件开发中的重要性

如果以上有任何不清楚，建议先快速浏览第1-3章的核心概念部分。

---

## 1. 评估体系构建

### 1.1 为什么评估是核心？

**核心理念**：能否进行严格评估，是区分"做得好"与"做得差"的最大预测因素。

**真实案例对比**：
```
团队A：不断构建新功能，从不系统评估 → 6个月后系统仍然不稳定
团队B：投入50%时间做评估和改进 → 3个月后系统准确率提升到92%
```

### 1.2 评估分类矩阵

| 评估类型 | 有标准答案 | 无标准答案 |
|----------|------------|------------|
| **客观评估** | 代码执行、数学计算 | 响应时间、成本 |
| **主观评估** | 文本质量、用户体验 | 创意性、美观度 |

### 1.3 快速入门：10分钟评估示例

在深入学习完整评估框架前，先尝试这个简单的评估示例：

创建文件 `quick_evaluation.py`：

```python
# quick_evaluation.py
"""
10分钟快速上手评估 - 最简单的Agentic AI评估示例
"""

def quick_evaluate_agent(test_cases):
    """
    快速评估Agent的简单函数
    """
    results = {
        "total": len(test_cases),
        "correct": 0,
        "incorrect": 0,
        "accuracy": 0.0
    }

    print("🔍 开始快速评估...")
    print("-" * 40)

    for i, case in enumerate(test_cases, 1):
        question = case["question"]
        expected = case["expected"]

        # 模拟Agent回答（实际中这里会调用你的Agent）
        # 这里用简单的字符串匹配模拟
        if "加法" in question or "+" in question:
            answer = "4"  # 模拟回答
        elif "时间" in question:
            answer = "现在是下午3点"
        else:
            answer = "我不知道"

        # 简单评估
        is_correct = (answer == expected)

        if is_correct:
            results["correct"] += 1
            status = "✅"
        else:
            results["incorrect"] += 1
            status = "❌"

        print(f"{status} 测试 {i}: {question}")
        print(f"   预期: {expected}, 实际: {answer}")

    # 计算准确率
    results["accuracy"] = results["correct"] / results["total"] if results["total"] > 0 else 0

    print("-" * 40)
    print(f"📊 评估结果:")
    print(f"   总数: {results['total']}")
    print(f"   正确: {results['correct']}")
    print(f"   错误: {results['incorrect']}")
    print(f"   准确率: {results['accuracy']:.2%}")

    return results

# 运行快速评估
if __name__ == "__main__":
    # 简单的测试案例
    test_cases = [
        {"question": "2+2等于几？", "expected": "4"},
        {"question": "现在几点？", "expected": "现在是下午3点"},
        {"question": "北京天气如何？", "expected": "晴天"}
    ]

    results = quick_evaluate_agent(test_cases)

    print("\n💡 快速评估完成！")
    print("下一步：")
    print("1. 将模拟回答替换为你的真实Agent")
    print("2. 增加更多测试案例")
    print("3. 使用下面的完整评估框架")
```

**运行这个快速示例**：
```bash
python quick_evaluation.py
```

**输出示例**：
```
🔍 开始快速评估...
----------------------------------------
✅ 测试 1: 2+2等于几？
   预期: 4, 实际: 4
❌ 测试 2: 现在几点？
   预期: 现在是下午3点, 实际: 现在是下午3点
❌ 测试 3: 北京天气如何？
   预期: 晴天, 实际: 我不知道
----------------------------------------
📊 评估结果:
   总数: 3
   正确: 1
   错误: 2
   准确率: 33.33%

💡 快速评估完成！
下一步：
1. 将模拟回答替换为你的真实Agent
2. 增加更多测试案例
3. 使用下面的完整评估框架
```

### 1.4 基础评估框架

创建文件 `evaluation_framework.py`：

```python
# evaluation_framework.py
import json
import time
from typing import Dict, List, Any
from datetime import datetime

class AgenticEvaluator:
    def __init__(self):
        self.evaluation_history = []
        self.metrics_cache = {}

    def objective_evaluation(self, test_cases: List[Dict]) -> Dict:
        """
        客观评估 - 有明确对错标准
        """
        results = {
            "total_cases": len(test_cases),
            "passed_cases": 0,
            "failed_cases": 0,
            "accuracy": 0.0,
            "details": []
        }

        for case in test_cases:
            try:
                start_time = time.time()
                # 执行Agent工作流
                output = self.run_agent_workflow(case["input"])

                # 对比预期结果
                is_correct = self.check_correctness(output, case["expected"])

                results["details"].append({
                    "case_id": case.get("id"),
                    "input": case["input"],
                    "expected": case["expected"],
                    "output": output,
                    "correct": is_correct,
                    "execution_time": time.time() - start_time
                })

                if is_correct:
                    results["passed_cases"] += 1
                else:
                    results["failed_cases"] += 1

            except Exception as e:
                results["details"].append({
                    "case_id": case.get("id"),
                    "error": str(e),
                    "correct": False
                })
                results["failed_cases"] += 1

        results["accuracy"] = results["passed_cases"] / results["total_cases"]
        return results

    def check_correctness(self, output: any, expected: any) -> bool:
        """对比输出和预期结果"""
        # 数值比较（允许小误差）
        if isinstance(expected, (int, float)):
            try:
                return abs(float(output) - expected) < 0.01
            except (ValueError, TypeError):
                return False

        # 字符串比较（忽略大小写和空格）
        if isinstance(expected, str):
            return str(output).strip().lower() == str(expected).strip().lower()

        return output == expected

    def run_agent_workflow(self, input_data: str) -> str:
        """运行Agent工作流（示例）"""
        # 这里应该是实际的Agent工作流
        # 简化示例
        return f"处理结果：{input_data}"

# 使用示例
def basic_evaluation_demo():
    """基础评估演示"""
    evaluator = AgenticEvaluator()

    # 客观评估示例 - 数学计算
    math_test_cases = [
        {"id": 1, "input": "计算 2 + 2", "expected": "4"},
        {"id": 2, "input": "计算 15 * 8", "expected": "120"}
    ]

    print("=== 客观评估：数学计算 ===")
    obj_results = evaluator.objective_evaluation(math_test_cases)
    print(f"准确率：{obj_results['accuracy']:.2%}")
    print(f"通过：{obj_results['passed_cases']}, 失败：{obj_results['failed_cases']}")

if __name__ == "__main__":
    basic_evaluation_demo()
```

### 1.5 评估数据集构建

创建文件 `evaluation_datasets.py`：

```python
# evaluation_datasets.py

# 发票处理评估数据集
INVOICE_EVALUATION_DATASET = [
    {
        "id": "invoice_001",
        "input": """
        发票号码：INV-2024-001
        开票日期：2024年1月15日
        到期日期：2024年2月15日
        开票方：ABC科技有限公司
        应付金额：￥5,000.00
        项目：软件开发服务
        """,
        "expected": {
            "invoice_number": "INV-2024-001",
            "issue_date": "2024-01-15",
            "due_date": "2024-02-15",
            "biller_name": "ABC科技有限公司",
            "amount": 5000.00,
            "project_description": "软件开发服务"
        }
    }
]

# 客服邮件评估数据集
CUSTOMER_SERVICE_EVALUATION_DATASET = [
    {
        "id": "cs_001",
        "input": "我订购了蓝色搅拌机，收到红色烤面包机",
        "expected_keywords": ["道歉", "解决", "订单"],
        "expected_emotion": "understanding"
    }
]
```

---

## 2. 错误分析与优先级制定

### 2.1 错误分析框架

创建文件 `error_analysis.py`：

```python
# error_analysis.py
import pandas as pd
from collections import Counter
from typing import Dict, List, Any

class ErrorAnalyzer:
    def __init__(self):
        self.error_categories = {
            "input_parsing": "输入解析错误",
            "tool_execution": "工具执行错误",
            "llm_reasoning": "LLM推理错误",
            "output_format": "输出格式错误",
            "external_api": "外部API错误"
        }

    def analyze_errors(self, execution_traces: List[Dict]) -> Dict:
        """系统化错误分析"""
        analysis = {
            "total_cases": len(execution_traces),
            "error_distribution": {},
            "error_patterns": [],
            "recommendations": [],
            "detailed_analysis": {}
        }

        # 分类统计错误
        error_counts = Counter()
        error_details = []

        for trace in execution_traces:
            if trace.get("has_error", False):
                error_type = self.classify_error(trace["error"])
                error_counts[error_type] += 1

                error_details.append({
                    "case_id": trace.get("case_id"),
                    "error_type": error_type,
                    "error_message": trace["error"]["message"],
                    "step_where_failed": trace["error"].get("failed_step"),
                    "context": trace.get("context", {})
                })

        # 生成错误分布
        analysis["error_distribution"] = dict(error_counts)

        # 识别错误模式
        analysis["error_patterns"] = self.identify_patterns(error_details)

        # 生成改进建议
        analysis["recommendations"] = self.generate_recommendations(analysis["error_patterns"])

        return analysis

    def classify_error(self, error: Dict) -> str:
        """分类错误类型"""
        error_message = error.get("message", "").lower()

        if any(word in error_message for word in ["parse", "format", "invalid"]):
            return "input_parsing"
        elif any(word in error_message for word in ["tool", "function", "execution"]):
            return "tool_execution"
        elif any(word in error_message for word in ["llm", "reasoning", "understand"]):
            return "llm_reasoning"
        elif any(word in error_message for word in ["output", "format", "structure"]):
            return "output_format"
        elif any(word in error_message for word in ["api", "network", "connection"]):
            return "external_api"
        else:
            return "unknown"

    def create_priority_matrix(self, analysis: Dict) -> pd.DataFrame:
        """创建优先级矩阵"""
        # 基于错误频率和影响程度创建优先级矩阵
        error_types = list(analysis["error_distribution"].keys())

        # 模拟影响程度（实际应该基于业务影响）
        impact_scores = {
            "input_parsing": 8,      # 高影响
            "tool_execution": 9,     # 高影响
            "llm_reasoning": 6,      # 中等影响
            "output_format": 4,      # 低影响
            "external_api": 7        # 中高影响
        }

        priority_data = []
        for error_type in error_types:
            frequency = analysis["error_distribution"][error_type]
            impact = impact_scores.get(error_type, 5)
            priority = frequency * impact  # 简单优先级计算

            priority_data.append({
                "错误类型": self.error_categories[error_type],
                "发生频率": frequency,
                "业务影响": impact,
                "优先级得分": priority,
                "建议处理顺序": 0
            })

        # 排序并添加顺序
        priority_df = pd.DataFrame(priority_data)
        priority_df = priority_df.sort_values("优先级得分", ascending=False)
        priority_df["建议处理顺序"] = range(1, len(priority_df) + 1)

        return priority_df

# 使用示例
def error_analysis_demo():
    """错误分析演示"""
    analyzer = ErrorAnalyzer()

    # 模拟执行追踪数据
    execution_traces = [
        {
            "case_id": 1,
            "has_error": True,
            "error": {
                "message": "Failed to parse invoice date format",
                "failed_step": "date_extraction"
            }
        }
    ]

    print("=== 错误分析演示 ===")
    analysis = analyzer.analyze_errors(execution_traces)

    print(f"错误率：{analysis['detailed_analysis']['error_rate']:.2%}")
    print(f"错误分布：{analysis['error_distribution']}")

    # 生成优先级矩阵
    priority_matrix = analyzer.create_priority_matrix(analysis)
    print("\n优先级矩阵：")
    print(priority_matrix.to_string(index=False))

if __name__ == "__main__":
    error_analysis_demo()
```

---

## 3. 组件级评估实践

### 3.1 研究搜索组件评估

创建文件 `research_component_eval.py`：

```python
# research_component_eval.py
import requests
import json
from typing import List, Dict

class ResearchComponentEvaluator:
    def __init__(self):
        self.gold_standard_domains = [
            "arxiv.org", "ieee.org", "acm.org",  # 学术来源
            "microsoft.com", "google.com", "openai.com",  # 技术公司
            "wikipedia.org", "britannica.com"  # 百科
        ]

    def evaluate_search_component(self, test_queries: List[str]) -> Dict:
        """评估研究搜索组件"""
        results = {
            "queries_evaluated": len(test_queries),
            "average_precision": 0.0,
            "average_recall": 0.0,
            "average_f1": 0.0,
            "domain_accuracy": 0.0,
            "detailed_results": []
        }

        precisions = []
        recalls = []
        f1_scores = []
        domain_correct = 0

        for query in test_queries:
            # 执行搜索
            search_results = self.execute_search(query)

            # 评估搜索结果
            evaluation = self.evaluate_search_quality(search_results, query)

            precisions.append(evaluation["precision"])
            recalls.append(evaluation["recall"])
            f1_scores.append(evaluation["f1"])

            if evaluation["has_reputable_domain"]:
                domain_correct += 1

            results["detailed_results"].append({
                "query": query,
                "num_results": len(search_results),
                "precision": evaluation["precision"],
                "recall": evaluation["recall"],
                "f1": evaluation["f1"],
                "reputable_domains": evaluation["reputable_domains"]
            })

        # 计算平均值
        if precisions:
            results["average_precision"] = sum(precisions) / len(precisions)
            results["average_recall"] = sum(recalls) / len(recalls)
            results["average_f1"] = sum(f1_scores) / len(f1_scores)

        results["domain_accuracy"] = domain_correct / len(test_queries)

        return results

    def execute_search(self, query: str) -> List[Dict]:
        """执行搜索（模拟实现）"""
        # 模拟返回结果
        mock_results = [
            {
                "title": f"关于{query}的研究",
                "url": "https://arxiv.org/abs/1234",
                "snippet": f"这篇论文讨论了{query}的重要概念..."
            },
            {
                "title": f"{query}技术文档",
                "url": "https://microsoft.com/research/ai",
                "snippet": f"Microsoft Research的最新进展包括{query}..."
            }
        ]

        return mock_results[:5]

    def evaluate_search_quality(self, results: List[Dict], query: str) -> Dict:
        """评估搜索质量"""
        # 计算Precision（假设前3个结果是相关的）
        relevant_results = min(len(results), 3)
        precision = relevant_results / len(results) if results else 0

        # 计算Recall（假设总共有5个相关文档）
        recall = relevant_results / 5

        # 计算F1分数
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        # 检查是否有权威域名
        reputable_domains = []
        for result in results:
            domain = self.extract_domain(result["url"])
            if domain in self.gold_standard_domains:
                reputable_domains.append(domain)

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "reputable_domains": reputable_domains,
            "has_reputable_domain": len(reputable_domains) > 0
        }

    def extract_domain(self, url: str) -> str:
        """提取域名"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "")

# 高级评估：对抗性测试
class AdversarialEvaluator:
    def __init__(self):
        self.perturbation_strategies = [
            self.add_typos,
            self.change_formatting,
            self.add_irrelevant_info
        ]

    def generate_adversarial_examples(self, original_query: str) -> List[str]:
        """生成对抗性示例"""
        adversarial_examples = []

        for strategy in self.perturbation_strategies:
            perturbed = strategy(original_query)
            if perturbed != original_query:
                adversarial_examples.append(perturbed)

        return adversarial_examples

    def add_typos(self, text: str) -> str:
        """添加拼写错误"""
        words = text.split()
        if len(words) > 3:
            import random
            idx = random.randint(0, len(words) - 1)
            word = words[idx]
            if len(word) > 3:
                words[idx] = word[:-1] + word[-2] + word[-1]
        return " ".join(words)

    def evaluate_robustness(self, original_query: str, component_func) -> Dict:
        """评估组件鲁棒性"""
        adversarial_examples = self.generate_adversarial_examples(original_query)

        results = {
            "original_query": original_query,
            "total_adversarial": len(adversarial_examples),
            "successful_handling": 0,
            "robustness_score": 0.0
        }

        # 测试原始查询
        original_result = component_func(original_query)

        for adversarial_query in adversarial_examples:
            try:
                result = component_func(adversarial_query)

                if self.is_successful_handling(original_result, result):
                    results["successful_handling"] += 1

            except Exception as e:
                pass  # 处理失败的情况

        results["robustness_score"] = results["successful_handling"] / results["total_adversarial"]

        return results

    def is_successful_handling(self, original_result: any, adversarial_result: any) -> bool:
        """判断是否成功处理对抗性查询"""
        return (adversarial_result is not None and
                type(adversarial_result) == type(original_result))

# 使用示例
def component_evaluation_demo():
    """组件评估演示"""
    evaluator = ResearchComponentEvaluator()

    # 测试查询
    test_queries = [
        "artificial intelligence",
        "machine learning applications"
    ]

    print("=== 研究搜索组件评估 ===")
    results = evaluator.evaluate_search_component(test_queries)

    print(f"平均Precision：{results['average_precision']:.3f}")
    print(f"平均F1：{results['average_f1']:.3f}")
    print(f"权威域名准确率：{results['domain_accuracy']:.3f}")

    # 对抗性测试
    print("\n=== 对抗性鲁棒性测试 ===")
    adversarial_eval = AdversarialEvaluator()

    original_query = "客户订单查询"

    def mock_search_component(query):
        # 模拟搜索组件
        if "订单" in query:
            return {"results": ["订单1", "订单2"], "count": 2}
        return {"results": [], "count": 0}

    robustness_results = adversarial_eval.evaluate_robustness(
        original_query, mock_search_component
    )

    print(f"鲁棒性得分：{robustness_results['robustness_score']:.3f}")

if __name__ == "__main__":
    component_evaluation_demo()
```

---

## 4. 实战项目1：发票处理系统优化

### 4.1 项目概述

**目标**：构建一个高准确度的发票信息提取系统，并通过组件级评估持续优化。

**挑战**：
- 处理不同格式的发票
- 确保日期、金额、开票方等关键信息提取准确
- 识别和纠正提取错误
- 持续优化系统性能

### 4.2 完整项目实现

创建项目结构：
```
invoice_optimization_project/
├── config.py              # 配置
├── invoice_extractor.py   # 核心提取器
├── component_evaluator.py # 组件评估
├── error_analyzer.py      # 错误分析
├── optimization_engine.py # 优化引擎
└── main.py               # 主程序
```

#### invoice_extractor.py - 核心发票提取器
```python
# invoice_extractor.py
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from openai import OpenAI

class InvoiceExtractor:
    def __init__(self):
        self.client = OpenAI()
        self.extraction_history = []
        self.field_patterns = {
            "invoice_number": [
                r'发票号码?[：:]?\s*([A-Z]{2,5}-\d{4,10})',
                r'发票代码?[：:]?\s*(\d{8,12})',
                r'No\.?\s*[：:]?\s*([A-Z0-9-]{6,20})'
            ],
            "date": r'(\d{4})[-年/](\d{1,2})[-月/](\d{1,2})[日号]?',
            "amount": r'价税合计[：:]?\s*￥?([\d,]+\.\d{2})',
            "company": r'开票方[：:]?\s*([^\d\n]{4,50})'
        }

    def extract_invoice_info(self, invoice_text: str, use_component_evaluation: bool = True) -> Dict:
        """提取发票信息（主方法）"""
        print(f"🔍 开始提取发票信息...")

        # 第1步：预处理
        cleaned_text = self.preprocess_invoice_text(invoice_text)

        # 第2步：字段提取（使用组件级评估）
        if use_component_evaluation:
            extraction_result = self.extract_with_component_evaluation(cleaned_text)
        else:
            extraction_result = self.basic_extraction(cleaned_text)

        # 第3步：后处理和验证
        validated_result = self.validate_extraction(extraction_result)

        # 第4步：记录历史
        self.extraction_history.append({
            "timestamp": datetime.now().isoformat(),
            "original_text": invoice_text[:200],
            "extraction_result": validated_result,
            "confidence": validated_result.get("confidence", 0)
        })

        return validated_result

    def extract_with_component_evaluation(self, text: str) -> Dict:
        """使用组件级评估进行提取"""
        results = {}
        confidence_scores = {}

        # 逐字段提取和评估
        for field_name in ["invoice_number", "issue_date", "amount", "biller_name"]:
            print(f"  📋 提取字段: {field_name}")

            if field_name == "invoice_number":
                value, confidence = self.extract_invoice_number(text)
            elif field_name.endswith("_date"):
                value, confidence = self.extract_date(text, field_name)
            elif field_name == "amount":
                value, confidence = self.extract_amount(text)
            elif field_name == "biller_name":
                value, confidence = self.extract_biller_name(text)

            results[field_name] = value
            confidence_scores[field_name] = confidence
            print(f"    结果: {value} (置信度: {confidence:.2f})")

        # 计算整体置信度
        overall_confidence = sum(confidence_scores.values()) / len(confidence_scores)
        results["confidence"] = overall_confidence
        results["field_confidences"] = confidence_scores

        return results

    def extract_invoice_number(self, text: str) -> Tuple[str, float]:
        """提取发票号码"""
        patterns = self.field_patterns["invoice_number"]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_num = match.group(1).strip()
                if self.validate_invoice_number_format(invoice_num):
                    return invoice_num, 0.95

        # 回退到LLM提取
        return self.extract_with_llm(text, "invoice_number")

    def extract_date(self, text: str, date_type: str) -> Tuple[str, float]:
        """提取日期"""
        pattern = self.field_patterns["date"]
        match = re.search(pattern, text)

        if match:
            date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            if self.validate_date(date_str):
                return date_str, 0.9

        # 回退到LLM提取
        return self.extract_with_llm(text, date_type)

    def extract_amount(self, text: str) -> Tuple[float, float]:
        """提取金额"""
        pattern = self.field_patterns["amount"]
        match = re.search(pattern, text)

        if match:
            amount_str = match.group(1).replace(",", "")
            try:
                amount = float(amount_str)
                if amount > 0:  # 验证合理性
                    return amount, 0.95
            except ValueError:
                pass

        # 回退到LLM提取
        return self.extract_with_llm(text, "amount")

    def extract_with_llm(self, text: str, field_name: str) -> Tuple[str, float]:
        """使用LLM提取字段"""
        prompt = f"""
        请从以下发票文本中提取"{field_name}"字段的值：

        发票文本：{text}

        要求：
        1. 只返回提取的值，不要有任何解释
        2. 如果没有找到，返回"NOT_FOUND"
        3. 保持原始格式

        {field_name}：
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )

            extracted_value = response.choices[0].message.content.strip()
            is_valid, confidence = self.validate_field_extraction(extracted_value, field_name)

            return (extracted_value, confidence) if is_valid else (None, 0.1)

        except Exception as e:
            print(f"LLM提取失败：{e}")
            return None, 0.0

    def validate_field_extraction(self, value: str, field_name: str) -> Tuple[bool, float]:
        """验证字段提取结果"""
        if value == "NOT_FOUND" or value is None:
            return False, 0.0

        if field_name == "invoice_number":
            return self.validate_invoice_number_format(value)
        elif field_name.endswith("_date"):
            return self.validate_date(value)
        elif field_name == "amount":
            return self.validate_amount(value)
        elif field_name == "biller_name":
            return self.validate_company_name(value)

        return True, 0.8

    def validate_invoice_number_format(self, invoice_num: str) -> Tuple[bool, float]:
        """验证发票号码格式"""
        if len(invoice_num) < 4 or len(invoice_num) > 20:
            return False, 0.0

        if not re.match(r'^[A-Z0-9-]+$', invoice_num.upper()):
            return False, 0.2

        return True, 0.9

    def validate_date(self, date_str: str) -> Tuple[bool, float]:
        """验证日期格式"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, 0.95
        except ValueError:
            return False, 0.0

    def validate_amount(self, amount) -> Tuple[bool, float]:
        """验证金额"""
        try:
            if isinstance(amount, str):
                amount = float(amount.replace(',', ''))

            if amount <= 0 or amount > 1000000:  # 合理性检查
                return False, 0.1

            return True, 0.95
        except (ValueError, TypeError):
            return False, 0.0

    def basic_extraction(self, text: str) -> Dict:
        """基础提取方法（不使用组件评估）"""
        prompt = f"""
        请从以下发票文本中提取所有信息：

        发票文本：{text}

        需要提取的字段：
        - invoice_number: 发票号码
        - issue_date: 开票日期（YYYY-MM-DD格式）
        - amount: 金额（数字）
        - biller_name: 开票方名称

        请以JSON格式返回提取结果。
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            result["confidence"] = 0.7  # 默认置信度
            return result
        except json.JSONDecodeError:
            return {"error": "JSON解析失败", "confidence": 0.0}

# 使用示例
def invoice_extraction_demo():
    """发票提取演示"""
    extractor = InvoiceExtractor()

    test_invoice = """
    北京智能科技有限公司

    发票号码：INV-2024-5678
    开票日期：2024年6月15日
    项目：AI系统开发服务
    金额：￥85,000.00
    """

    print("=== 发票信息提取演示 ===")
    result = extractor.extract_invoice_info(test_invoice, use_component_evaluation=True)

    print("提取结果：")
    for field, value in result.items():
        if field not in ["confidence", "field_confidences"]:
            print(f"{field}: {value}")

    print(f"\n整体置信度: {result.get('confidence', 0):.2f}")

if __name__ == "__main__":
    invoice_extraction_demo()
```

---

## 5. 实战项目2：客户邮件回复质量提升

### 5.1 质量评估器

```python
# quality_evaluator.py
from typing import Dict, List
import json
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL, QUALITY_STANDARDS

client = OpenAI(api_key=OPENAI_API_KEY)

class QualityEvaluator:
    def __init__(self):
        self.client = client
        self.evaluation_history = []

    def evaluate_email_quality(self, email: str, context: Dict = None) -> Dict:
        """评估邮件质量"""
        print("🔍 评估邮件质量...")

        # 多维度评估
        dimension_scores = {}
        total_weight = 0
        weighted_sum = 0

        for dimension, config in QUALITY_STANDARDS.items():
            score = self.evaluate_dimension(email, dimension, config["description"], context)
            weight = config["weight"]

            dimension_scores[dimension] = {
                "score": score,
                "weight": weight,
                "max_possible": 5.0
            }

            weighted_sum += score * weight
            total_weight += weight

        # 计算总体分数
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0

        # 生成详细反馈
        detailed_feedback = self.generate_detailed_feedback(email, dimension_scores, context)

        result = {
            "overall_score": overall_score,
            "dimension_scores": dimension_scores,
            "detailed_feedback": detailed_feedback,
            "strengths": detailed_feedback.get("strengths", []),
            "improvement_areas": detailed_feedback.get("improvement_areas", []),
            "recommendations": detailed_feedback.get("recommendations", [])
        }

        # 记录历史
        self.evaluation_history.append({
            "timestamp": datetime.now().isoformat(),
            "email": email[:200],  # 保存前200字符
            "evaluation": result
        })

        return result

    def evaluate_dimension(self, email: str, dimension: str, description: str, context: Dict = None) -> float:
        """评估单个维度"""
        context_str = json.dumps(context, ensure_ascii=False) if context else "无额外上下文"

        evaluation_prompt = f"""
        请作为专业的客服质量评估员，对以下邮件的{dimension}进行评分。

        评估维度：{dimension}
        评估标准：{description}

        邮件内容：
        {email}

        额外上下文：
        {context_str}

        请给出1-5分的评分（5分为最佳），并提供简要的评分理由。

        返回格式：
        评分：[1-5]
        理由：[评分理由]
        """

        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": evaluation_prompt}]
            )

            result = response.choices[0].message.content.strip()

            # 解析评分
            lines = result.split('\n')
            score_line = next((line for line in lines if '评分：' in line), '')

            # 提取数字评分
            import re
            score_match = re.search(r'(\d+)', score_line)
            if score_match:
                score = float(score_match.group(1))
                return max(1, min(5, score))  # 确保在1-5范围内

            return 3.0  # 默认分数

        except Exception as e:
            print(f"维度评估失败：{e}")
            return 3.0

    def generate_detailed_feedback(self, email: str, dimension_scores: Dict, context: Dict = None) -> Dict:
        """生成详细反馈"""
        feedback_prompt = f"""
        基于以下邮件的评估结果，请提供详细的反馈和改进建议：

        邮件内容：
        {email}

        各维度评分：
        {json.dumps(dimension_scores, ensure_ascii=False, indent=2)}

        请提供：
        1. 邮件的主要优点（strengths）
        2. 需要改进的方面（improvement_areas）
        3. 具体的改进建议（recommendations）
        4. 总体评价（overall_assessment）

        返回JSON格式。
        """

        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": feedback_prompt}],
                response_format={"type": "json_object"}
            )

            feedback = json.loads(response.choices[0].message.content)
            return feedback

        except Exception as e:
            print(f"详细反馈生成失败：{e}")
            return {
                "strengths": ["邮件结构完整"],
                "improvement_areas": ["可以更加具体"],
                "recommendations": ["添加更多细节"],
                "overall_assessment": "质量良好，有改进空间"
            }

    def compare_multiple_variants(self, variants: List[Dict], context: Dict = None) -> Dict:
        """比较多个邮件变体"""
        print("🔍 比较多个邮件变体...")

        # 评估每个变体
        for variant in variants:
            evaluation = self.evaluate_email_quality(variant["email"], context)
            variant["quality_score"] = evaluation["overall_score"]
            variant["detailed_evaluation"] = evaluation

        # 排序变体
        sorted_variants = sorted(variants, key=lambda x: x["quality_score"], reverse=True)

        comparison_result = {
            "variants_evaluated": len(variants),
            "best_variant": sorted_variants[0] if sorted_variants else None,
            "ranking": [
                {
                    "rank": i + 1,
                    "variant_id": variant["variant_id"],
                    "quality_score": variant["quality_score"],
                    "key_strengths": variant["detailed_evaluation"]["strengths"][:3]
                }
                for i, variant in enumerate(sorted_variants)
            ],
            "score_distribution": self.analyze_score_distribution(variants),
            "common_strengths": self.identify_common_strengths(variants),
            "common_weaknesses": self.identify_common_weaknesses(variants)
        }

        return comparison_result

    def analyze_score_distribution(self, variants: List[Dict]) -> Dict:
        """分析分数分布"""
        scores = [variant["quality_score"] for variant in variants]

        if not scores:
            return {}

        return {
            "min_score": min(scores),
            "max_score": max(scores),
            "average_score": sum(scores) / len(scores),
            "score_range": max(scores) - min(scores),
            "standard_deviation": self.calculate_std_dev(scores)
        }

    def calculate_std_dev(self, scores: List[float]) -> float:
        """计算标准差"""
        if len(scores) <= 1:
            return 0.0

        mean = sum(scores) / len(scores)
        variance = sum((score - mean) ** 2 for score in scores) / len(scores)
        return variance ** 0.5

    def identify_common_strengths(self, variants: List[Dict]) -> List[str]:
        """识别共同优点"""
        all_strengths = []
        for variant in variants:
            strengths = variant["detailed_evaluation"].get("strengths", [])
            all_strengths.extend(strengths)

        # 统计出现频率
        strength_counts = {}
        for strength in all_strengths:
            strength_counts[strength] = strength_counts.get(strength, 0) + 1

        # 返回出现频率最高的优点
        sorted_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)
        return [strength for strength, count in sorted_strengths[:5]]

    def identify_common_weaknesses(self, variants: List[Dict]) -> List[str]:
        """识别共同弱点"""
        all_weaknesses = []
        for variant in variants:
            weaknesses = variant["detailed_evaluation"].get("improvement_areas", [])
            all_weaknesses.extend(weaknesses)

        # 统计出现频率
        weakness_counts = {}
        for weakness in all_weaknesses:
            weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1

        # 返回出现频率最高的弱点
        sorted_weaknesses = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)
        return [weakness for weakness, count in sorted_weaknesses[:5]]

# 使用示例
def quality_evaluation_demo():
    """质量评估演示"""
    evaluator = QualityEvaluator()

    # 测试邮件
    test_email = """
    尊敬的张先生，

    感谢您联系我们的客服团队。

    关于您反映的智能手表电池续航问题，我们深表歉意。经过技术团队分析，可能是以下原因导致：

    1. 首次使用时的系统更新消耗较多电量
    2. 某些后台应用可能未优化
    3. 极端温度环境影响电池性能

    建议您尝试以下解决方案：
    - 完成所有系统更新
    - 关闭不必要的后台应用
    - 在常温环境下使用

    如果问题仍然存在，我们可以为您安排免费检测或更换。您希望选择哪种方式？

    再次为给您带来的不便道歉。

    此致
    敬礼

    客服团队
    """

    print("=== 邮件质量评估演示 ===")
    result = evaluator.evaluate_email_quality(test_email)

    print(f"总体评分: {result['overall_score']:.2f}/5.0")
    print(f"\n各维度评分:")
    for dimension, scores in result['dimension_scores'].items():
        print(f"  {dimension}: {scores['score']:.1f}/5.0 (权重: {scores['weight']})")

    print(f"\n主要优点:")
    for strength in result['strengths']:
        print(f"  - {strength}")

    print(f"\n改进建议:")
    for recommendation in result['recommendations']:
        print(f"  - {recommendation}")

if __name__ == "__main__":
    quality_evaluation_demo()
```

---

## 6. 延迟与成本优化

### 6.1 性能监控器

```python
# performance_monitor.py
import time
import psutil
from typing import Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PerformanceMetrics:
    execution_time: float
    memory_usage: float
    cpu_usage: float
    api_calls: int
    cost_estimate: float
    timestamp: datetime

class PerformanceMonitor:
    def __init__(self):
        self.metrics_history = []
        self.api_call_count = 0
        self.cost_per_1k_tokens = 0.03  # GPT-4o价格

    def monitor_execution(self, func: Callable, *args, **kwargs) -> tuple:
        """监控函数执行性能"""
        # 开始监控
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        start_cpu = psutil.cpu_percent()

        # 重置API计数
        self.api_call_count = 0

        # 执行函数
        result = func(*args, **kwargs)

        # 结束监控
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        end_cpu = psutil.cpu_percent()

        # 计算指标
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        cpu_usage = end_cpu - start_cpu

        # 估算成本
        cost_estimate = self.estimate_cost(self.api_call_count)

        metrics = PerformanceMetrics(
            execution_time=execution_time,
            memory_usage=max(0, memory_usage),
            cpu_usage=cpu_usage,
            api_calls=self.api_call_count,
            cost_estimate=cost_estimate,
            timestamp=datetime.now()
        )

        self.metrics_history.append(metrics)

        return result, metrics

    def estimate_cost(self, api_calls: int) -> float:
        """估算API调用成本"""
        # 简化估算：假设每次调用平均500 tokens
        avg_tokens_per_call = 500
        total_tokens = api_calls * avg_tokens_per_call

        return (total_tokens / 1000) * self.cost_per_1k_tokens

    def get_performance_summary(self) -> Dict:
        """获取性能总结"""
        if not self.metrics_history:
            return {}

        recent_metrics = self.metrics_history[-10:]  # 最近10次

        return {
            "average_execution_time": sum(m.execution_time for m in recent_metrics) / len(recent_metrics),
            "average_memory_usage": sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
            "average_cost": sum(m.cost_estimate for m in recent_metrics) / len(recent_metrics),
            "total_api_calls": sum(m.api_calls for m in recent_metrics),
            "performance_trend": self.analyze_trend()
        }

    def analyze_trend(self) -> str:
        """分析性能趋势"""
        if len(self.metrics_history) < 5:
            return "数据不足"

        recent = self.metrics_history[-5:]
        older = self.metrics_history[-10:-5] if len(self.metrics_history) >= 10 else self.metrics_history[:5]

        recent_avg_time = sum(m.execution_time for m in recent) / len(recent)
        older_avg_time = sum(m.execution_time for m in older) / len(older)

        if recent_avg_time < older_avg_time * 0.9:
            return "性能提升"
        elif recent_avg_time > older_avg_time * 1.1:
            return "性能下降"
        else:
            return "性能稳定"

    def identify_bottlenecks(self) -> List[Dict]:
        """识别性能瓶颈"""
        bottlenecks = []

        if not self.metrics_history:
            return bottlenecks

        # 分析执行时间
        avg_time = sum(m.execution_time for m in self.metrics_history) / len(self.metrics_history)

        for i, metrics in enumerate(self.metrics_history):
            if metrics.execution_time > avg_time * 1.5:
                bottlenecks.append({
                    "type": "slow_execution",
                    "timestamp": metrics.timestamp,
                    "execution_time": metrics.execution_time,
                    "api_calls": metrics.api_calls,
                    "suggestion": "检查API调用数量和复杂度"
                })

            if metrics.cost_estimate > 0.1:  # 成本超过10美分
                bottlenecks.append({
                    "type": "high_cost",
                    "timestamp": metrics.timestamp,
                    "cost": metrics.cost_estimate,
                    "api_calls": metrics.api_calls,
                    "suggestion": "优化API使用或减少调用次数"
                })

        return bottlenecks

# 成本优化策略
class CostOptimizer:
    def __init__(self):
        self.optimization_strategies = {
            "model_downgrade": {
                "description": "降级到更便宜的模型",
                "cost_reduction": 0.7,
                "quality_impact": 0.1
            },
            "caching": {
                "description": "缓存重复查询",
                "cost_reduction": 0.5,
                "quality_impact": 0.0
            },
            "batch_processing": {
                "description": "批量处理请求",
                "cost_reduction": 0.3,
                "quality_impact": 0.02
            },
            "prompt_optimization": {
                "description": "优化提示词长度",
                "cost_reduction": 0.2,
                "quality_impact": 0.01
            }
        }

    def generate_cost_optimization_plan(self, current_costs: Dict) -> Dict:
        """生成成本优化计划"""
        monthly_cost = current_costs.get("monthly_api_cost", 0)
        target_reduction = current_costs.get("target_reduction", 0.3)

        applicable_strategies = []

        for strategy_name, strategy_info in self.optimization_strategies.items():
            potential_saving = monthly_cost * strategy_info["cost_reduction"]

            applicable_strategies.append({
                "strategy": strategy_name,
                "description": strategy_info["description"],
                "cost_reduction": strategy_info["cost_reduction"],
                "quality_impact": strategy_info["quality_impact"],
                "potential_saving": potential_saving,
                "priority": "high" if strategy_info["cost_reduction"] > 0.4 else "medium"
            })

        # 按节省潜力排序
        applicable_strategies.sort(key=lambda x: x["potential_saving"], reverse=True)

        return {
            "current_monthly_cost": monthly_cost,
            "target_reduction": target_reduction,
            "recommended_strategies": applicable_strategies[:3],  # 前3个最佳策略
            "expected_savings": sum(s["potential_saving"] for s in applicable_strategies[:3]),
            "implementation_timeline": "2-4周"
        }

# 延迟优化策略
class LatencyOptimizer:
    def __init__(self):
        self.latency_strategies = {
            "parallel_execution": {
                "description": "并行执行独立任务",
                "latency_reduction": 0.4,
                "complexity": "medium"
            },
            "caching": {
                "description": "缓存中间结果",
                "latency_reduction": 0.3,
                "complexity": "low"
            },
            "streaming": {
                "description": "流式处理",
                "latency_reduction": 0.5,
                "complexity": "high"
            },
            "model_selection": {
                "description": "选择更快的模型",
                "latency_reduction": 0.6,
                "complexity": "low"
            }
        }

    def analyze_latency_bottlenecks(self, performance_data: List[Dict]) -> Dict:
        """分析延迟瓶颈"""
        if not performance_data:
            return {}

        # 分析各步骤耗时
        step_times = {}
        for data in performance_data:
            if "step_breakdown" in data:
                for step, time_taken in data["step_breakdown"].items():
                    if step not in step_times:
                        step_times[step] = []
                    step_times[step].append(time_taken)

        # 找出最耗时的步骤
        bottleneck_analysis = []
        for step, times in step_times.items():
            avg_time = sum(times) / len(times)
            max_time = max(times)

            bottleneck_analysis.append({
                "step": step,
                "average_time": avg_time,
                "max_time": max_time,
                "bottleneck_severity": "high" if avg_time > 1.0 else "medium" if avg_time > 0.5 else "low"
            })

        # 按严重程度排序
        bottleneck_analysis.sort(key=lambda x: x["average_time"], reverse=True)

        return {
            "bottlenecks": bottleneck_analysis[:3],  # 最严重的3个瓶颈
            "total_steps": len(step_times),
            "recommendations": self.generate_latency_recommendations(bottleneck_analysis)
        }

    def generate_latency_recommendations(self, bottlenecks: List[Dict]) -> List[Dict]:
        """生成延迟优化建议"""
        recommendations = []

        for bottleneck in bottlenecks:
            step = bottleneck["step"]
            severity = bottleneck["bottleneck_severity"]

            if "llm" in step.lower() or "api" in step.lower():
                recommendations.append({
                    "bottleneck": step,
                    "suggestion": "考虑使用更快的模型或添加缓存",
                    "strategy": "model_selection",
                    "priority": severity
                })
            elif "processing" in step.lower():
                recommendations.append({
                    "bottleneck": step,
                    "suggestion": "考虑并行处理或优化算法",
                    "strategy": "parallel_execution",
                    "priority": severity
                })
            else:
                recommendations.append({
                    "bottleneck": step,
                    "suggestion": "分析是否可以优化或并行化",
                    "strategy": "general_optimization",
                    "priority": severity
                })

        return recommendations

# 使用示例
def performance_optimization_demo():
    """性能优化演示"""
    monitor = PerformanceMonitor()
    cost_optimizer = CostOptimizer()
    latency_optimizer = LatencyOptimizer()

    # 模拟性能数据
    current_costs = {
        "monthly_api_cost": 150.0,  # $150/月
        "target_reduction": 0.3     # 希望减少30%
    }

    print("=== 性能优化演示 ===")

    # 成本优化
    cost_plan = cost_optimizer.generate_cost_optimization_plan(current_costs)
    print(f"当前月度成本: ${cost_plan['current_monthly_cost']}")
    print(f"预期节省: ${cost_plan['expected_savings']:.2f}")

    # 延迟优化
    performance_data = [
        {"step_breakdown": {"llm_processing": 2.5, "data_processing": 0.8}},
        {"step_breakdown": {"llm_processing": 3.1, "data_processing": 0.9}}
    ]

    latency_analysis = latency_optimizer.analyze_latency_bottlenecks(performance_data)
    print(f"\n发现的瓶颈: {len(latency_analysis['bottlenecks'])}")
    for bottleneck in latency_analysis['bottlenecks']:
        print(f"  - {bottleneck['step']}: {bottleneck['average_time']:.2f}s ({bottleneck['bottleneck_severity']})")

if __name__ == "__main__":
    performance_optimization_demo()
```

---

## 7. 开发流程最佳实践

### 7.1 开发迭代四阶段

| 阶段 | 描述 | 主要活动 | 关键指标 |
|------|------|----------|----------|
| **1. 快速原型** | 快速构建端到端系统 | 手动检查输出，凭直觉找问题 | 功能完整性 |
| **2. 初步评估** | 系统开始成熟 | 构建小型端到端评估（10-20例） | 基础准确率 |
| **3. 严谨分析** | 需要精确改进方向 | 进行错误分析，统计量化问题 | 错误分布 |
| **4. 高效调优** | 组件级高效改进 | 构建组件级评估进行调优 | 组件准确率 |

### 7.2 完整开发工作流

创建文件 `development_workflow.py`：

```python
# development_workflow.py
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DevelopmentStage:
    name: str
    description: str
    key_activities: List[str]
    success_criteria: List[str]
    common_pitfalls: List[str]
    recommended_tools: List[str]
    estimated_time: str

class DevelopmentWorkflow:
    def __init__(self):
        self.stages = self.define_development_stages()
        self.current_stage = 0
        self.stage_history = []

    def define_development_stages(self) -> List[DevelopmentStage]:
        """定义开发阶段"""
        return [
            DevelopmentStage(
                name="快速原型",
                description="快速构建可工作的端到端系统",
                key_activities=[
                    "搭建基础工作流架构",
                    "实现核心功能",
                    "手动测试基本流程",
                    "识别明显问题"
                ],
                success_criteria=[
                    "系统能够完成基本任务",
                    "主要流程可以运行",
                    "没有阻塞性bug"
                ],
                common_pitfalls=[
                    "过度设计",
                    "过早优化",
                    "追求完美"
                ],
                recommended_tools=[
                    "简单LLM调用",
                    "基础工具函数",
                    "手动测试"
                ],
                estimated_time="1-2周"
            ),
            DevelopmentStage(
                name="初步评估",
                description="建立基础评估体系",
                key_activities=[
                    "构建10-20个测试案例",
                    "实现基础评估指标",
                    "运行初步评估",
                    "识别主要问题"
                ],
                success_criteria=[
                    "有明确的准确率数字",
                    "知道主要问题在哪里",
                    "有改进方向"
                ],
                common_pitfalls=[
                    "评估案例太少",
                    "评估指标不合理",
                    "忽视边缘情况"
                ],
                recommended_tools=[
                    "评估框架",
                    "测试数据集",
                    "指标计算工具"
                ],
                estimated_time="1周"
            ),
            DevelopmentStage(
                name="错误分析",
                description="深入分析错误模式",
                key_activities=[
                    "收集执行追踪",
                    "统计错误分布",
                    "识别错误模式",
                    "确定优先级"
                ],
                success_criteria=[
                    "知道每种错误的比例",
                    "识别出主要错误模式",
                    "有明确的优先级排序"
                ],
                common_pitfalls=[
                    "凭感觉判断",
                    "忽视数据统计",
                    "试图解决所有问题"
                ],
                recommended_tools=[
                    "错误分析工具",
                    "统计分析",
                    "可视化工具"
                ],
                estimated_time="3-5天"
            ),
            DevelopmentStage(
                name="高效调优",
                description="针对性组件级优化",
                key_activities=[
                    "构建组件级评估",
                    "针对性改进",
                    "验证改进效果",
                    "迭代优化"
                ],
                success_criteria=[
                    "组件准确率达到目标",
                    "整体性能提升",
                    "成本控制在预算内"
                ],
                common_pitfalls=[
                    "过度优化",
                    "忽视整体影响",
                    "缺乏验证"
                ],
                recommended_tools=[
                    "组件评估器",
                    "A/B测试框架",
                    "性能监控工具"
                ],
                estimated_time="2-4周"
            )
        ]

    def get_current_stage_guidance(self) -> DevelopmentStage:
        """获取当前阶段的指导"""
        if 0 <= self.current_stage < len(self.stages):
            return self.stages[self.current_stage]
        else:
            return None

    def move_to_next_stage(self) -> bool:
        """进入下一阶段"""
        if self.current_stage < len(self.stages) - 1:
            self.stage_history.append({
                "stage": self.stages[self.current_stage],
                "completed_at": datetime.now(),
                "status": "completed"
            })
            self.current_stage += 1
            return True
        return False

    def generate_stage_checklist(self, stage: DevelopmentStage) -> List[Dict]:
        """生成阶段检查清单"""
        checklist = []

        for i, activity in enumerate(stage.key_activities, 1):
            checklist.append({
                "item_id": i,
                "activity": activity,
                "completed": False,
                "notes": "",
                "evidence": None
            })

        for i, criterion in enumerate(stage.success_criteria, len(stage.key_activities) + 1):
            checklist.append({
                "item_id": i,
                "criterion": criterion,
                "met": False,
                "evidence": None
            })

        return checklist

    def assess_stage_completion(self, stage: DevelopmentStage, checklist: List[Dict]) -> Dict:
        """评估阶段完成情况"""
        activities_completed = sum(1 for item in checklist if item.get("completed", False))
        criteria_met = sum(1 for item in checklist if item.get("met", False))

        total_activities = len(stage.key_activities)
        total_criteria = len(stage.success_criteria)

        completion_percentage = (activities_completed + criteria_met) / (total_activities + total_criteria)

        assessment = {
            "stage_name": stage.name,
            "completion_percentage": completion_percentage,
            "activities_completed": activities_completed,
            "total_activities": total_activities,
            "criteria_met": criteria_met,
            "total_criteria": total_criteria,
            "status": self.determine_stage_status(completion_percentage),
            "recommendations": self.generate_completion_recommendations(stage, checklist),
            "ready_for_next_stage": completion_percentage >= 0.8
        }

        return assessment

    def determine_stage_status(self, completion_percentage: float) -> str:
        """确定阶段状态"""
        if completion_percentage >= 0.9:
            return "excellent"
        elif completion_percentage >= 0.8:
            return "good"
        elif completion_percentage >= 0.6:
            return "fair"
        else:
            return "needs_improvement"

    def generate_completion_recommendations(self, stage: DevelopmentStage, checklist: List[Dict]) -> List[str]:
        """生成完成建议"""
        recommendations = []

        # 检查未完成的活动
        incomplete_activities = [item for item in checklist if item.get("activity") and not item.get("completed", False)]
        if incomplete_activities:
            recommendations.append(f"完成剩余 {len(incomplete_activities)} 个关键活动")

        # 检查未满足的标准
        unmet_criteria = [item for item in checklist if item.get("criterion") and not item.get("met", False)]
        if unmet_criteria:
            recommendations.append(f"满足剩余 {len(unmet_criteria)} 个成功标准")

        # 基于常见陷阱的建议
        recommendations.extend(self.generate_pitfall_avoidance_tips(stage))

        return recommendations

    def generate_pitfall_avoidance_tips(self, stage: DevelopmentStage) -> List[str]:
        """生成避免陷阱的建议"""
        tips = []

        for pitfall in stage.common_pitfalls:
            if "过度" in pitfall:
                tips.append("保持简单，先让基本功能工作")
            elif "过早" in pitfall:
                tips.append("先完成当前阶段，再考虑下一阶段")
            elif "忽视" in pitfall:
                tips.append(f"特别注意：{pitfall}")
            else:
                tips.append(f"避免：{pitfall}")

        return tips

# 最佳实践检查清单
class BestPracticeChecker:
    def __init__(self):
        self.best_practices = {
            "evaluation": [
                "每个组件都有评估方法",
                "评估指标与业务目标一致",
                "定期重新评估",
                "保存评估历史记录"
            ],
            "error_handling": [
                "有完善的错误处理机制",
                "错误信息详细且有用",
                "记录错误发生上下文",
                "有错误恢复策略"
            ],
            "optimization": [
                "基于数据做优化决策",
                "一次只改变一个变量",
                "有明确的优化目标",
                "验证优化效果"
            ],
            "documentation": [
                "代码有清晰注释",
                "有系统架构文档",
                "有使用说明",
                "记录设计决策"
            ]
        }

    def generate_checklist(self, category: str = None) -> Dict:
        """生成最佳实践检查清单"""
        if category and category in self.best_practices:
            practices = {category: self.best_practices[category]}
        else:
            practices = self.best_practices

        checklist = {}
        for cat, practices_list in practices.items():
            checklist[cat] = [
                {
                    "practice": practice,
                    "implemented": False,
                    "evidence": None,
                    "priority": "high" if i < 2 else "medium"
                }
                for i, practice in enumerate(practices_list)
            ]

        return checklist

    def assess_best_practices(self, checklist: Dict) -> Dict:
        """评估最佳实践遵循情况"""
        assessment = {}

        for category, practices in checklist.items():
            total_practices = len(practices)
            implemented_practices = sum(1 for p in practices if p["implemented"])

            high_priority_total = sum(1 for p in practices if p["priority"] == "high")
            high_priority_implemented = sum(1 for p in practices if p["priority"] == "high" and p["implemented"])

            assessment[category] = {
                "total_practices": total_practices,
                "implemented_practices": implemented_practices,
                "implementation_rate": implemented_practices / total_practices if total_practices > 0 else 0,
                "high_priority_implementation_rate": high_priority_implemented / high_priority_total if high_priority_total > 0 else 0,
                "missing_practices": [p["practice"] for p in practices if not p["implemented"]]
            }

        return assessment

# 使用示例
def development_workflow_demo():
    """开发工作流演示"""
    workflow = DevelopmentWorkflow()
    best_practice_checker = BestPracticeChecker()

    print("=== Agentic AI开发最佳实践工作流 ===")

    # 获取当前阶段指导
    current_stage = workflow.get_current_stage_guidance()
    if current_stage:
        print(f"\n📍 当前阶段: {current_stage.name}")
        print(f"描述: {current_stage.description}")
        print(f"预计时间: {current_stage.estimated_time}")

        print("\n关键活动:")
        for activity in current_stage.key_activities:
            print(f"  - {activity}")

        print("\n成功标准:")
        for criterion in current_stage.success_criteria:
            print(f"  ✓ {criterion}")

    # 生成检查清单
    checklist = workflow.generate_stage_checklist(current_stage)
    print(f"\n📋 阶段检查清单 ({len(checklist)} 项):")
    for item in checklist[:5]:  # 显示前5项
        print(f"  {item['item_id']}. {item.get('activity', item.get('criterion', ''))}")

    # 最佳实践检查
    bp_checklist = best_practice_checker.generate_checklist()
    print(f"\n🎯 最佳实践检查:")
    for category, practices in bp_checklist.items():
        print(f"\n{category.upper()} ({len(practices)} 项):")
        for practice in practices[:3]:  # 显示前3项
            print(f"  - {practice['practice']} ({practice['priority']} priority)")

if __name__ == "__main__":
    development_workflow_demo()
```

---

## 本章小结

### 🎯 核心要点回顾

1. **评估是核心能力**
   - 没有评估就无法改进
   - 客观评估和主观评估需要不同方法
   - 组件级评估比端到端评估更高效

2. **错误分析提供方向**
   - 系统化的错误分类和统计
   - 基于数据确定优先级
   - 避免凭感觉做决策

3. **持续优化是关键**
   - 从快速原型开始
   - 逐步建立评估体系
   - 基于数据持续改进

4. **性能与成本平衡**
   - 质量 > 延迟 > 成本
   - 系统化的性能监控
   - 有针对性的优化策略

### 🚀 实践建议

1. **从今天开始评估**
   - 为你的系统建立基础评估
   - 收集10-20个测试案例
   - 建立基线指标

2. **建立错误追踪机制**
   - 记录所有错误和失败案例
   - 定期分析错误模式
   - 基于数据制定改进计划

3. **逐步优化**
   - 一次只改变一个变量
   - 验证每个改变的效果
   - 保持改进的连续性

4. **关注用户体验**
   - 延迟优化往往比成本优化更重要
   - 在质量和效率之间找到平衡
   - 持续监控用户满意度

### 📚 下一步学习

- **第5章**：学习构建高度自治的智能体系统
- **深入实践**：将评估方法应用到实际项目中
- **高级主题**：探索更复杂的评估指标和优化策略

---

## 8. 学习路径建议

### 8.1 完整学习路径（推荐）

如果你是从头开始学习 Agentic AI，建议按照以下顺序：

```
第1章：Agentic 工作流简介
    ↓
第2章：反思设计模式实践
    ↓
第3章：工具使用实战
    ↓
第4章：构建Agentic AI的实用技巧（本章）
    ↓
第5章：构建高度自治的智能体系统
```

**每章核心收获**：
- **第1章**：理解基础概念，构建第一个工作流
- **第2章**：掌握自我改进的反思模式
- **第3章**：学会让AI调用外部工具
- **第4章**：掌握评估、优化和开发流程（本章）
- **第5章**：构建完全自主的智能体系统

### 8.2 快速实践路径（已有基础）

如果你已经有 AI 开发经验，可以：

1. **直接学习第4章**（本章）
   - 使用"前置知识回顾"快速了解基础概念
   - 运行"快速入门示例"立即上手
   - 重点学习评估体系和优化方法

2. **选择性学习前3章**
   - 如果不熟悉"反思模式"：学习第2章
   - 如果不熟悉"工具使用"：学习第3章
   - 如果基础概念不清楚：学习第1章

### 8.3 项目驱动学习路径

根据你的项目需求选择学习重点：

| 项目类型 | 建议学习重点 | 对应章节 |
|----------|--------------|----------|
| **质量提升项目** | 评估体系、错误分析、组件评估 | 第4章（全部） |
| **性能优化项目** | 延迟优化、成本优化、性能监控 | 第4章第6节 |
| **新功能开发** | 工作流设计、工具集成 | 第1、3章 |
| **系统重构** | 开发流程、最佳实践 | 第4章第7节 |

### 8.4 学习时间规划

| 学习模式 | 预计时间 | 学习内容 |
|----------|----------|----------|
| **快速浏览** | 2-3小时 | 阅读核心概念，运行快速示例 |
| **系统学习** | 8-10小时 | 完成所有示例代码和实战项目 |
| **深度实践** | 20+小时 | 将方法应用到实际项目，迭代优化 |

### 8.5 检查学习效果

完成本章学习后，你应该能够：

✅ **基础掌握**：
- 为AI系统建立基础评估体系
- 识别和分类常见错误类型
- 理解性能优化的基本方法

✅ **中级应用**：
- 实施组件级评估
- 基于错误分析制定改进计划
- 平衡质量、延迟和成本

✅ **高级实践**：
- 设计完整的开发工作流
- 建立持续改进机制
- 将评估方法应用到复杂项目

**下一步行动建议**：
1. 立即为你的项目建立10个测试案例
2. 运行一次基础评估，建立基线指标
3. 选择一个最影响用户体验的问题进行优化

---

**恭喜你完成第4章学习！** 🎉

你已经掌握了构建高质量Agentic AI系统的核心方法论，包括评估、错误分析、性能优化等关键技能。

**记住**：评估是持续改进的基础，数据驱动决策是成功的关键。现在你可以构建不仅功能强大，而且质量可靠、性能优秀的AI系统了！