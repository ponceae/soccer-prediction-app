from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    
class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    date: date
    
    competition_id: int = Field(foreign_key='competition.id')
    season_id: int = Field(foreign_key='season.id')
    
    home_team_id: int = Field(foreign_key='team.id')
    away_team_id: int = Field(foreign_key='team.id')
    
    home_goals: int
    away_goals: int
    
class TeamCompetition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    team_id: int = Field(foreign_key='team.id')
    competition_id: int = Field(foreign_key='competition.id')
    season_id: int = Field(foreign_key='season.id')
    
    is_primary: bool = False
    
class Competition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    type: str = Field(index=True) # Ex. `domestic`, `cup` etc.
    
class Season(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    year: str # Ex. `2024-25`
    