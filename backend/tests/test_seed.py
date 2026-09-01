import pytest 
from sqlmodel import create_engine, Session, SQLModel

import seed 
import models

""" 
Pattern:

def test_something():
    engine = create_engine('sqlite://')
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Add known data
        # Call validator with THIS session
        # Assert result
"""

def test_validate_unique_entry_is_true():
    engine = create_engine('sqlite://')
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        session.add(models.Team(name='Arsenal', id=1))
        result = seed.validate_unique_entry(models.Team, session, 'Arsenal')
    assert result is True

def test_validate_unique_entry_is_false():
    engine = create_engine('sqlite://')
    SQLModel.metadata.create_all(engine)
        
    with Session(engine) as session:
        session.add(models.Team(name='Arsenal', id=1))
        result = seed.validate_unique_entry(models.Team, session, 'Manchester United')    
    assert result is False
    
def test_validate_unique_entry_does_not_load_duplicate_data(tmp_path):
    engine = create_engine('sqlite://')
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        session.add(models.Team(name='Arsenal', id=1))
        session.commit()

        csv_file = tmp_path / 'test_data.csv'
        csv_file.write_text(
            'id,name\n'
            '1,Arsenal\n'
        )
        
        seed.load_csv_to_table(session, csv_file, models.Team)
        
    

def test_validate_unique_entry_loads_unique_data():
    pass
