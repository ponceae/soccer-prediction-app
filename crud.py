""" 

"""

__author__ = 'Adrien P.'

from models import Team
from sqlmodel import Session

def get_team_by_id(session: Session, team_id: int):
    return session.get(Team, team_id)
