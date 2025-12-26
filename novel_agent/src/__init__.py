"""
Novel Agent - A multi-agent system for novel chapter generation.

This package provides a multi-agent system for generating novel chapters
based on outlines, character settings, scene descriptions, and other inputs.
"""

__version__ = "0.1.0"
__author__ = "Novel Agent Team"
__email__ = "team@example.com"

# Import main classes for easier access
from src.agents.novel_agent import NovelAgent, NovelInput, ChapterResult
from src.runtime.supervisor import Supervisor

__all__ = [
    "NovelAgent",
    "NovelInput",
    "ChapterResult",
    "Supervisor",
]