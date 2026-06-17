from datetime import date
from sqlmodel import Session
from models import Match, Team

from main import engine

def seed_database():
    with Session(engine) as session:
        man_u = Team(name='Manchester United', league='Premier League')
        chelsea = Team(name='Chelsea', league='Premier League')
        
        session.add(man_u)
        session.add(chelsea)
        session.commit()
        
        session.refresh(man_u)
        session.refresh(chelsea)
        
        assert man_u.id is not None
        assert chelsea.id is not None
        
        match_1 = Match(
            date=date(2026, 2, 7),
            home_team_id=man_u.id,
            away_team_id=chelsea.id,
            home_goals=3,
            away_goals=2,
        )
        
        match_2 = Match(
            date=date(2025, 9, 13),
            home_team_id=chelsea.id,
            away_team_id=man_u.id,
            home_goals=0,
            away_goals=1,
        )
        
        session.add(match_1)
        session.add(match_2)
        session.commit()
        
        print('Database has been successfully seeded.')
        
if __name__ == '__main__':
    seed_database()
          