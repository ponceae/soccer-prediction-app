from contextlib import asynccontextmanager
from collections import defaultdict
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import selectinload
from sqlmodel import col, select, Session, SQLModel

from analytics import Analytics, HomeAwayID
from database import engine, get_session
import models as models, schemas as schemas

@asynccontextmanager
async def setup_db(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title='Poisson Soccer Prediction Model', lifespan=setup_db)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# +==============+
#   Quick Routes
# +==============+

league_router = APIRouter(
    prefix='/leagues/{competition_id}/{season_id}',
    tags=['Leagues'],
)

prediction_router = APIRouter(
    prefix = '/{competition_id}/{season_id}/matchup',
    tags=['Predictions'],
)

team_stats_router = APIRouter(
    prefix = '/teams/{team_id}/{competition_id}/{season_id}',
    tags=['Team Statistics'],
)

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

@league_router.get('/summary', response_model=schemas.LeagueSummaryResponse)
def get_league_summary(analytics: Analytics = Depends(get_analytics)):
    h_league_goal_avg, a_league_goal_avg = analytics.league_goal_averages()
    
    return {
        'goal_averages': {
            'home_league_goal_avg': h_league_goal_avg, 
            'away_league_goal_avg': a_league_goal_avg,
        },
        'btts_rate': analytics.btts_rate(),
        'over_rate': analytics.over_rate(),
    }

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

@league_router.get('/league_table')
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

@prediction_router.get('/prediction', response_model=schemas.PredictionResponse)
def get_matchup_prediction(
    analytics: Analytics = Depends(get_analytics), 
    teams: HomeAwayID = Depends(get_team_matchups),
):
    h_xg, a_xg = analytics.expected_goals(teams)
    home_win, draw, away_win = analytics.poisson_prediction(teams)
    
    return {
        'xg': {
            'home_expected_goals': h_xg,
            'away_expected_goals': a_xg,
        },
        'win_probability': {
            'home_win_probability': round((home_win * 100), 3),
            'away_win_probability': round((away_win * 100), 3),
            'draw_probability': round((draw * 100), 3),
        },
        'likely_scoreline': analytics.scoreline_chance(teams),
    }
    
@league_router.get('/matchups', response_model=list[schemas.MatchWithTeams])
def get_league_matchups(
    competition_id: int,
    season_id: int,
    session: Session = Depends(get_session)
):
    statement = (
        select(models.Match)
        .where(
            models.Match.competition_id == competition_id,
            models.Match.season_id == season_id,
        )
        .options(
            selectinload(models.Match.home_team), # type: ignore
            selectinload(models.Match.away_team), # type: ignore
        )
        .order_by(col(models.Match.date).desc())
    )
    
    return session.exec(statement).all()

# +============================+
#     Team Specific Routes
# +============================+

@app.get(
    '/teams/{team_id}/competitions', 
    response_model=list[schemas.TeamCompetitionExtended],
)
def get_team_competitions(team_id: int, session: Session = Depends(get_session)):
    _get_team_or_404(session, team_id)
    
    return session.exec(
        select(models.TeamCompetition).where(models.TeamCompetition.team_id == team_id)
    ).all()

@team_stats_router.get('/profile', response_model=schemas.TeamProfileResponse)
def get_team_profile(
    team_id: int, 
    session: Session = Depends(get_session), 
    analytics: Analytics = Depends(get_analytics)
):
    _get_team_or_404(session, team_id)
    
    h_atk, h_def, a_atk, a_def = analytics.team_strengths(team_id)
    wins, draws, losses = analytics.outcome_percentages(team_id)
    (
        h_clean_sheets, 
        a_clean_sheets, 
        total_clean_sheets,
    ) = analytics.team_clean_sheets(team_id)
    
    return {
        'strengths': {
            'home_attack': h_atk, 
            'home_defense': h_def, 
            'away_attack': a_atk, 
            'away_defense': a_def,
        },
        'outcomes': {
            'win_rate': wins,
            'loss_rate': losses,
            'draw_rate': draws,
        },
        'clean_sheets': {
            'home_clean_sheets': h_clean_sheets,
            'away_clean_sheets': a_clean_sheets,
            'total_clean_sheets': total_clean_sheets,
        },
        'points_per_game': analytics.ppg(team_id)
    }

app.include_router(league_router)
app.include_router(prediction_router)
app.include_router(team_stats_router)

# +============================+
#       Helper Functions
# +============================+

def _get_team_or_404(session: Session, team_id: int) -> models.Team:
    team = session.get(models.Team, team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail='Team not found')
    
    return team
