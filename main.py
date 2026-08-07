from contextlib import asynccontextmanager
from collections import defaultdict
from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlmodel import col, func, SQLModel, Session, select, or_

from analytics import Analytics, HomeAwayID
from crud import get_team_by_id
from database import engine, get_session
import models
import schemas

@asynccontextmanager
async def setup_db(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title='Poisson Soccer Prediction Model', lifespan=setup_db)

# +============================+
#         Dependencies
# +============================+

def get_analytics(
    competition_id: int, 
    season_id: int,
    session: Session = Depends(get_session)
) -> Analytics:
    return Analytics(session, competition_id, season_id)

def get_team_matchups(home_id: int, away_id: int) -> HomeAwayID:
    return HomeAwayID(home_team_id=home_id, away_team_id=away_id)

# +============================+
#         General Routes
# +============================+

@app.get('/ping')
def home():
    return {'message': 'Soccer Predictor API'}

@app.get('/teams/{team_id}', response_model=schemas.TeamRead)
def get_team(team_id: int, session: Session = Depends(get_session)):
    return _get_team_or_404(session, team_id)

@app.get('/teams', response_model=list[schemas.TeamRead])
def get_teams(session: Session = Depends(get_session)):
    return session.exec(select(models.Team).order_by(col(models.Team.name))).all()      
    
# +============================+
#     League Specific Routes
# +============================+

@app.get('/leagues/{competition_id}/{season_id}/goal_averages')
def get_league_goal_avg(analytics: Analytics = Depends(get_analytics)):
    h_league_goal_avg, a_league_goal_avg = analytics.league_goal_averages()
    
    return {
        'home_league_goal_avg': h_league_goal_avg, 
        'away_league_goal_avg': a_league_goal_avg,
    }

@app.get('/leagues/{competition_id}/{season_id}/btts_rate')
def get_btts_rate(analytics: Analytics = Depends(get_analytics)):
    return {'both_teams_to_score_rate': analytics.btts_rate()}

@app.get('/leagues/{competition_id}/{season_id}/over_rate')
def get_over_rate(analytics: Analytics = Depends(get_analytics)):    
    return {'over_2.5_goals': analytics.over_rate()}

@app.get('/menu_data')
def get_menu_data(session: Session = Depends(get_session)):
    statement = (
        select(
            models.Competition, 
            models.Season,
        )
        .join(
            models.TeamCompetition, 
            col(models.Competition.id) == col(models.TeamCompetition.competition_id),
        )
        .join(
            models.Season, 
            col(models.TeamCompetition.season_id) == col(models.Season.id),
        )
        .group_by(col(models.Competition.id), col(models.Season.id))
        .order_by(
            col(models.Competition.country), 
            col(models.Competition.name), 
            col(models.Season.year).desc(),
        )
    )
    
    results = session.exec(statement).all()
    
    menu = defaultdict(lambda: defaultdict(list))
    
    for comp, season in results:
        menu[comp.country][comp.name].append({
            'competition_id': comp.id,
            'season_id': season.id,
            'season_year': season.year,
        })
    
    return menu 

@app.get('/leagues/{competition_id}/{season_id}/league_table')
def get_full_league_table(
    analytics: Analytics = Depends(get_analytics), 
    session: Session = Depends(get_session),
):
    league_teams = session.exec(
        select(models.Team)
        .join(models.TeamCompetition)
        .where(
            models.TeamCompetition.competition_id == analytics.competition_id,
            models.TeamCompetition.season_id == analytics.season_id,
        )
    ).all()
    
    table = []
        
    for team in league_teams:
        assert team.id is not None
        (
            wins, 
            losses, 
            draws, 
            total_matches, 
            gf, 
            ga, 
            gd, 
            points,
        ) = analytics.league_table_stats(team.id)
        
        table.append({
            'team_id': team.id,
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

    return sorted(table, key=lambda x: (x['points'], x['gd'], x['gf']), reverse=True)

# +============================+
#     Matchup Specific Routes
# +============================+

@app.get('/{competition_id}/{season_id}/matchup/expected_goals')
def get_team_xgs(
    analytics: Analytics = Depends(get_analytics),
    teams: HomeAwayID = Depends(get_team_matchups),
):
    h_xg, a_xg = analytics.expected_goals(teams)
    
    return {
        'home_expected_goals': h_xg,
        'away_expected_goals': a_xg,
    }

@app.get('/{competition_id}/{season_id}/matchup/prediction')
def get_prediction(
    analytics: Analytics = Depends(get_analytics),
    teams: HomeAwayID = Depends(get_team_matchups),
):
    home_win, away_win, draw = analytics.poisson_prediction(teams)
    
    return {
        'home_win_probability': round((home_win * 100), 3),
        'away_win_probability': round((away_win * 100), 3),
        'draw_probability': round((draw * 100), 3),
    }

@app.get('/{competition_id}/{season_id}/matchup/scoreline_likelihood')
def get_scoreline_likelihood(
    analytics: Analytics = Depends(get_analytics), 
    teams: HomeAwayID = Depends(get_team_matchups),
):
    return {'most_likely_scoreline': analytics.scoreline_chance(teams)}

# +============================+
#     Team Specific Routes
# +============================+

# @app.get('teams/{team_id}/{competition_id}/{season_id}/team_profile')
# def get_team_profile(session: Session = Depends(get_session)):
    
    
@app.get('/teams/{team_id}/{competition_id}/{season_id}/strengths')
def get_team_strengths(team_id: int, analytics: Analytics = Depends(get_analytics)):
    h_atk, h_def, a_atk, a_def = analytics.team_strengths(team_id)

    return {
        'home_attack': h_atk, 
        'home_defense': h_def, 
        'away_attack': a_atk, 
        'away_defense': a_def,
    }

@app.get(
    '/teams/{team_id}/competitions', 
    response_model=list[schemas.TeamCompetitionExtended]
)
def get_team_competitions(team_id: int, session: Session = Depends(get_session)):
    return session.exec(
        select(models.TeamCompetition).where(models.TeamCompetition.team_id == team_id)
    ).all()

@app.get('/teams/{team_id}/{competition_id}/{season_id}/outcome_rates')
def get_outcome_rates(team_id: int, analytics: Analytics = Depends(get_analytics)):
    wins, draws, losses = analytics.outcome_percentages(team_id)
    
    return {
        'win_rate': wins,
        'loss_rate': losses,
        'draw_rate': draws,
    }

@app.get('/teams/{team_id}/{competition_id}/{season_id}/ppg')
def get_team_ppg(team_id: int, analytics: Analytics = Depends(get_analytics)):
    return {'points_per_game': analytics.ppg(team_id)}

app.mount('/', StaticFiles(directory='static', html=True), name='static')

# +============================+
#       Helper Functions
# +============================+

def _get_team_or_404(session: Session, team_id: int) -> models.Team:
    team = get_team_by_id(session, team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail='Team not found')
    
    return team
