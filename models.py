from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

class MatchBase(SQLModel):
    date: date
    
    competition_id: int = Field(foreign_key='competition.id')
    season_id: int = Field(foreign_key='season.id')
    
    home_team_id: int = Field(foreign_key='team.id')
    away_team_id: int = Field(foreign_key='team.id')
    
    home_goals: int
    away_goals: int

class Match(MatchBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    home_team: Optional[Team] = Relationship(
        sa_relationship_kwargs={'foreign_keys': 'Match.home_team_id'}
    )
    away_team: Optional[Team] = Relationship(
        sa_relationship_kwargs={'foreign_keys': 'Match.away_team_id'}
    )

class MatchWithTeams(MatchBase):
    id: int
    
    home_team: Optional[Team] = None
    away_team: Optional[Team] = None
 
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
    