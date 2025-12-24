#!/usr/bin/env python3
"""Test script to verify director agent can parse NovelInput from context."""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from src.models import NovelInput, Character, Scene
from src.agents.director import DirectorAgent

def test_parse_novel_input():
    """Test that director agent can parse NovelInput from context."""
    print("=" * 60)
    print("Testing Director Agent - NovelInput Parsing")
    print("=" * 60)

    # Create sample novel input
    characters = [
        Character(
            name="Test Character",
            role="Protagonist",
            personality="Brave",
            background="Test background",
        )
    ]

    scenes = [
        Scene(
            name="Test Scene",
            description="A test scene",
            atmosphere="Mysterious",
        )
    ]

    novel_input = NovelInput(
        genre="玄幻",
        overall_outline="Test outline",
        chapter_outline="Test chapter outline",
        characters=characters,
        scenes=scenes,
        style_preferences={
            "writing_style": "网络小说风格",
            "target_audience": "年轻读者",
        },
    )

    print(f"\n✅ Created NovelInput:")
    print(f"   Genre: {novel_input.genre}")
    print(f"   Characters: {len(novel_input.characters)}")
    print(f"   Scenes: {len(novel_input.scenes)}")

    # Create director agent
    director = DirectorAgent(llm_provider="deepseek")
    print(f"\n✅ Created Director Agent")

    # Test parsing with NovelInput in context
    context = {"novel_input": novel_input}
    print(f"\n📋 Testing parsing with context keys: {list(context.keys())}")

    try:
        parsed_input = director._parse_novel_input(context)
        print(f"✅ Successfully parsed NovelInput from context")
        print(f"   Genre: {parsed_input.genre}")
        print(f"   Character count: {len(parsed_input.characters)}")
        print(f"   Scene count: {len(parsed_input.scenes)}")

        # Verify it's the same object
        assert parsed_input is novel_input, "Parsed input should be the same object"
        print(f"✅ Verified: Parsed input is the same object as original")

    except Exception as e:
        print(f"❌ Failed to parse NovelInput: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test JSON serialization for LLM context
    print(f"\n📋 Testing JSON serialization for LLM context...")
    try:
        messages = director._prepare_messages("Test task", context)
        print(f"✅ Successfully prepared messages for LLM")
        print(f"   System message length: {len(messages[0]['content'])}")
        print(f"   User message length: {len(messages[1]['content'])}")

    except Exception as e:
        print(f"❌ Failed to prepare messages: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("All tests passed! ✅")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_parse_novel_input()
    sys.exit(0 if success else 1)
