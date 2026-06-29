import csv
from datetime import datetime
from sqlmodel import Session, SQLModel

from database import engine
import models as db
    
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

def seed_database():
    print('Creating database tables...')
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        print('Importing independent tables...')
        load_csv_to_table(session, 'data/teams.csv', db.Team)
        load_csv_to_table(session, 'data/competitions.csv', db.Competition)
        load_csv_to_table(session, 'data/seasons.csv', db.Season)
        
        print('Importing relational tables...')     
        load_csv_to_table(session, 'data/team_competitions.csv', db.TeamCompetition)
        load_csv_to_table(session, 'data/matches.csv', db.Match)
        
        print('Database successfully seeded from CSVs.')
        
if __name__ == '__main__':
    seed_database()
          