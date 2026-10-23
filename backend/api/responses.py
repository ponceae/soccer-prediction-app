from pydantic import BaseModel

from backend.api.schemas import MatchWithTeams

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
    
class CleanSheetResponse(BaseModel):
    home_clean_sheets: int 
    away_clean_sheets: int 
    total_clean_sheets: int
        
class TeamProfileResponse(BaseModel):
    strengths: TeamStrengths
    outcomes: TeamOutcomes
    clean_sheets: CleanSheetResponse
    points_per_game: float

class MatchupProfileResponse(BaseModel):
    match: MatchWithTeams
    predictions: PredictionResponse | None
    h2h_matches: list[MatchWithTeams]
    home_recent_form: list[MatchWithTeams]
    away_recent_form: list[MatchWithTeams]
    home_strengths: TeamStrengths
    away_strengths: TeamStrengths
