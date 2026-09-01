import pytest 
from sqlmodel import create_engine, select, Session, SQLModel

import seed 
import models

@pytest.fixture
def test_session():
    engine = create_engine('sqlite://')
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_validate_unique_entry_is_true(test_session):
    test_session.add(models.Team(name='Arsenal'))

    result = seed.validate_unique_entry(models.Team, test_session, 'Arsenal')
    assert result is True

def test_validate_unique_entry_is_false(test_session):
    test_session.add(models.Team(name='Arsenal'))
    result = seed.validate_unique_entry(models.Team, test_session, 'Manchester United')    
    assert result is False
    
def test_validate_unique_entry_does_not_load_duplicate_table_data(
    test_session, 
    tmp_path
):
    test_session.add(models.Team(name='Arsenal', id=1))
    test_session.commit()

    csv_file = tmp_path / 'test_data.csv'
    csv_file.write_text(
        'name\n'
        'Arsenal\n'
    )
    
    seed.load_csv_to_table(test_session, csv_file, models.Team)

    all_entries = test_session.exec(select(models.Team)).all()
    assert len(all_entries) == 1

    tids = [entry.name for entry in all_entries]
    assert tids.count('Arsenal') == 1

def test_validate_unique_entry_loads_unique_data(test_session, tmp_path):
    test_session.add(models.Team(name='Arsenal', id=1))
    test_session.commit()

    csv_file = tmp_path / 'test_data.csv'
    csv_file.write_text(
        'name\n'
        'Manchester United\n'
    )

    seed.load_csv_to_table(test_session, csv_file, models.Team)

    all_entries = test_session.exec(select(models.Team)).all()
    assert len(all_entries) == 2

    tids = [entry.name for entry in all_entries]
    assert tids.count('Arsenal') == 1
    assert tids.count('Manchester United') == 1