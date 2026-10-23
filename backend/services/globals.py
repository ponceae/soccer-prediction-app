from collections import defaultdict
from typing import Sequence
from sqlmodel import col, select, Session

import backend.api.models as models

def generate_menu_data(session: Session) -> defaultdict:
    """ 
    Build a nested dictionary of competitions and seasons.
    
    Args:
        session (Session): The current working database.
        
    Returns:
        defaultdict: Nested dictionary mapping countries to competitions, containing
            lists of the following season metadata:
                - Competition ID
                - Season ID
                - Season year
                - Competition knockout flag identifier.
    """
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
            col(models.Competition.code), 
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
            'has_knockout': comp.knockout,
        })
    
    return menu

def get_all_teams(session: Session):
    return session.exec(select(models.Team).order_by(col(models.Team.name))).all()

def get_team_competitions(team_id: int, session: Session):
    statement = session.exec(
        select(
            models.TeamCompetition
        )
        .where(models.TeamCompetition.team_id == team_id)
    ).all()
    
    return statement
