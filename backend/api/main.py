from contextlib import asynccontextmanager
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel

from backend.api.database import engine, get_session
import backend.api.models as models, backend.api.schemas as schemas
import backend.api.responses as responses

from services import globals
from services.base import HomeAwayID
from services.league import LeagueService
from services.matchup import MatchupService
from services.prediction import PredictionEngine
from services.team import TeamService

# +==============+
#   Route Setup
# +==============+

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

def get_league_service(
    competition_id: int, 
    season_id: int, 
    session: Session = Depends(get_session)
):
    return LeagueService(session, competition_id, season_id)

def get_team_service(
    competition_id: int,
    season_id: int,
    session: Session = Depends(get_session)
):
    return TeamService(session, competition_id, season_id)

def get_prediction_engine(
    competition_id: int,
    season_id: int,
    session: Session = Depends(get_session)
):
    return PredictionEngine(session, competition_id, season_id)

def get_matchup_service(
    competition_id: int,
    season_id: int,
    session: Session = Depends(get_session),
):
    return MatchupService(session, competition_id, season_id)

def get_team_matchups(home_id: int, away_id: int) -> HomeAwayID:
    return HomeAwayID(home_team_id=home_id, away_team_id=away_id)

# +============================+
#         General Routes
# +============================+

@app.get('/ping')
def home():
    return {'message': 'Soccer Predictor API'}

@app.get('/menu_data')
def get_menu_data(session: Session = Depends(get_session)):
    return globals.generate_menu_data(session)

@app.get('/teams/{team_id}', response_model=schemas.TeamRead)
def get_team(team_id: int, session: Session = Depends(get_session)):
    return _get_team_or_404(session, team_id)

@app.get('/teams', response_model=list[schemas.TeamRead])
def get_teams(session: Session = Depends(get_session)):
    return globals.get_all_teams(session)

@app.get(
    '/teams/{team_id}/competitions', 
    response_model=list[schemas.TeamCompetitionExtended],
)
def get_team_competitions_route(team_id: int, session: Session = Depends(get_session)):
    _get_team_or_404(session, team_id)
    
    return globals.get_team_competitions(team_id, session)
    
# +============================+
#     League Specific Routes
# +============================+

@league_router.get('/summary', response_model=responses.LeagueSummaryResponse)
def get_league_summary(leagues: LeagueService = Depends(get_league_service)):
    return leagues.league_summary()

@league_router.get('/league_table')
def get_full_league_table(leagues: LeagueService = Depends(get_league_service)):
    return leagues.generate_league_table()

@league_router.get('/matchups', response_model=list[schemas.MatchWithTeams])
def get_league_matchups(leagues: LeagueService = Depends(get_league_service)):
    return leagues.get_regular_season_matchups()

@league_router.get('/knockouts', response_model=list[schemas.MatchWithTeams])
def get_league_knockouts(leagues: LeagueService = Depends(get_league_service)):
    return leagues.get_knockout_matches()

# +============================+
#     Matchup Specific Routes
# +============================+

@prediction_router.get('/prediction', response_model=responses.PredictionResponse)
def get_matchup_prediction(
    predictions: PredictionEngine = Depends(get_prediction_engine), 
    teams: HomeAwayID = Depends(get_team_matchups),
):
    return predictions.generate_matchup_prediction(teams)

@prediction_router.get('/{match_id}/profile', response_model=responses.MatchupProfileResponse)
def get_matchup_profile(
    match_id: int,
    matchup: MatchupService = Depends(get_matchup_service)
):
    profile = matchup.generate_matchup_profile(match_id)
    if not profile:
        raise HTTPException(status_code=404, detail='Match not found')
    return profile

# +============================+
#     Team Specific Routes
# +============================+

@team_stats_router.get('/profile', response_model=responses.TeamProfileResponse)
def get_team_profile(
    team_id: int, 
    session: Session = Depends(get_session), 
    team: TeamService = Depends(get_team_service)
):
    _get_team_or_404(session, team_id)
    return team.generate_team_profile(team_id)

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
