from datetime import date
from sqlmodel import Session
from models import Competition, Match, Season, Team, TeamCompetition

from main import engine

def seed_database():
    with Session(engine) as session:
        epl = Competition(name='Premier League', type='Domestic')
        fa_cup = Competition(name='FA Cup', type='Domestic Cup')
        carabao_cup = Competition(name='Carabao Cup', type='League Cup')
        season_24_25 = Season(year='2024-25')
        
        session.add_all([epl, fa_cup, carabao_cup, season_24_25])
        session.flush()
        
        man_u = Team(name='Manchester United')
        chelsea = Team(name='Chelsea')
        liverpool = Team(name='Liverpool')
        newcastle_u = Team(name='Newcastle United')
        
        session.add_all([man_u, chelsea, liverpool, newcastle_u])
        session.flush()
        
        assert man_u.id is not None
        assert chelsea.id is not None
        assert liverpool.id is not None
        assert newcastle_u.id is not None
        
        assert epl.id is not None
        assert fa_cup.id is not None
        assert carabao_cup.id is not None
        assert season_24_25.id is not None
        
        man_u_epl_comp = TeamCompetition(
            team_id=man_u.id, 
            competition_id=epl.id, 
            season_id=season_24_25.id, 
            is_primary=True,
        )
        
        man_u_fa_cup_comp = TeamCompetition(
            team_id=man_u.id, 
            competition_id=fa_cup.id, 
            season_id=season_24_25.id, 
            is_primary=False,
        )
        
        man_u_carabao_cup_comp = TeamCompetition(
            team_id=man_u.id,
            competition_id=carabao_cup.id,
            season_id=season_24_25.id,
            is_primary=False,
        )
        
        chelsea_epl_comp = TeamCompetition(
            team_id=chelsea.id,
            competition_id=epl.id,
            season_id=season_24_25.id,
            is_primary=True,
        )  
        
        chelsea_carabao_cup_comp = TeamCompetition(
            team_id=chelsea.id,
            competition_id=carabao_cup.id,
            season_id=season_24_25.id,
            is_primary=False,
        )  
        
        liverpool_epl_comp = TeamCompetition(
            team_id=liverpool.id,
            competition_id=epl.id,
            season_id=season_24_25.id,
            is_primary=True,
        )     
        
        liverpool_fa_cup_comp = TeamCompetition(
            team_id=liverpool.id,
            competition_id=fa_cup.id,
            season_id=season_24_25.id,
            is_primary=False,
        ) 
        
        newcastle_u_epl_comp = TeamCompetition(
            team_id=newcastle_u.id,
            competition_id=epl.id,
            season_id=season_24_25.id,
            is_primary=True,
        )   
        
        newcastle_u_carabao_comp = TeamCompetition(
            team_id=newcastle_u.id,
            competition_id=carabao_cup.id,
            season_id=season_24_25.id,
            is_primary=False,
        )        
        
        session.add_all([
            man_u_epl_comp, 
            man_u_fa_cup_comp, 
            man_u_carabao_cup_comp, 
            chelsea_epl_comp, 
            chelsea_carabao_cup_comp,
            liverpool_epl_comp, 
            liverpool_fa_cup_comp, 
            newcastle_u_epl_comp,
            newcastle_u_carabao_comp
        ])
        session.flush()
        
        session.refresh(man_u)
        session.refresh(chelsea)
        session.refresh(liverpool)
        session.refresh(newcastle_u)
        session.refresh(season_24_25)
        session.refresh(epl)
        session.refresh(fa_cup)
        session.refresh(carabao_cup)
        
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
        
        match_3 = Match(
            date=date(2025, 11, 16),
            competition_id=epl.id,
            season_id=season_24_25.id,
            home_team_id=liverpool.id,
            away_team_id=newcastle_u.id,
            home_goals=1,
            away_goals=3,
        )
        
        match_4 = Match(
            date=date(2026, 1, 18),
            competition_id=epl.id,
            season_id=season_24_25.id,
            home_team_id=chelsea.id,
            away_team_id=liverpool.id,
            home_goals=2,
            away_goals=2,
        )
        
        match_5 = Match(
            date=date(2026, 4, 19),
            competition_id=epl.id,
            season_id=season_24_25.id,
            home_team_id=newcastle_u.id,
            away_team_id=man_u.id,
            home_goals=3,
            away_goals=3,
        )
        
        match_6 = Match(
            date=date(2025, 10, 23),
            competition_id=fa_cup.id,
            season_id=season_24_25.id,
            home_team_id=liverpool.id,
            away_team_id=man_u.id,
            home_goals=1,
            away_goals=2,
        )
        
        match_7 = Match(
            date=date(2025, 9, 5),
            competition_id=carabao_cup.id,
            season_id=season_24_25.id,
            home_team_id=newcastle_u.id,
            away_team_id=chelsea.id,
            home_goals=1,
            away_goals=0,
        )
        
        match_8 = Match(
            date=date(2026, 4, 19),
            competition_id=epl.id,
            season_id=season_24_25.id,
            home_team_id=newcastle_u.id,
            away_team_id=man_u.id,
            home_goals=3,
            away_goals=3,
        )
        
        session.add_all([
            match_1, match_2, match_3, match_4, match_5, match_6, match_8
        ])
        session.commit()
        
        print('Database has been successfully seeded.')
        
if __name__ == '__main__':
    seed_database()
          