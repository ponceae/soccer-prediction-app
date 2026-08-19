from datetime import date
from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from typing import Optional

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
    
    competition_id: int
    season_id: int
    home_team_id: int 
    away_team_id: int
    
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
    
# +=====================+
#   Response Validators
# +=====================+

class ExpectedGoals(BaseModel):
    home_expected_goals: float
    away_expected_goals: float
    
class WinProbability(BaseModel):
    home_win_probability: float
    away_win_probability: float
    draw_probability: float

class PredictionResponse(BaseModel):
    xg: ExpectedGoals
    win_probability: WinProbability
    likely_scoreline: tuple[int, int]
    
class GoalAveragesResponse(BaseModel):
    home_league_goal_avg: float
    away_league_goal_avg: float
    
class LeagueSummaryResponse(BaseModel):
    goal_averages: GoalAveragesResponse
    btts_rate: float
    over_rate: float
    
class TeamStrengths(BaseModel):
    home_attack: float 
    home_defense: float 
    away_attack: float
    away_defense: float
        
class TeamOutcomes(BaseModel):
    win_rate: float
    loss_rate: float
    draw_rate: float
        
class TeamProfileResponse(BaseModel):
    strengths: TeamStrengths
    outcomes: TeamOutcomes
    points_per_game: float
