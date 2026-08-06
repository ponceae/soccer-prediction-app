from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel

# +==============+
#   Read Schemas
# +==============+

class TeamRead(SQLModel):
    id: int
    name: str
    
class SeasonRead(SQLModel):
    id: int
    year: str
    
class CompetitionRead(SQLModel):
    id: int
    name: str
    type: str
    country: str
    
# +================+
#    Base Schemas
# +================+

class TeamBase(SQLModel):
    name: str
    
class SeasonBase(SQLModel):
    year: str
    
class CompetitionBase(SQLModel):
    name: str
    type: str
    country: str

class MatchBase(SQLModel):
    date: date
    matchweek: int
    
    competition_id: int = Field(foreign_key='competition_id', index=True)
    season_id: int = Field(foreign_key='season_id', index=True)
    home_team_id: int = Field(foreign_key='team_id', index=True)
    away_team_id: int = Field(foreign_key='team_id', index=True)
    
    # full time / half time goals & results
    ft_home_goals: int
    ft_away_goals: int
    ft_result: str
    ht_home_goals: int
    ht_away_goals: int
    ht_result: str
    
    # other match stats
    referee: str
    home_shots: int
    away_shots: int
    home_sot: int
    away_sot: int
    home_fouls: int
    away_fouls: int
    home_corners: int
    away_corners: int
    home_yellow_cards: int
    away_yellow_cards: int
    home_red_cards: int
    away_red_cards: int
    
class TeamCompetitionBase(SQLModel):
    team_id: int
    competition_id: int
    season_id: int
    is_primary: bool = True
    
# +==================+
#   Extended Schemas
# +==================+

class MatchWithTeams(MatchBase):
    id: int
    home_team: Optional[TeamRead] = None
    away_team: Optional[TeamRead] = None

class TeamCompetitionExtended(TeamCompetitionBase):
    id: int
    team: Optional[TeamRead] = None
    competition: Optional[CompetitionRead] = None
    season: Optional[SeasonRead] = None
