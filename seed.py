from datetime import date
from sqlmodel import Session
from models import Competition, Match, Season, Team, TeamCompetition

from main import engine

def seed_database():
    with Session(engine) as session:
        epl = Competition(name='Premier League', type='Domestic')
        season_24_25 = Season(year='2024-25')
        
        session.add_all([epl, season_24_25])
        session.flush()
        
        man_u = Team(name='Manchester United')
        chelsea = Team(name='Chelsea')
        
        session.add_all([man_u, chelsea])
        session.flush()
        
        assert man_u.id is not None
        assert chelsea.id is not None
        assert epl.id is not None
        assert season_24_25.id is not None
        
        man_u_comp = TeamCompetition(
            team_id=man_u.id, 
            competition_id=epl.id, 
            season_id=season_24_25.id, 
            is_primary=True,
        )
        
        chelsea_comp = TeamCompetition(
            team_id=chelsea.id,
            competition_id=epl.id,
            season_id=season_24_25.id,
            is_primary=True,
        )        
        
        session.add_all([man_u_comp, chelsea_comp])
        session.flush()
        
        session.refresh(man_u)
        session.refresh(chelsea)
        session.refresh(season_24_25)
        session.refresh(epl)
        
        match_1 = Match(
            date=date(2026, 2, 7),
            competition_id=epl.id,
            season_id=season_24_25.id,
            home_team_id=man_u.id,
            away_team_id=chelsea.id,
            home_goals=3,
            away_goals=2,
        )
        
        match_2 = Match(
            date=date(2025, 9, 13),
            competition_id=epl.id,
            season_id=season_24_25.id,
            home_team_id=chelsea.id,
            away_team_id=man_u.id,
            home_goals=0,
            away_goals=1,
        )
        
        session.add_all([match_1, match_2])
        session.commit()
        
        print('Database has been successfully seeded.')
        
if __name__ == '__main__':
    seed_database()
          