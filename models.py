from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class TeamBase(SQLModel):
    name: str = Field(index=True, unique=True)
    
class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
class TeamRead(TeamBase):
    id: int

class SeasonBase(SQLModel):
    year: str
    
class Season(SeasonBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
class SeasonRead(SeasonBase):
    id: int

class CompetitionBase(SQLModel):
    name: str = Field(index=True, unique=True)
    type: str = Field(index=True)
    
class Competition(CompetitionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
class CompetitionRead(CompetitionBase):
    id: int

class MatchBase(SQLModel):
    date: date
    matchweek: int
    
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
 
class TeamCompetitionBase(SQLModel):
    team_id: int = Field(foreign_key='team.id')
    competition_id: int = Field(foreign_key='competition.id')
    season_id: int = Field(foreign_key='season.id')
    is_primary: bool = True
    
class TeamCompetition(TeamCompetitionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
 
    team: Optional[Team] = Relationship()
    competition: Optional[Competition] = Relationship()
    season: Optional[Season] = Relationship()
    
class TeamCompetitionExtended(TeamCompetitionBase):
    id: int
    
    team: Optional[TeamRead]
    competition: Optional[CompetitionRead]
    season: Optional[SeasonRead]
    