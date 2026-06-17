from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    league: str
    
class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: date
    
    home_team_id: int = Field(foreign_key='team.id')
    away_team_id: int = Field(foreign_key='team.id')
    
    home_goals: int
    away_goals: int
    