from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, create_engine, Session, select, or_

from analytics import (
    get_league_goal_averages, 
    get_team_strengths, 
    poisson_prediction
)
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

@app.get('/teams')
def get_teams():
    with Session(engine) as session:
        statement = select(Team)
        teams = session.exec(statement).all()
        
        return teams
    
@app.get('/matches')
def get_matches():
    with Session(engine) as session:
        statement = select(Match)
        matches = session.exec(statement).all()
        
        return matches

@app.get('/teams/{team_id}/league/average_goals')
def get_league_average_goals(team_id):
    with Session(engine) as session:
        team = _get_team_or_404(session, team_id)
        # league = team.league
        h_lga, a_lga = get_league_goal_averages(session)
        return {'home_league_goal_avg': h_lga, 'away_league_goal_avg': a_lga}

@app.get('/teams/{team_id}')
def get_team(team_id: int):
    with Session(engine) as session:
        return _get_team_or_404(session, team_id)

@app.get('/teams/{team_id}/goals')
def get_scores(team_id: int):
    with Session(engine) as session:
        team = _get_team_or_404(session, team_id)
        
        statement = select(Match).where(
            or_(Match.home_team_id == team_id, Match.away_team_id == team_id)
        )
        all_matches = session.exec(statement).all()
        
        goals = 0
        for match in all_matches:
            if match.home_team_id == team_id:
                goals += match.home_goals
            else:
                goals += match.away_goals
        
        return {'team': team.name, 'total_goals_scored': goals}


def _get_team_or_404(session: Session, team_id: int) -> Team:
    team = get_team_by_id(session, team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail='Team not found')
    
    return team

# # debug
# @app.get('/test/strengths/{team_id}')
# def test_strengths(team_id: int):
#     with Session(engine) as session:
#         avg_home_goals, avg_away_goals = get_league_goal_averages(session)
        
#         h_atk, h_def, a_atk, a_def = get_team_strengths(session, team_id)
        
#         return {
#             'team_id': team_id,
#             'baseline': {
#                 'avg_league_home_goals': avg_home_goals,
#                 'avg_league_away_goals': avg_away_goals,
#             },
#             'strengths': {
#                 'home_attack': h_atk,
#                 'home_defense': h_def,
#                 'away_attack': a_atk,
#                 'away_defense': a_def,
#             }
#         }

# # debug
# def main():
#     with Session(engine) as session:
#         win, loss, draw = poisson_prediction(session, 1, 2)
#         print(f'{win:%}')
#         print(f'{draw:%}')
#         print(f'{loss:%}')

        
# if __name__ == '__main__':
#     main()
