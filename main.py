from contextlib import asynccontextmanager
from collections import defaultdict
from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlmodel import col, SQLModel, Session, select, or_

from analytics import Analytics, HomeAwayID
from crud import get_team_by_id
from database import engine, get_session
import models as db

@asynccontextmanager
async def setup_db(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title='Poisson Soccer Prediction Model', lifespan=setup_db)

# +============================+
#         General Routes
# +============================+

@app.get('/ping')
def home():
    return {'message': 'Soccer Predictor API'}

@app.get('/teams/{team_id}', response_model=db.TeamRead)
def get_team(team_id: int, session: Session = Depends(get_session)):
    return _get_team_or_404(session, team_id)

@app.get('/teams', response_model=list[db.TeamRead])
def get_teams(session: Session = Depends(get_session)):
    return session.exec(select(db.Team).order_by(col(db.Team.name))).all()
    
@app.get('/matches', response_model=list[db.MatchWithTeams])
def get_matches(session: Session = Depends(get_session)):
    return session.exec(select(db.Match).order_by(col(db.Match.date))).all()
    
@app.get('/competitions', response_model=list[db.CompetitionRead])
def get_competitions(session: Session = Depends(get_session)):
    return session.exec(select(db.Competition)).all()        

@app.get('/seasons', response_model=list[db.SeasonRead])
def get_seasons(session: Session = Depends(get_session)):
    return session.exec(select(db.Season)).all()

@app.get('/team_competitions', response_model=db.TeamCompetitionExtended)
def get_all_team_competitions(session: Session = Depends(get_session)):
    return session.exec(select(db.TeamCompetition)).all()
    
# +============================+
#     League Specific Routes
# +============================+

@app.get('/leagues/{competition_id}/{season_id}/goal_averages')
def get_league_goal_avg(competition_id: int, season_id: int):
    h_league_goal_avg, a_league_goal_avg = _create_analytic_data(
        competition_id, 
        season_id
    ).league_goal_averages()
    
    return {
        'home_league_goal_avg': h_league_goal_avg, 
        'away_league_goal_avg': a_league_goal_avg,
    }

@app.get('/leagues/{competition_id}/{season_id}/btts_rate')
def get_btts_rate(competition_id: int, season_id: int):
    btts_rate = _create_analytic_data(competition_id, season_id).btts_rate()
    
    return {
        'both_teams_to_score_rate': btts_rate,
    }

@app.get('/leagues/{competition_id}/{season_id}/over_rate')
def get_over_rate(competition_id: int, season_id: int):
    over_rate = _create_analytic_data(competition_id, season_id).over_rate()
    
    return {
        'over_2.5_goals': over_rate,
    }

@app.get('/menu_data')
def get_menu_data(session: Session = Depends(get_session)):
    competitions = session.exec(select(db.Competition)).all()
    
    menu = defaultdict(list)
    
    for comp in competitions:
        curr_season_id = session.exec(
            select(db.TeamCompetition.season_id)
            .join(db.Season)
            .where(col(db.TeamCompetition.competition_id) == comp.id)
            .order_by(col(db.Season.year).desc())
        ).first()
    
        season_id = curr_season_id if curr_season_id else 0
        
        menu[comp.country].append({
            'id': comp.id,
            'name': comp.name,
            'season_id': season_id
        })
    
    return menu

@app.get('/leagues/{competition_id}/{season_id}/league_table')
def get_full_league_table(competition_id: int, season_id: int, session: Session = Depends(get_session)):
    league_teams = session.exec(
        select(db.Team)
        .join(db.TeamCompetition)
        .where(db.TeamCompetition.competition_id == competition_id)
    ).all()
    
    table = []
    
    analytics = _create_analytic_data(competition_id, season_id)
    
    for team in league_teams:
        assert team.id is not None
        wins, losses, draws, total_matches, gf, ga, gd, points = analytics.league_table_stats(team.id)
        table.append({
            'team_name': team.name,
            'matches_played': total_matches,
            'points': points,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'gf': gf,
            'ga': ga,
            'gd': gd,
        })

    return table

# +============================+
#     Matchup Specific Routes
# +============================+

@app.get('/{competition_id}/{season_id}/matchup/expected_goals')
def get_team_xgs(competition_id: int, season_id: int, home_id: int, away_id: int):
    h_xg, a_xg = _create_analytic_data(
        competition_id, 
        season_id
    ).expected_goals(_create_home_and_away_data(home_id, away_id))
    
    return {
        'home_expected_goals': h_xg,
        'away_expected_goals': a_xg,
    }

@app.get('/{competition_id}/{season_id}/matchup/prediction')
def get_prediction(competition_id: int, season_id: int, home_id: int, away_id: int):
    home_win, away_win, draw = _create_analytic_data(
        competition_id, 
        season_id,
    ).poisson_prediction(_create_home_and_away_data(home_id, away_id))
    
    return {
        'home_win_probability': round((home_win * 100), 3),
        'away_win_probability': round((away_win * 100), 3),
        'draw_probability': round((draw * 100), 3),
    }

@app.get('/{competition_id}/{season_id}/matchup/scoreline_likelihood')
def get_scoreline_likelihood(
    competition_id: int, 
    season_id: int, 
    home_id: int, 
    away_id: int,
):
    scoreline = _create_analytic_data(
        competition_id, 
        season_id,
    ).scoreline_chance(_create_home_and_away_data(home_id, away_id))
    
    return {
        'most_likely_scoreline': scoreline,
    }

# +============================+
#     Team Specific Routes
# +============================+

@app.get('/teams/{team_id}/{competition_id}/{season_id}/strengths')
def get_team_strengths(competition_id: int, season_id: int, team_id: int):
    h_atk, h_def, a_atk, a_def = _create_analytic_data(
        competition_id, 
        season_id
    ).team_strengths(team_id)

    return {
        'home_attack': h_atk, 
        'home_defense': h_def, 
        'away_attack': a_atk, 
        'away_defense': a_def,
    }

@app.get('/teams/{team_id}/goals')
def get_team_goals(team_id: int):
    with Session(engine) as session:        
        filter = select(db.Match).where(
            or_(db.Match.home_team_id == team_id, db.Match.away_team_id == team_id)
        )
        all_matches = session.exec(filter).all()
        
        goals = 0
        for match in all_matches:
            if match.home_team_id == team_id:
                goals += match.home_goals
            else:
                goals += match.away_goals
        
        return {
            'team': _get_team_or_404(session, team_id).name, 
            'total_goals_scored': goals,
        }

@app.get(
    '/teams/{team_id}/competitions', 
    response_model=list[db.TeamCompetitionExtended]
)
def get_team_competitions(team_id: int, session: Session = Depends(get_session)):
    return session.exec(
        select(db.TeamCompetition).where(db.TeamCompetition.team_id == team_id)
    ).all()

@app.get('/teams/{team_id}/{competition_id}/{season_id}/outcome_rates')
def get_outcome_rates(competition_id: int, season_id: int, team_id: int):
    wins, draws, losses = _create_analytic_data(
        competition_id, 
        season_id
    ).outcome_percentages(team_id)
    
    return {
        'win_rate': wins,
        'loss_rate': losses,
        'draw_rate': draws,
    }

@app.get('/teams/{team_id}/{competition_id}/{season_id}/ppg')
def get_team_ppg(competition_id: int, season_id: int, team_id: int):
    ppg = _create_analytic_data(competition_id, season_id).ppg(team_id)
    
    return {
        'points_per_game': ppg
    }

@app.get('/teams/{team_id}/{competition_id}/{season_id}/league_table_data')
def get_team_league_table_stats(competition_id: int, season_id: int, team_id: int):
    wins, losses, draws, total_matches, gf, ga, gd, points, = _create_analytic_data(
        competition_id, 
        season_id
    ).league_table_stats(team_id)
    
    return {
        'wins': wins,
        'losses': losses,
        'draws': draws,
        'matches_played': total_matches,
        'goals_for': gf,
        'goals_against': ga,
        'goal_difference': gd,
        'points': points,
    }

app.mount('/', StaticFiles(directory='static', html=True), name='static')

# +============================+
#       Helper Functions
# +============================+
    
def _create_analytic_data(competition_id: int, season_id: int) -> Analytics:
    with Session(engine) as session:
        return Analytics(session, competition_id, season_id)

def _create_home_and_away_data(home_team_id: int, away_team_id: int) -> HomeAwayID:
    return HomeAwayID(home_team_id, away_team_id)

def _get_team_or_404(session: Session, team_id: int) -> db.Team:
    team = get_team_by_id(session, team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail='Team not found')
    
    return team
