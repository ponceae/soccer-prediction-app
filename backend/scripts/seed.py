import csv
from backend.api.database import engine
from datetime import date, datetime, time
from sqlmodel import func, and_, select, Session, SQLModel
from pathlib import Path
from typing import TypeVar

from seed_constants import COMP_LU, F_SEASONS, PRIMARY_COMP, TEAM_LU
import backend.api.models as models
    
T = TypeVar('T', bound=SQLModel)

# +=====================+
#   Loaders/CSV Parsers
# +=====================+

def derive_and_load_teamcompetition(
    session: Session, 
    csv_path: str, 
    model: type[SQLModel],
    comp_id: int,
    season_id: int,
    is_primary: bool,
):
    """ 
    Use the match batch to derive TeamCompetition data. 
    
    Build each candidate a row (home and away team and their attributes), then check
    if the record exists, if not then create the TeamCompetition record.
    
    Args:
        session (Session): The current database workspace for the current transaction.
        csv_path (str): The path to to the `.csv` file.
        model (type[SQLModel]): The SQLModel class mapping to the database table.
        comp_id (int): The derived competition ID from the data file.
        season_id (int): The derived season ID from the data file.
        is_primary (bool): The primary league identifier derived from the data file.
    """
    with open(csv_path, mode='r', encoding='utf-8') as file:
        tids = generate_tids(session)
        reader = csv.DictReader(file)
        
        processed_team_ids = set()
        
        for row in reader:
            home_team = TEAM_LU.get(row['HomeTeam'], row['HomeTeam'])
            away_team = TEAM_LU.get(row['AwayTeam'], row['AwayTeam'])
            
            home_id = tids.get(home_team)
            away_id = tids.get(away_team)
            
            for tid in (home_id, away_id):
                if tid and tid not in processed_team_ids:                    
                    if not validate_unique_teamcompetition_entry(
                        models.TeamCompetition, session, tid, comp_id, season_id
                    ):
                        team_comp = model(
                            team_id=tid,
                            competition_id=comp_id,
                            season_id=season_id,
                            is_primary=is_primary
                        )
                        session.add(team_comp)
                    processed_team_ids.add(tid)
        session.commit()
            
def load_csv_to_table(session: Session, csv_path: str, model: type[SQLModel]):
    """
    Open, read, and load a `.csv` file's contents into the specified database table.

    Args:
        session (Session): The current database workspace for the current transaction.
        csv_path (str): The path to the `.csv` file.
        model (type[SQLModel]): The SQLModel class mapping to the database table.
    """
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key, value in row.items():
                if key == 'knockout':
                    row[key] = value.strip().lower() == 'true'
               
            duplicate = False     
            if model is models.Team or model is models.Competition:
                duplicate = validate_unique_entry(model, session, row['name'])
            elif model is models.Season:
                duplicate = validate_unique_entry(model, session, row['year'])
                    
            if not duplicate:
                session.add(model.model_validate(row))
                
    session.commit()

def load_match_csv_to_table(
    session: Session, csv_path: str, comp_id: int, season_id: int,
):
    """
    Read match data from a `.csv` file and load it into the `Match` database table.

    Args:
        session (Session): The current database workspace for the current transaction.
        csv_path (str): The path to to the `.csv` file.
        comp_id (int): The competition ID the matches belong to.
        season_id (int): The season ID the matches belong to.
    """
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        tids = generate_tids(session)
        
        tally = {}

        # select the highest matchweek saved for this season
        base_matchweek = session.exec(
            select(func.max(models.Match.matchweek))
            .where(
                models.Match.competition_id == comp_id,
                models.Match.season_id == season_id,
            )
        ).one_or_none() or 0
        
        for row in reader:            
            home_team = TEAM_LU.get(row['HomeTeam'], row['HomeTeam'])
            away_team = TEAM_LU.get(row['AwayTeam'], row['AwayTeam'])

            # matchweek is inferred from cumulative team appearances 
            # this loader only processes complete historical season CSVs in batches.
            # !!!!!!
            # DO NOT reuse this logic for incremental/live match ingestion.
            # !!!!!!
            
            h_games_played = tally.get(home_team, 0)
            a_games_played = tally.get(away_team, 0)

            curr_matchweek = base_matchweek + max(h_games_played, a_games_played) + 1

            tally[home_team] = h_games_played + 1
            tally[away_team] = a_games_played + 1
             
            # tally updates must occur before duplicate rows are skipped.
            duplicate = validate_unique_match_entry(
                models.Match, 
                session,
                comp_id,
                season_id,
                tids[home_team],
                tids[away_team],
                datetime.strptime(row['Date'], '%d/%m/%Y').date(),
                datetime.strptime(row['Time'], '%H:%M').time()
            )
            
            if not duplicate:
                match = models.Match(
                    date=datetime.strptime(row['Date'], '%d/%m/%Y').date(),
                    time=datetime.strptime(row['Time'], '%H:%M').time(),
                    matchweek=curr_matchweek,
                    competition_id=comp_id,
                    season_id=season_id,
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
                    aet_home_goals=int(row['AETHG']) if row.get('AETHG') else None,
                    aet_away_goals=int(row['AETAG']) if row.get('AETAG') else None,
                    ps_home_goals=int(row['PSHG']) if row.get('PSHG') else None,
                    ps_away_goals=int(row['PSAG']) if row.get('PSAG') else None,
                )
                session.add(match)
    session.commit()          

# +==================================+
#   Filename Parsers/Table Validators
# +==================================+

def derive_competition_and_season_id(
    session: Session, league: str, season: str
) -> tuple[int, int, bool]:
    """ 
    Retrieve the database IDs for the given competition and season and return them 
    alongside the primary league flag identifier.
    
    Args:
        session (Session): The current database workspace for the current transaction.
        league (str): The raw league name.
        season (str): The raw season year.
        
    Returns:
        tuple[int, int, bool]: A tuple containing the following queried DB data:
            - Competition ID
            - Season ID
            - The is_primary league flag
    """
    # looks up the official league names & correctly formatted season years.
    comp_name = COMP_LU.get(league, league)
    season_year = F_SEASONS.get(season, season)
    
    comp_obj = session.exec(
        select(models.Competition).where(models.Competition.name == comp_name)
    ).first()
    
    season_obj = session.exec(
        select(models.Season).where(models.Season.year == season_year)
    ).first()
    
    # loud fails, something wrong happened with independent table loading...
    
    if not comp_obj or not season_obj:
        raise ValueError(
            f"Competition '{comp_name}' or Season '{season_year}' not found in DB."
        )
    
    if comp_obj.id is None or season_obj.id is None:
        raise RuntimeError('Retrieved database records are missing primary keys.')
        
    is_primary = league in PRIMARY_COMP
    
    return comp_obj.id, season_obj.id, is_primary

def generate_tids(session: Session) -> dict[str, int]:
    """
    Retrieve all the teams from the current workspace and create a lookup dictionary.

    Args:
        session (Session): The current database workspace for the current transaction.

    Returns:
        dict[str, int]: A mapping of all the teams to their unique IDs.
    """
    teams = session.exec(select(models.Team)).all()
    
    tids = {}
    for team in teams:
        tids[team.name] = team.id
    
    return tids

def parse_csv_filename(fp_name: str) -> tuple[str, str]:
    """ 
    Parse and return the metadata contained in the CSV filename.
    Should be of the pattern 'data/{League Name}_{Season Years}_season_matches.csv'

    Args:
        fp_name (str): The name of the csv file path to parse.
        
    Returns:
        tuple[str, str]: A tuple containing filename metadata in the form:
            - League name
            - League season years
    """
    new_path = fp_name.split('_')

    league = new_path[0].split('/')
    league.remove('data')

    return league[0], new_path[1]

def validate_unique_entry(
    model_class: type[T], session: Session, curr_entry: str
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

def validate_unique_match_entry(
    model_class: type[models.Match],
    session: Session,
    competition_id: int,
    season_id: int,
    home_team_id: int,
    away_team_id: int,
    date: date,
    time: time,
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
            model_class.time == time,
        ),
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

# +=======================+
#          Main
# +=======================+

def seed_database():
    """ 
    Create the DB if not created already, and iterate through the data directory
    to batch pull, open, and load the data from the `.csv` onto the DB.
    """
    print('Creating database tables...')
    SQLModel.metadata.create_all(engine)
    
    data_dir = Path('data')
    
    with Session(engine) as session:
        print('Importing independent tables...')
        load_csv_to_table(session, str(data_dir / 'teams.csv'), models.Team)
        load_csv_to_table(
            session, str(data_dir / 'competitions.csv'), models.Competition
        )
        load_csv_to_table(session, str(data_dir / 'seasons.csv'), models.Season)
        
        for match_file in data_dir.glob('*_matches.csv'):
            fp = str(match_file)
            
            league, season_str = parse_csv_filename(fp)
            
            comp_id, season_id, is_primary = derive_competition_and_season_id(
                session, league, season_str
            )
            
            print('Importing relational tables...')     
            derive_and_load_teamcompetition(
                session,
                fp,
                models.TeamCompetition,
                comp_id, 
                season_id,
                is_primary,
            )
            load_match_csv_to_table(session, fp, comp_id, season_id)
        
        print('Database successfully seeded from CSVs.')
        
if __name__ == '__main__':
    seed_database()
          