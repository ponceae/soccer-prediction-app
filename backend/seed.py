import csv
from database import engine
from datetime import date, datetime
from sqlmodel import and_, select, Session, SQLModel
from typing import TypeVar

import models
    
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

# +=====================+
#   Loaders/CSV Parsers
# +=====================+

def derive_and_load_teamcompetition(
    session: Session, 
    csv_path: str, 
    model: type[SQLModel]
):
    pass


def load_csv_to_table(session: Session, csv_path: str, model: type[SQLModel]):
    """
    Open and read a csv file and load its contents into the specified database table.

    Args:
        session (Session): The current database workspace for the current transaction.
        csv_path (str): The path to the `.csv` file.
        model (type[SQLModel]): The SQLModel class mapping to the database table.
    """
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
                elif key == 'team_id':
                    team_id = int(row[key])
                elif key == 'competition_id':
                    comp_id = int(row[key])
                elif key == 'season_id':
                    season_id = int(row[key])
                if model is models.Team or model is models.Competition:
                    duplicate = validate_unique_entry(model, session, row['name'])
                elif model is models.Season:
                    duplicate = validate_unique_entry(model, session, row['year'])
                # MAY OR MAY NOT CHANGE BELOW!!
                elif model is models.TeamCompetition:
                    duplicate = validate_unique_teamcompetition_entry(
                        model, 
                        session, 
                        team_id,
                        comp_id,
                        season_id,
                    )
            if not duplicate:
                session.add(model.model_validate(row))
    session.commit()

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
    _season_id: int,
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

            # Matchweek is inferred from cumulative team appearances because this 
            # loader only processes complete historical season CSVs in batch order.
            # 
            # DO NOT reuse this logic for incremental/live match ingestion.
            
            h_games_played = tally.get(home_team, 0)
            a_games_played = tally.get(away_team, 0)

            curr_matchweek = max(h_games_played, a_games_played) + 1

            tally[home_team] = h_games_played + 1
            tally[away_team] = a_games_played + 1
             
            # Tally updates must occur before duplicate rows are skipped.
            duplicate = validate_unique_match_entry(
                models.Match, 
                session,
                comp_id,
                _season_id,
                tids[home_team],
                tids[away_team],
                datetime.strptime(row['Date'], '%Y-%m-%d').date(),
            )
            
            if not duplicate:
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

def validate_unique_entry(
    model_class: type[T], 
    session: Session, 
    curr_entry: str
) -> bool:
    """
    Read a table row and determine if its entry already exists in the database.

    Args:
        model_class (type[T]): The SQLModel class mapping to the database table.
        session (Session): The current database workspace for the current transaction.
        curr_entry (str): The table row to read.

    Returns:
        bool: `True` if the entry already exists, `False` otherwise.
    """
    if model_class == models.Team or model_class == models.Competition:
        statement = select(model_class).where(
            getattr(model_class, 'name') == curr_entry
        )
    elif model_class == models.Season:
        statement = select(models.Season).where(
            models.Season.year == curr_entry
        )
    
    entry = session.exec(statement).first()
    
    return entry is not None

def validate_unique_teamcompetition_entry(
    model_class: type[models.TeamCompetition], 
    session: Session, 
    team_id: int,
    competition_id: int,
    season_id: int,
) -> bool:
    """
    Read a table row and determine if its entry already exists in the database.

    Args:
        model_class (type[models.TeamCompetition]): The SQLModel class mapping to the 
            database table.
        session (Session): The current database workspace for the current transaction.
        team_id (int): The entry's team ID.
        competition_id (int): The entry's competition ID.
        season_id: (int): The entry's season ID.

    Returns:
        bool: `True` if the entry already exists, `False` otherwise.
    """
    statement = select(model_class).where(
        and_(
            model_class.team_id == team_id,
            model_class.competition_id == competition_id,
            model_class.season_id == season_id,
        ),
    )
    
    entry = session.exec(statement).first()
    
    return entry is not None 

def validate_unique_match_entry(
    model_class: type[models.Match],
    session: Session,
    competition_id: int,
    season_id: int,
    home_team_id: int,
    away_team_id: int,
    date: date,
) -> bool:
    """
    Read a table row and determine if its entry already exists in the database.

    Args:
        model_class (type[models.Match]): The SQLModel class mapping to the database 
            table.
        session (Session): The current database workspace for the current transaction.
        team_id (int): The entry's team ID.
        competition_id (int): The entry's competition ID.
        season_id: (int): The entry's season ID.
        home_team_id (int): The entry's home team ID.
        away_team_id (int): The entry's away team ID.
        date (datetime): The entry's date.

    Returns:
        bool: `True` if the entry already exists, `False` otherwise.
    """
    statement = select(model_class).where(
        and_(
            model_class.competition_id == competition_id,
            model_class.season_id == season_id,
            model_class.home_team_id == home_team_id,
            model_class.away_team_id == away_team_id,
            model_class.date == date,
        ),
    )
    
    entry = session.exec(statement).first()
    
    return entry is not None

# +=======================+
#          Main
# +=======================+

def seed_database():
    print('Creating database tables...')
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        print('Importing independent tables...')
        load_csv_to_table(session, 'data/teams.csv', models.Team)
        load_csv_to_table(session, 'data/competitions.csv', models.Competition)
        load_csv_to_table(session, 'data/seasons.csv', models.Season)
        
        # TODO: I need to implement TeamCompetition so that its ids are derived 
        # from Team, Competition, and Season. `is_primary` needs to be derived 
        # somehow from the Competition.
        
        # print('Importing relational tables...')     
        # load_csv_to_table(
        #     session, 
        #     'data/team_competitions.csv', 
        #     models.TeamCompetition
        # )
        load_match_csv_to_table(session, 'data/epl_2526_season_matches.csv', 1, 1)
        
        print('Database successfully seeded from CSVs.')
        
if __name__ == '__main__':
    seed_database()
          