"""
Data models for Novel Agent.
"""

from .novel_input import NovelInput, Character, Scene, Prop
from .chapter_result import ChapterResult, ChapterMetadata
from .chapter_draft import ChapterDraft, PlotPoint, DialogueLine, SceneSegment

__all__ = [
    "NovelInput",
    "Character",
    "Scene",
    "Prop",
    "ChapterResult",
    "ChapterMetadata",
    "ChapterDraft",
    "PlotPoint",
    "DialogueLine",
    "SceneSegment",
]