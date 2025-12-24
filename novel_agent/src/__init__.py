"""
Novel Agent - A multi-agent system for novel chapter generation.

This package provides a multi-agent system for generating novel chapters
based on outlines, character settings, scene descriptions, and other inputs.
"""

__version__ = "0.1.0"
__author__ = "Novel Agent Team"
__email__ = "team@example.com"

from .workflows.novel_workflow import NovelWorkflow, WorkflowConfig, WorkflowResult
from .models.novel_input import NovelInput, Character, Scene, Prop
from .models.chapter_result import ChapterResult, ChapterMetadata
from .models.chapter_draft import ChapterDraft, PlotPoint, DialogueLine, SceneSegment

__all__ = [
    "NovelWorkflow",
    "WorkflowConfig",
    "WorkflowResult",
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