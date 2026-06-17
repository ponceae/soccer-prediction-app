""" 
"""

__author__ = 'Adrien P.'

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, create_engine, Session, select, or_

from crud import get_team_by_id
from models import Match, Team

sqlite_file_name = 'soccer.db'
sqlite_url = f'sqlite:///{sqlite_file_name}'
engine = create_engine(sqlite_url, echo=False)

@asynccontextmanager
async def setup_db(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title='Poisson Soccer Prediction Model', lifespan=setup_db)

@app.get('/')
def home():
    return {'message': 'Soccer Predictor API'}

# ============
# LIST QUERIES 
# ============

@app.get('/teams')
def get_teams():
    with Session(engine) as session:
        statement = select(Team)
        teams = session.exec(statement).all()
        
        return teams
    
@app.get('/matches')
def get_matches():
    with Session(engine) as session:
        query = select(Match)
        matches = session.exec(query).all()
        
        return matches

# ==============
# DETAIL QUERIES
# ==============

@app.get('/teams/{team_id}')
def get_team(team_id: int):
    with Session(engine) as session:
        return get_team_or_404(team_id, session)

@app.get('/teams/{team_id}/goals')
def get_scores(team_id: int):
    with Session(engine) as session:
        team = get_team_or_404(team_id, session)
        
        query = select(Match).where(
            or_(Match.home_team_id == team_id, Match.away_team_id == team_id)
        )
        all_matches = session.exec(query).all()
        
        goals = 0
        for match in all_matches:
            if match.home_team_id == team_id:
                goals += match.home_goals
            else:
                goals += match.away_goals
        
        return {'team': team.name, 'total_goals_scored': goals}

def get_team_or_404(team_id: int, session: Session):
    team = get_team_by_id(session, team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail='Team not found')
    
    return team
