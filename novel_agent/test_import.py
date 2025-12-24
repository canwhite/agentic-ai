#!/usr/bin/env python3
"""Simple import test for novel_agent."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    # Test importing from src
    import src
    print("✅ src imported successfully")

    # Test importing models
    from src.models import NovelInput, Character, Scene
    print("✅ Models imported successfully")

    # Test creating objects
    character = Character(
        name="Test",
        role="Test",
        personality="Test",
        background="Test"
    )
    scene = Scene(
        name="Test",
        location="Test",
        time="Test"
    )
    novel_input = NovelInput(
        genre="Test",
        overall_outline="Test",
        chapter_outline="Test",
        characters=[character],
        scenes=[scene]
    )
    print(f"✅ Objects created: {novel_input.genre}")

    # Test importing workflows
    from src.workflows import NovelWorkflow, WorkflowConfig
    print("✅ Workflows imported successfully")

    # Test creating workflow
    config = WorkflowConfig(llm_provider="deepseek")
    workflow = NovelWorkflow(config)
    print(f"✅ Workflow created with {len(workflow.agents)} agents")

    print("\n🎉 All tests passed! The system is working correctly.")

except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)