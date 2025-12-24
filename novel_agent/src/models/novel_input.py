"""
Novel input data models.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator


class Character(BaseModel):
    """Character definition for novel generation."""

    name: str = Field(..., description="Character name")
    role: str = Field(..., description="Character role (e.g., protagonist, antagonist)")
    personality: str = Field(..., description="Personality traits and characteristics")
    background: str = Field(..., description="Character background and history")
    appearance: Optional[str] = Field(None, description="Physical appearance")
    special_abilities: Optional[List[str]] = Field(
        default_factory=list, description="Special abilities or skills"
    )
    relationships: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Relationships with other characters"
    )
    character_arc: Optional[str] = Field(None, description="Character development arc")
    speech_style: Optional[str] = Field(None, description="Character speech style")
    key_memories: Optional[List[str]] = Field(
        default_factory=list, description="Key memories or experiences"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "name": "林风",
                "role": "主角",
                "personality": "坚韧不拔，机智勇敢，重情重义",
                "background": "普通山村少年，父母早逝，由爷爷抚养长大",
                "appearance": "清秀俊朗，眼神坚毅，身材修长",
                "special_abilities": ["修炼天赋异禀", "过目不忘"],
                "relationships": {"爷爷": "抚养人", "小青": "青梅竹马"},
                "character_arc": "从普通少年成长为一代宗师",
                "speech_style": "简洁有力，偶尔幽默",
                "key_memories": ["爷爷传授修炼心法", "小青离别赠玉"],
            }
        }


class Scene(BaseModel):
    """Scene definition for novel generation."""

    name: str = Field(..., description="Scene name")
    description: str = Field(..., description="Scene description")
    atmosphere: str = Field(..., description="Atmosphere and mood")
    location_type: Optional[str] = Field(None, description="Type of location")
    time_period: Optional[str] = Field(None, description="Time period or era")
    weather: Optional[str] = Field(None, description="Weather conditions")
    key_features: Optional[List[str]] = Field(
        default_factory=list, description="Key features or landmarks"
    )
    sensory_details: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Sensory details (sight, sound, smell, touch, taste)",
    )
    symbolic_elements: Optional[List[str]] = Field(
        default_factory=list, description="Symbolic elements or motifs"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "name": "上古秘境",
                "description": "充满神秘能量的古老遗迹，隐藏着无数秘密",
                "atmosphere": "神秘、危险、机遇并存",
                "location_type": "秘境遗迹",
                "time_period": "上古时代",
                "weather": "雾气弥漫，偶尔有闪电",
                "key_features": ["古老祭坛", "神秘石碑", "能量漩涡"],
                "sensory_details": {
                    "sight": "幽蓝的光芒在石壁上流动",
                    "sound": "低沉的能量嗡鸣声",
                    "smell": "古老的尘土和臭氧混合气味",
                },
                "symbolic_elements": ["传承", "考验", "蜕变"],
            }
        }


class Prop(BaseModel):
    """Prop definition for novel generation."""

    name: str = Field(..., description="Prop name")
    description: str = Field(..., description="Prop description")
    significance: Optional[str] = Field(None, description="Significance to plot")
    is_foreshadowing: bool = Field(False, description="Whether used for foreshadowing")
    magical_properties: Optional[List[str]] = Field(
        default_factory=list, description="Magical or special properties"
    )
    owner: Optional[str] = Field(None, description="Current owner")
    history: Optional[str] = Field(None, description="Historical background")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "name": "神秘玉佩",
                "description": "半透明的青色玉佩，刻有古老符文",
                "significance": "蕴含上古传承的关键",
                "is_foreshadowing": True,
                "magical_properties": ["存储能量", "感应危险", "记录功法"],
                "owner": "林风",
                "history": "上古大能遗留的传承信物",
            }
        }


class NovelInput(BaseModel):
    """Input data for novel chapter generation."""

    overall_outline: str = Field(
        ..., description="Overall novel outline or synopsis"
    )
    chapter_outline: str = Field(
        ..., description="Specific outline for this chapter"
    )
    characters: List[Character] = Field(
        default_factory=list, description="List of characters"
    )
    scenes: List[Scene] = Field(
        default_factory=list, description="List of scenes"
    )
    props: List[Prop] = Field(
        default_factory=list, description="List of props"
    )
    previous_chapter: Optional[str] = Field(
        None, description="Content of previous chapter (if any)"
    )
    genre: str = Field(
        default="玄幻",
        description="Novel genre (e.g., 玄幻, 科幻, 网络小说)",
    )
    style_preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="Style preferences (e.g., writing style, pacing, tone)",
    )
    target_length: Optional[int] = Field(
        None, description="Target chapter length in characters"
    )
    special_requirements: Optional[List[str]] = Field(
        default_factory=list,
        description="Special requirements or constraints",
    )
    emotional_curve: Optional[List[str]] = Field(
        default_factory=list,
        description="Desired emotional curve (e.g., ['平静', '紧张', '高潮', '回落'])",
    )

    @validator("genre")
    def validate_genre(cls, v):
        """Validate genre."""
        valid_genres = ["玄幻", "科幻", "奇幻", "网络小说", "爽文", "武侠", "仙侠"]
        if v not in valid_genres:
            raise ValueError(
                f"Invalid genre: {v}. Valid genres are: {', '.join(valid_genres)}"
            )
        return v

    @validator("target_length")
    def validate_target_length(cls, v):
        """Validate target length."""
        if v is not None and v < 500:
            raise ValueError("Target length must be at least 500 characters")
        if v is not None and v > 10000:
            raise ValueError("Target length must not exceed 10000 characters")
        return v

    def get_character_by_name(self, name: str) -> Optional[Character]:
        """Get character by name.

        Args:
            name: Character name

        Returns:
            Character object if found, None otherwise
        """
        for character in self.characters:
            if character.name == name:
                return character
        return None

    def get_scene_by_name(self, name: str) -> Optional[Scene]:
        """Get scene by name.

        Args:
            name: Scene name

        Returns:
            Scene object if found, None otherwise
        """
        for scene in self.scenes:
            if scene.name == name:
                return scene
        return None

    def get_prop_by_name(self, name: str) -> Optional[Prop]:
        """Get prop by name.

        Args:
            name: Prop name

        Returns:
            Prop object if found, None otherwise
        """
        for prop in self.props:
            if prop.name == name:
                return prop
        return None

    def to_context_dict(self) -> Dict[str, Any]:
        """Convert to context dictionary for agents.

        Returns:
            Dictionary with context information
        """
        return {
            "overall_outline": self.overall_outline,
            "chapter_outline": self.chapter_outline,
            "characters": [char.dict() for char in self.characters],
            "scenes": [scene.dict() for scene in self.scenes],
            "props": [prop.dict() for prop in self.props],
            "previous_chapter": self.previous_chapter,
            "genre": self.genre,
            "style_preferences": self.style_preferences,
            "target_length": self.target_length,
            "special_requirements": self.special_requirements,
            "emotional_curve": self.emotional_curve,
        }

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "overall_outline": "一个少年在玄幻世界修炼成神的故事",
                "chapter_outline": "主角在秘境中意外获得上古传承，引发各方势力争夺",
                "characters": [
                    {
                        "name": "林风",
                        "role": "主角",
                        "personality": "坚韧不拔，机智勇敢",
                        "background": "普通山村少年",
                        "special_abilities": ["修炼天赋异禀"],
                    }
                ],
                "scenes": [
                    {
                        "name": "上古秘境",
                        "description": "充满神秘能量的古老遗迹",
                        "atmosphere": "神秘、危险、机遇并存",
                    }
                ],
                "props": [
                    {
                        "name": "神秘玉佩",
                        "description": "蕴含上古秘密的玉佩",
                        "is_foreshadowing": True,
                    }
                ],
                "genre": "玄幻",
                "style_preferences": {"文风": "热血激昂", "节奏": "快"},
                "emotional_curve": ["平静", "紧张", "高潮", "回落"],
            }
        }