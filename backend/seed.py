import csv
from database import engine
from datetime import datetime
from sqlmodel import select, Session, SQLModel
from typing import TypeVar

import models as models
    
T = TypeVar('T', bound=SQLModel)
    
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

F_SEASONS = {
    '2526': '2025-26',
}

LEAGUE_COUNTRIES = {
    'epl': 'England',
}

# +=======================+
#   Loaders/CSV Parsers
# +=======================+


def load_csv_to_table(session: Session, csv_path: str, model: type[SQLModel]):
    """
    Open and read a csv file and load its contents into the specified database table.

    Args:
        session (Session): The current database workspace for the current transaction.
        csv_path (str): The path to the `.csv` file.
        model (type[SQLModel]): The SQLModel class mapping to the database table.
    """
    # with open(csv_path, mode='r', encoding='utf-8') as file:
    #     reader = csv.DictReader(file)
    #     for row in reader:
    #         for key, value in row.items():
    #             if value == 'True':
    #                 row[key]= True
    #             elif value == 'False':
    #                 row[key] = False
    #             elif key == 'date':
    #                 row[key] = datetime.strptime(value, '%Y-%m-%d').date()
    #             if model is models.Team or model is models.Competition:
    #                 pass
    #             elif model is models.Season:
    #                 pass
    #         session.add(model(**row))
    # session.commit()

def generate_tids(session: Session) -> dict[str, int]:
    """
    Retrieve all the teams from the current workspace and create a lookup dictionary.

    Args:
        session (Session): The current database workspace for the current transaction.

    Returns:
        dict[str, int]: A mapping of all the teams to their unique IDs.
            (e.g., `{'Arsenal': 1, 'Aston Villa': 2, ...}`).
    """
    teams = session.exec(select(models.Team)).all()
    
    tids = {}
    for team in teams:
        tids[team.name] = team.id
    
    return tids

def load_match_csv_to_table(
    session: Session, 
    csv_path: str, 
    comp_id: int, 
    _season_id: int
):
    """
    Read match data from a `.csv` file and load it into the `Match` database table.

    Args:
        session (Session): The current database workspace for the current transaction.
        csv_path (str): The path to to the `.csv` file.
        comp_id (int): The competition ID the matches belong to.
        _season_id (int): The season ID the matches belong to.
    """
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        tids = generate_tids(session)
        
        tally = {}
        
        for row in reader:            
            home_team = EPL_LU.get(row['HomeTeam'], row['HomeTeam'])
            away_team = EPL_LU.get(row['AwayTeam'], row['AwayTeam'])

            h_games_played = tally.get(home_team, 0)
            a_games_played = tally.get(away_team, 0)

            curr_matchweek = max(h_games_played, a_games_played) + 1

            tally[home_team] = h_games_played + 1
            tally[away_team] = a_games_played + 1
                            
            match = models.Match(
                date=datetime.strptime(row['Date'], '%Y-%m-%d').date(),
                matchweek=curr_matchweek,
                competition_id=comp_id,
                season_id=_season_id,
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

# +==================================+
#   Filename Parsers/Table Validators
# +==================================+

def parse_csv_filename(path: str) -> tuple[str, str]:
    """ 
    Parse and return the metadata contained in the CSV filename.
    Should be of the pattern 'data/{League Name}_{Season Years}_season_matches.csv'

    Args:
        path (str): The name of the csv file to parse.
    Returns:
        tuple[str, str]: A tuple containing filename metadata in the form:
            - League name
            - League season years
    """
    new_path = path.split('_')

    league = new_path[0].split('/')
    league.remove('data')

    return league[0], new_path[1]

def validate_unique_entry(model_class: type[T], session: Session, curr_entry: str):
    if model_class == models.Team or model_class == models.Competition:
        statement = select(model_class).where(
            getattr(model_class, 'name') == curr_entry
        )
    elif model_class == models.Season:
        statement = select(models.Season).where(
            models.Season.year == curr_entry
        )
    
    entry = session.exec(statement).first()
    
    if entry:
        return True
    return False
    
    # TODO: 
    # Figure out if the function should have the power to update the current
    # session, or if it should return a flag to the loader to either skip or write
    # the entry.

# +=======================+
#          Main
# +=======================+

def seed_database():
    print(parse_csv_filename('data/epl_2526_season_matches.csv'))
    # print('Creating database tables...')
    # SQLModel.metadata.create_all(engine)
    
    # with Session(engine) as session:
    #     print('Importing independent tables...')
    #     load_csv_to_table(session, 'data/teams.csv', models.Team)
    #     load_csv_to_table(session, 'data/competitions.csv', models.Competition)
    #     load_csv_to_table(session, 'data/seasons.csv', models.Season)
        
    #     print('Importing relational tables...')     
    #     load_csv_to_table(
    #         session, 
    #         'data/team_competitions.csv', 
    #         models.TeamCompetition
    #     )
    #     load_match_csv_to_table(session, 'data/epl_2526_season_matches.csv', 1, 1)
        
    #     print('Database successfully seeded from CSVs.')
        
if __name__ == '__main__':
    seed_database()
          