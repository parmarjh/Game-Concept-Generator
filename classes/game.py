import sqlite3
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict
from datetime import datetime
import uuid

# Expanded Enums
class ProjectType(Enum):
    ACTION = "action"
    RPG = "rpg"
    STRATEGY = "strategy"
    ADVENTURE = "adventure"
    PLATFORMER = "platformer"
    PUZZLE = "puzzle"
    SIMULATION = "simulation"
    HORROR = "horror"
    RACING = "racing"
    FIGHTING = "fighting"

class ConceptType(Enum):
    CHARACTER = "character"
    ENVIRONMENT = "environment"
    STORY = "story"
    MECHANIC = "mechanic"
    QUEST = "quest"
    ITEM = "item"
    DIALOGUE = "dialogue"
    MUSIC = "music"
    LEVEL = "level"
    ENEMY = "enemy"

class ArtStyle(Enum):
    PIXEL_ART = "pixel_art"
    LOW_POLY = "low_poly"
    ANIME = "anime"
    REALISTIC = "realistic"
    STYLIZED = "stylized"
    HAND_DRAWN = "hand_drawn"
    MINIMALIST = "minimalist"
    VOXEL = "voxel"
    WATERCOLOR = "watercolor"
    COMIC = "comic"

# Expanded Data Models
@dataclass
class GameProject:
    name: str
    project_type: ProjectType
    art_style: ArtStyle
    target_audience: str
    core_mechanics: List[str]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    concepts: Dict[str, 'GameConcept'] = field(default_factory=dict)
    high_concept: str = ""
    unique_selling_points: List[str] = field(default_factory=list)
    inspiration_sources: List[str] = field(default_factory=list)
    target_platform: List[str] = field(default_factory=list)
    estimated_scope: str = ""
    mood_board: List[str] = field(default_factory=list)
    project_status: str = "Pre-production"
    team_size: str = ""
    budget_range: str = ""

@dataclass
class GameConcept:
    type: ConceptType
    name: str
    description: str
    references: List[str]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    generated_video: Optional[str] = None
    variations: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    concept_art: List[str] = field(default_factory=list)
    feedback_notes: List[str] = field(default_factory=list)
    iteration_history: List[Dict] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)

class GameProjectManager:
    def __init__(self):
        self.projects: Dict[str, GameProject] = {}
        
    def create_project(self, name: str, project_type: ProjectType, art_style: ArtStyle, 
                      target_audience: str, core_mechanics: List[str], **kwargs) -> GameProject:
        project = GameProject(
            name=name,
            project_type=project_type,
            art_style=art_style,
            target_audience=target_audience,
            core_mechanics=core_mechanics,
            **kwargs
        )
        self.projects[project.id] = project


        conn = sqlite3.connect('game_project.db')
        c = conn.cursor()

        # Guardar en SQLite
        c.execute('''
            INSERT INTO projects (id, name, project_type, art_style, target_audience,
            core_mechanics, high_concept, unique_selling_points, target_platform,
            team_size, budget_range, created_at, project_status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project.id, name, project_type.value, art_style.value, target_audience,
            "\n".join(core_mechanics), kwargs.get("high_concept", ""),
            "\n".join(kwargs.get("unique_selling_points", [])),
            "\n".join(kwargs.get("target_platform", [])), kwargs.get("team_size", ""),
            kwargs.get("budget_range", ""), project.created_at.isoformat(),
            kwargs.get("project_status", "Pre-production")))
        conn.commit()
        conn.close()

        return project
    
    def add_concept(self, project_id: str, concept: GameConcept):
        conn = sqlite3.connect('game_project.db')
        c = conn.cursor()

        # Guardar en SQLite
        c.execute('''
            INSERT INTO concepts (id, project_id, type, name, description, reference_links,
            generated_video, variations, metadata, concept_art, feedback_notes,
            iteration_history, related_concepts) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (concept.id, project_id, concept.type.value, concept.name, concept.description,
              "\n".join(concept.references), concept.generated_video,
              "\n".join(map(str, concept.variations)), str(concept.metadata),
              "\n".join(concept.concept_art), "\n".join(concept.feedback_notes),
              "\n".join(map(str, concept.iteration_history)), "\n".join(concept.related_concepts)))
        conn.commit()
        conn.close()