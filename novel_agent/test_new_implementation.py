"""
测试 Novel Agent 新实现

基于成功模式实现的完整系统测试
"""

import sys
import time
from pathlib import Path

# 添加 src 到路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s (PID %(process)d): %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主测试函数"""
    import sys
    from pathlib import Path

    # 确保 src 在路径中
    src_dir = Path(__file__).parent / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from src.runtime.supervisor import Supervisor
    from src.agents.novel_agent import NovelInput

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
    supervisor = Supervisor(
        min_workers=1,
        max_workers=2,
        worker_max_concurrent=2,
    )

    # 启动 Supervisor（在后台线程）
    supervisor.start(daemon=True)

    logger.info("等待 Workers 启动...")
    time.sleep(2)

    # 提交任务
    logger.info("\n提交测试任务...")
    task_ids = []
    for task in test_tasks:
        task_id = supervisor.submit_task(task)
        task_ids.append(task_id)
        logger.info(f"已提交任务: {task_id}")

    # 收集结果
    logger.info("\n开始收集结果...")
    results = []
    start_time = time.time()
    timeout = 300  # 5分钟超时

    while len(results) < len(task_ids) and (time.time() - start_time) < timeout:
        result = supervisor.get_result(timeout=1.0)
        if result:
            results.append(result)
            logger.info(
                f"\n{'='*60}\n"
                f"收到结果: {result['task_id']}\n"
                f"Worker: {result.get('worker_id', 'Unknown')}\n"
                f"成功: {result['success']}\n"
                f"内容长度: {len(result.get('content', ''))}\n"
                f"执行时间: {result.get('execution_time', 0):.2f}s\n"
                f"{'='*60}\n"
            )

            if result.get('error'):
                logger.error(f"错误信息: {result['error']}")

            if result.get('content'):
                logger.info(f"内容预览: {result['content'][:200]}...")

    # 停止 Supervisor
    logger.info("\n测试完成，停止 Supervisor...")
    supervisor.stop()

    # 输出总结
    logger.info("\n" + "="*60)
    logger.info("测试总结")
    logger.info("="*60)
    logger.info(f"提交任务数: {len(task_ids)}")
    logger.info(f"完成任务数: {len(results)}")
    logger.info(f"总耗时: {time.time() - start_time:.2f}s")

    success_count = sum(1 for r in results if r.get('success'))
    logger.info(f"成功: {success_count}/{len(results)}")

    for result in results:
        status = "✅" if result.get('success') else "❌"
        logger.info(
            f"{status} {result['task_id']} - "
            f"长度={len(result.get('content', ''))}, "
            f"时间={result.get('execution_time', 0):.2f}s"
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n程序被中断")
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)
