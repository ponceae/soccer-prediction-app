"""
"""

__author__ = 'Adrien P.'

from sqlmodel import Session, select
from models import Match

""" 
Return the average home & away goals across the whole league.
"""
def get_league_averages(session: Session):
    matches = session.exec(select(Match)).all()
    total_matches = len(matches)
    
    if total_matches == 0:
        return 0.0, 0.0
    
    total_home_goals = sum(m.home_goals for m in matches)
    total_away_goals = sum(m.away_goals for m in matches)
    
    home_goal_avg = total_home_goals / total_matches
    away_goal_avg = total_away_goals / total_matches
    
    return home_goal_avg, away_goal_avg
