"""
Basic usage example for Novel Agent.

This example demonstrates how to use the Novel Agent system to generate
a novel chapter based on input data.
"""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Import directly from modules
from src.models import NovelInput, Character, Scene
from src.workflows.novel_workflow import NovelWorkflow, WorkflowConfig


def create_sample_novel_input() -> NovelInput:
    """Create sample novel input for demonstration.

    Returns:
        NovelInput object with sample data
    """
    # Create characters
    characters = [
        Character(
            name="林风",
            role="主角",
            personality="勇敢、聪明、有正义感，但有时过于冲动",
            background="出身普通家庭，偶然获得神秘力量",
            speech_style="直接、有力，略带幽默",
        ),
        Character(
            name="苏雨",
            role="女主角",
            personality="温柔、善良、聪明，内心坚强",
            background="医学世家出身，医术高超",
            speech_style="温和、体贴，富有同理心",
        ),
        Character(
            name="黑影",
            role="反派",
            personality="阴险、狡诈、野心勃勃",
            background="神秘组织的首领",
            speech_style="低沉、威胁，充满算计",
        ),
    ]

    # Create scenes
    scenes = [
        Scene(
            name="古庙相遇",
            description="深山中的破败古庙，夜晚的烛光摇曳，墙上有神秘符文",
            atmosphere="神秘、紧张",
        ),
        Scene(
            name="力量觉醒",
            description="古庙深处的密室，发光的水晶照亮古老壁画，能量波动强烈",
            atmosphere="震撼、惊奇",
        ),
        Scene(
            name="初次交锋",
            description="古庙外的树林，黎明时分，刀光剑影与法术光芒交错",
            atmosphere="激烈、危险",
        ),
    ]

    # Create novel input
    novel_input = NovelInput(
        genre="玄幻",
        overall_outline="普通青年林风偶然获得神秘力量，卷入正邪之争，与苏雨相识相知，共同对抗黑影组织的阴谋。",
        chapter_outline="林风在古庙中意外获得神秘力量，遭遇苏雨，两人共同对抗突然出现的黑影组织成员。",
        characters=characters,
        scenes=scenes,
        target_length=2500,
        style_preferences={
            "writing_style": "网络小说风格，节奏明快，对话生动",
            "target_audience": "年轻读者，喜欢玄幻、冒险题材",
        },
    )

    return novel_input


def setup_environment() -> None:
    """Setup environment variables for LLM API."""
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        print(f"Using environment file: {env_file}")
    else:
        print("Warning: .env file not found. Using default configuration.")
        print("Please create a .env file with your API keys:")
        print("  DEEPSEEK_API_KEY=your_deepseek_api_key")
        print("  OPENAI_API_KEY=your_openai_api_key (optional)")


def run_basic_example() -> None:
    """Run basic example of novel chapter generation."""
    print("=" * 60)
    print("Novel Agent - Basic Usage Example")
    print("=" * 60)

    # Setup environment
    setup_environment()

    # Create sample novel input
    print("\n1. Creating sample novel input...")
    novel_input = create_sample_novel_input()
    print(f"   Genre: {novel_input.genre}")
    print(f"   Characters: {len(novel_input.characters)}")
    print(f"   Scenes: {len(novel_input.scenes)}")
    print(f"   Target length: {novel_input.target_length} characters")

    # Configure workflow
    print("\n2. Configuring workflow...")
    config = WorkflowConfig(
        llm_provider="deepseek",  # Use DeepSeek API
        temperature=0.7,
        enable_quality_checks=True,
        enable_anti_collapse=True,
        output_format="text",
    )
    print(f"   LLM Provider: {config.llm_provider}")
    print(f"   Quality checks: {config.enable_quality_checks}")
    print(f"   Anti-collapse: {config.enable_anti_collapse}")

    # Create workflow
    print("\n3. Creating workflow instance...")
    workflow = NovelWorkflow(config)
    print(f"   Agents initialized: {len(workflow.agents)}")

    # Execute workflow
    print("\n4. Executing workflow...")
    print("   This may take a few minutes depending on API response times.")
    print("   Workflow steps:")
    print("   1. Director creates creation plan")
    print("   2. Plot designer designs plot structure")
    print("   3. Character agent designs character interactions")
    print("   4. Scene renderer designs scene descriptions")
    print("   5. Writing optimizer improves writing style")
    print("   6. Consistency checker performs quality checks")
    print("   7. Final chapter synthesis")

    result = workflow.execute(novel_input)

    # Display results
    print("\n5. Results:")
    print("=" * 40)

    if result.success:
        print(f"✅ Success! Execution time: {result.execution_time:.2f}s")

        chapter_result = result.chapter_result
        print(f"\n📖 Generated Chapter:")
        print("-" * 40)

        # Display first 500 characters of chapter
        content_preview = chapter_result.content[:500]
        print(content_preview)
        if len(chapter_result.content) > 500:
            print("...")

        print(f"\n📊 Statistics:")
        print(f"   Chapter length: {len(chapter_result.content)} characters")
        print(f"   Format: {chapter_result.format}")

        if chapter_result.metadata:
            print(f"   Genre: {chapter_result.metadata.get('novel_genre', 'N/A')}")
            print(f"   Readability score: {chapter_result.metadata.get('readability_score', {}).get('readability_score', 'N/A')}")

        print(f"\n🤖 Agent Executions:")
        for agent_name, exec_info in result.agent_executions.items():
            status = "✅" if exec_info.get("success", False) else "❌"
            time = exec_info.get("execution_time", 0)
            print(f"   {status} {agent_name}: {time:.2f}s")

        # Save chapter to file
        output_file = "generated_chapter.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(chapter_result.content)
        print(f"\n💾 Chapter saved to: {output_file}")

    else:
        print("❌ Workflow failed!")
        print(f"   Execution time: {result.execution_time:.2f}s")

        if result.errors:
            print("\n❌ Errors:")
            for error in result.errors:
                print(f"   - {error}")

        if result.warnings:
            print("\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"   - {warning}")

    # Display workflow statistics
    stats = workflow.get_execution_stats()
    print(f"\n📈 Workflow Statistics:")
    print(f"   Total executions: {stats['total_executions']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")
    print(f"   Avg. execution time: {stats['avg_execution_time']:.2f}s")
    print(f"   Avg. chapter length: {stats['avg_chapter_length']:.0f} chars")

    print("\n" + "=" * 60)
    print("Example completed! 🎉")
    print("=" * 60)


def run_quick_test() -> None:
    """Run a quick test without API calls."""
    print("\n" + "=" * 60)
    print("Quick Test - System Check")
    print("=" * 60)

    try:
        # Test imports
        from src.models import NovelInput, Character, Scene
        from src.workflows.novel_workflow import NovelWorkflow, WorkflowConfig

        print("✅ All imports successful")

        # Test model creation - use the imported classes
        test_character = Character(
            name="Test",
            role="Test",
            personality="Test",
            background="Test"
        )
        test_scene = Scene(
            name="Test",
            description="Test scene",
            atmosphere="Test"
        )
        test_novel_input = NovelInput(
            genre="玄幻",
            overall_outline="Test",
            chapter_outline="Test",
            characters=[test_character],
            scenes=[test_scene]
        )
        print(f"✅ Model creation test passed: {test_novel_input.genre}")

        # Test workflow creation
        config = WorkflowConfig(llm_provider="deepseek")
        workflow = NovelWorkflow(config)
        print(f"✅ Workflow created with {len(workflow.agents)} agents")

        print("\n✅ System check passed! The Novel Agent system is ready.")
        print("\nTo run the full example with API calls:")
        print("1. Set up your .env file with API keys")
        print("2. Run: python examples/basic_usage.py")

    except Exception as e:
        print(f"❌ System check failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the novel_agent directory")
        print("2. Check that all dependencies are installed: pip install -e .")
        print("3. Verify the project structure is correct")


if __name__ == "__main__":
    # Check if we should run quick test or full example
    import argparse

    parser = argparse.ArgumentParser(description="Novel Agent Example")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run quick system test without API calls",
    )
    args = parser.parse_args()

    if args.test:
        run_quick_test()
    else:
        run_basic_example()