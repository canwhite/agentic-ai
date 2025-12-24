"""
Chapter draft data model for intermediate results.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DialogueLine(BaseModel):
    """Single line of dialogue."""

    character: str = Field(..., description="Character speaking")
    content: str = Field(..., description="Dialogue content")
    emotion: Optional[str] = Field(None, description="Emotion or tone")
    action: Optional[str] = Field(None, description="Accompanying action")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "character": "林风",
                "content": "这玉佩...似乎蕴含着强大的能量！",
                "emotion": "惊讶",
                "action": "紧紧握住玉佩",
            }
        }


class SceneSegment(BaseModel):
    """Segment of a scene."""

    scene_name: str = Field(..., description="Scene name")
    description: str = Field(..., description="Scene description")
    atmosphere: str = Field(..., description="Atmosphere and mood")
    characters_present: List[str] = Field(
        default_factory=list, description="Characters present in scene"
    )
    key_actions: List[str] = Field(
        default_factory=list, description="Key actions in scene"
    )
    sensory_details: Dict[str, str] = Field(
        default_factory=dict, description="Sensory details"
    )
    duration: Optional[str] = Field(None, description="Scene duration or time span")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "scene_name": "上古秘境核心",
                "description": "秘境最深处，能量最为浓郁的区域",
                "atmosphere": "神圣而危险",
                "characters_present": ["林风"],
                "key_actions": ["探索遗迹", "发现传承", "触发机关"],
                "sensory_details": {
                    "sight": "金色符文在空中流转",
                    "sound": "古老的吟唱声回荡",
                },
                "duration": "约一炷香时间",
            }
        }


class PlotPoint(BaseModel):
    """Key plot point in chapter."""

    point_type: str = Field(
        ..., description="Type of plot point (conflict, revelation, twist, climax, etc.)"
    )
    description: str = Field(..., description="Description of plot point")
    significance: str = Field(..., description="Significance to plot")
    characters_involved: List[str] = Field(
        default_factory=list, description="Characters involved"
    )
    tension_level: int = Field(
        default=5, ge=1, le=10, description="Tension level from 1 to 10"
    )
    is_foreshadowing: bool = Field(False, description="Whether foreshadows future events")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "point_type": "冲突",
                "description": "林风发现玉佩后，神秘黑衣人出现争夺",
                "significance": "引入反派势力，增加剧情张力",
                "characters_involved": ["林风", "黑衣人"],
                "tension_level": 8,
                "is_foreshadowing": True,
            }
        }


class ChapterDraft(BaseModel):
    """Draft structure for chapter generation."""

    # Plot structure
    plot_structure: str = Field(..., description="Overall plot structure")
    plot_points: List[PlotPoint] = Field(
        default_factory=list, description="Key plot points"
    )
    emotional_curve: List[Dict[str, Any]] = Field(
        default_factory=list, description="Emotional curve throughout chapter"
    )
    conflicts: List[str] = Field(default_factory=list, description="Major conflicts")
    cliffhangers: List[str] = Field(default_factory=list, description="Cliffhangers")

    # Character development
    character_arcs: Dict[str, str] = Field(
        default_factory=dict, description="Character development arcs"
    )
    character_interactions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Key character interactions"
    )
    dialogue: List[DialogueLine] = Field(default_factory=list, description="Dialogue lines")

    # Scene descriptions
    scene_segments: List[SceneSegment] = Field(
        default_factory=list, description="Scene segments"
    )
    scene_transitions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Scene transitions"
    )

    # Props and elements
    props_used: List[Dict[str, Any]] = Field(
        default_factory=list, description="Props used in chapter"
    )
    symbolic_elements: List[str] = Field(
        default_factory=list, description="Symbolic elements"
    )

    # Writing style
    writing_style: Dict[str, Any] = Field(
        default_factory=dict, description="Writing style specifications"
    )
    pacing: str = Field(default="中等", description="Pacing (快, 中等, 慢)")
    point_of_view: str = Field(default="第三人称", description="Point of view")

    # Metadata
    estimated_length: int = Field(default=2000, description="Estimated word count")
    chapter_title: Optional[str] = Field(None, description="Chapter title")
    chapter_number: Optional[int] = Field(None, description="Chapter number")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return self.dict()

    def get_plot_summary(self) -> str:
        """Get plot summary.

        Returns:
            Formatted plot summary
        """
        summary = []
        summary.append("情节结构:")
        summary.append(self.plot_structure)
        summary.append("")

        if self.plot_points:
            summary.append("关键情节点:")
            for i, point in enumerate(self.plot_points, 1):
                summary.append(f"{i}. [{point.point_type}] {point.description}")
                summary.append(f"   张力等级: {point.tension_level}/10")
                if point.characters_involved:
                    summary.append(f"   涉及人物: {', '.join(point.characters_involved)}")
                summary.append("")

        if self.conflicts:
            summary.append("主要冲突:")
            for conflict in self.conflicts:
                summary.append(f"- {conflict}")
            summary.append("")

        return "\n".join(summary)

    def get_character_summary(self) -> str:
        """Get character summary.

        Returns:
            Formatted character summary
        """
        summary = []
        if self.character_arcs:
            summary.append("人物发展弧线:")
            for character, arc in self.character_arcs.items():
                summary.append(f"- {character}: {arc}")
            summary.append("")

        if self.dialogue:
            summary.append("关键对话:")
            for dialogue in self.dialogue[:5]:  # Show first 5 dialogues
                emotion_str = f" ({dialogue.emotion})" if dialogue.emotion else ""
                action_str = f" 【{dialogue.action}】" if dialogue.action else ""
                summary.append(f"- {dialogue.character}{emotion_str}: {dialogue.content}{action_str}")
            if len(self.dialogue) > 5:
                summary.append(f"... 还有 {len(self.dialogue) - 5} 条对话")
            summary.append("")

        return "\n".join(summary)

    def get_scene_summary(self) -> str:
        """Get scene summary.

        Returns:
            Formatted scene summary
        """
        summary = []
        if self.scene_segments:
            summary.append("场景安排:")
            for i, scene in enumerate(self.scene_segments, 1):
                summary.append(f"{i}. {scene.scene_name}")
                summary.append(f"   氛围: {scene.atmosphere}")
                if scene.characters_present:
                    summary.append(f"   在场人物: {', '.join(scene.characters_present)}")
                if scene.key_actions:
                    summary.append(f"   关键动作: {', '.join(scene.key_actions[:3])}")
                summary.append("")

        return "\n".join(summary)

    def print_draft_summary(self) -> None:
        """Print draft summary."""
        print("=" * 60)
        print("章节草稿摘要")
        print("=" * 60)

        if self.chapter_title:
            print(f"章节标题: {self.chapter_title}")
        if self.chapter_number:
            print(f"章节编号: 第{self.chapter_number}章")
        print(f"预计字数: {self.estimated_length} 字")
        print(f"叙事视角: {self.point_of_view}")
        print(f"节奏: {self.pacing}")
        print()

        print(self.get_plot_summary())
        print(self.get_character_summary())
        print(self.get_scene_summary())

        if self.props_used:
            print("使用道具:")
            for prop in self.props_used:
                print(f"- {prop.get('name', '未知')}: {prop.get('usage', '')}")

        print("=" * 60)

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "plot_structure": "引入→发展→冲突→高潮→回落",
                "plot_points": [
                    {
                        "point_type": "引入",
                        "description": "林风进入上古秘境",
                        "significance": "建立场景和氛围",
                        "tension_level": 3,
                    }
                ],
                "emotional_curve": [
                    {"segment": "开头", "emotion": "好奇", "intensity": 4},
                    {"segment": "发展", "emotion": "紧张", "intensity": 7},
                ],
                "conflicts": ["人与环境的冲突", "人与人的冲突"],
                "character_arcs": {"林风": "从好奇到决心"},
                "scene_segments": [
                    {
                        "scene_name": "秘境入口",
                        "description": "神秘的能量波动",
                        "atmosphere": "神秘",
                    }
                ],
                "writing_style": {"文风": "热血", "描写": "细腻"},
                "pacing": "中等",
                "point_of_view": "第三人称",
                "estimated_length": 2000,
                "chapter_title": "秘境奇遇",
            }
        }