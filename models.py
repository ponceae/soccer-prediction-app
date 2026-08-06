from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from schemas import (
    TeamBase,
    SeasonBase,
    CompetitionBase,
    MatchBase,
    TeamCompetitionBase,
)

class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    
class Season(SeasonBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
class Competition(CompetitionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    type: str = Field(index=True)
    country: str = Field(index=True)

class Match(MatchBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    competition_id: int = Field(foreign_key='competition.id', index=True)
    season_id: int = Field(foreign_key='season.id', index=True)
    home_team_id: int = Field(foreign_key='team.id', index=True)
    away_team_id: int = Field(foreign_key='team.id', index=True)
    
    home_team: Optional[Team] = Relationship(
        sa_relationship_kwargs={'foreign_keys': 'Match.home_team_id'}
    )
    away_team: Optional[Team] = Relationship(
        sa_relationship_kwargs={'foreign_keys': 'Match.away_team_id'}
    )
    
class TeamCompetition(TeamCompetitionBase, table=True):
    __table_args__ = (
        UniqueConstraint(
            'team_id', 
            'competition_id', 
            'season_id', 
            name='unique_team_comp_season',
        ),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
 
    team_id: int = Field(foreign_key='team.id')
    competition_id: int = Field(foreign_key='competition.id')
    season_id: int = Field(foreign_key='season.id')
 
    team: Optional[Team] = Relationship()
    competition: Optional[Competition] = Relationship()
    season: Optional[Season] = Relationship()
