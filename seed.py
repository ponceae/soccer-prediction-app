import csv
from datetime import datetime
from sqlmodel import Session, SQLModel, select

from database import engine
import models as models
    
EPL_LU = {
    'Tottenham': 'Tottenham Hotspur',
    'Spurs': 'Tottenham Hotspur',
    'Brighton': 'Brighton and Hove Albion',
    'Nott\'m Forest': 'Nottingham Forest',
    'Man United': 'Manchester United',
    'Man City': 'Manchester City',
    'Leeds': 'Leeds United',
    'West Ham': 'West Ham United',
    'Newcastle': 'Newcastle United',
    'Wolves': 'Wolverhampton Wanderers',
    'Bournemouth': 'AFC Bournemouth'
}
    
def load_csv_to_table(session: Session, csv_path: str, model):
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key, value in row.items():
                if value == 'True':
                    row[key]= True
                elif value == 'False':
                    row[key] = False
                elif key == 'date':
                    row[key] = datetime.strptime(value, '%Y-%m-%d').date()
            session.add(model(**row))
    session.commit()

def generate_tids(session: Session) -> dict[str, int]:
    teams = session.exec(select(models.Team)).all()
    
    tids = {}
    for team in teams:
        tids[team.name] = team.id
    
    return tids

def load_match_csv_to_table(session: Session, csv_path: str, model, cid: int, sid: int):
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        _matchweek = 1
        tids = generate_tids(session)
        
        tally = {}
        
        for row in reader:            
            home_team = EPL_LU.get(row['HomeTeam'], row['HomeTeam'])
            away_team = EPL_LU.get(row['AwayTeam'], row['AwayTeam'])

            tally['HomeTeam'] = tally.get(home_team, 0) + 1
            tally['AwayTeam'] = tally.get(away_team, 0) + 1
                            
            match = models.Match(
                date=datetime.strptime(row['Date'], '%Y-%m-%d').date(),
                matchweek=_matchweek,
                competition_id=cid,
                season_id=sid,
                home_team_id=tids[home_team],
                away_team_id=tids[away_team],
                ft_home_goals=int(row['FTHG']),
                ft_away_goals=int(row['FTAG']),
                ft_result=row['FTR'],
                ht_home_goals=int(row['HTHG']),
                ht_away_goals=int(row['HTAG']),
                ht_result=row['HTR'],
                referee=row['Referee'],
                home_shots=int(row['HS']),
                away_shots=int(row['AS']),
                home_sot=int(row['HST']),
                away_sot=int(row['AST']),
                home_fouls=int(row['HF']),
                away_fouls=int(row['AF']),
                home_corners=int(row['HC']),
                away_corners=int(row['AC']),
                home_yellow_cards=int(row['HY']),
                away_yellow_cards=int(row['AY']),
                home_red_cards=int(row['HR']),
                away_red_cards=int(row['AR']),
            )
            session.add(match)
    session.commit()          

def seed_database():
    print('Creating database tables...')
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        print('Importing independent tables...')
        load_csv_to_table(session, 'data/teams.csv', models.Team)
        load_csv_to_table(session, 'data/competitions.csv', models.Competition)
        load_csv_to_table(session, 'data/seasons.csv', models.Season)
        
        print('Importing relational tables...')     
        load_csv_to_table(session, 'data/team_competitions.csv', models.TeamCompetition)
        load_match_csv_to_table(session, 'data/epl_2526_season_matches.csv', models.Match, 1, 1)
        
        print('Database successfully seeded from CSVs.')
        
if __name__ == '__main__':
    seed_database()
          