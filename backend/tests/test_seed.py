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

# +======================+
#   Team Validator Tests
# +======================+

def test_validate_unique_team_entry_is_true(test_session):
    test_session.add(models.Team(name='Arsenal'))

    result = seed.validate_unique_entry(models.Team, test_session, 'Arsenal')
    assert result is True

def test_validate_unique_team_entry_is_false(test_session):
    test_session.add(models.Team(name='Arsenal'))
    result = seed.validate_unique_entry(models.Team, test_session, 'Manchester United')    
    assert result is False
    
def test_validate_team_entry_does_not_load_duplicate_table_data(
    test_session, 
    tmp_path
):
    test_session.add(models.Team(name='Arsenal'))
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

def test_validate_unique_team_entry_loads_to_table(test_session, tmp_path):
    test_session.add(models.Team(name='Arsenal'))
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
    
# +============================+
#   Competition Validator Tests
# +============================+

def test_validate_unique_comp_entry_is_true(test_session):
    test_session.add(
        models.Competition(
            name='Premier League', 
            type='Domestic League', 
            country='England',
        )
    )

    result = seed.validate_unique_entry(
        models.Competition, 
        test_session, 
        'Premier League',
    )
    assert result is True
    
def test_validate_unique_comp_entry_is_false(test_session):
    test_session.add(
        models.Competition(
            name='Premier League', 
            type='Domestic League', 
            country='England',
        )
    )

    result = seed.validate_unique_entry(
        models.Competition, 
        test_session, 
        'FA Cup'
    )
    assert result is False

def test_validate_comp_entry_does_not_load_duplicate_table_data(
    test_session, 
    tmp_path,
):
    test_session.add(
        models.Competition(
            name='Premier League', 
            type='Domestic League', 
            country='England',
        )
    )
    test_session.commit()

    csv_file = tmp_path / 'test_data.csv'
    csv_file.write_text(
        'name,type,country\n'
        'Premier League,Domestic League,England\n'
    )
    
    seed.load_csv_to_table(test_session, csv_file, models.Competition)

    all_entries = test_session.exec(select(models.Competition)).all()
    assert len(all_entries) == 1

    tids = [entry.name for entry in all_entries]
    assert tids.count('Premier League') == 1

def test_validate_unique_comp_entry_loads_to_table(
    test_session, 
    tmp_path,
):
    test_session.add(
        models.Competition(
            name='Premier League', 
            type='Domestic League', 
            country='England'
        )
    )
    test_session.commit()

    csv_file = tmp_path / 'test_data.csv'
    csv_file.write_text(
        'name,type,country\n'
        'FA Cup,Domestic Cup,England\n'
    )
    
    seed.load_csv_to_table(test_session, csv_file, models.Competition)

    all_entries = test_session.exec(select(models.Competition)).all()
    assert len(all_entries) == 2

    tids = [entry.name for entry in all_entries]
    assert tids.count('Premier League') == 1
    assert tids.count('FA Cup') == 1

# +========================+
#   Season Validator Tests
# +========================+

def test_validate_unique_season_entry_is_true(test_session):
    test_session.add(
        models.Season(
            year='2025-26'
        )
    )

    result = seed.validate_unique_entry(
        models.Season, 
        test_session, 
        '2025-26',
    )
    assert result is True
    
def test_validate_unique_season_entry_is_false(test_session):
    test_session.add(
        models.Season(
            year='2025-26'
        )
    )

    result = seed.validate_unique_entry(
        models.Competition, 
        test_session, 
        '2024-25'
    )
    assert result is False

def test_validate_season_entry_does_not_load_duplicate_table_data(
    test_session, 
    tmp_path,
):
    test_session.add(
        models.Season(
            year='2025-26'
        )
    )
    test_session.commit()

    csv_file = tmp_path / 'test_data.csv'
    csv_file.write_text(
        'year\n'
        '2025-26\n'
    )
    
    seed.load_csv_to_table(test_session, csv_file, models.Season)

    all_entries = test_session.exec(select(models.Season)).all()
    assert len(all_entries) == 1

    tids = [entry.year for entry in all_entries]
    assert tids.count('2025-26') == 1

def test_validate_unique_season_entry_loads_to_table(
    test_session, 
    tmp_path,
):
    test_session.add(
        models.Season(
            year='2025-26'
        )
    )
    test_session.commit()

    csv_file = tmp_path / 'test_data.csv'
    csv_file.write_text(
        'year\n'
        '2024-25\n'
    )
    
    seed.load_csv_to_table(test_session, csv_file, models.Season)

    all_entries = test_session.exec(select(models.Season)).all()
    assert len(all_entries) == 2

    tids = [entry.year for entry in all_entries]
    assert tids.count('2025-26') == 1
    assert tids.count('2024-25') == 1

# +================================+
#   TeamCompetition Validator Tests
# +================================+

# def test_validate_unique_teamcompetition_entry_is_true(test_session):
#     test_session.add(
#         models.TeamCompetition(
#             year='2025-26'
#         )
#     )

#     result = seed.validate_unique_entry(
#         models.Season, 
#         test_session, 
#         '2025-26',
#     )
#     assert result is True
    
# def test_validate_unique_season_entry_is_false(test_session):
#     test_session.add(
#         models.Season(
#             year='2025-26'
#         )
#     )

#     result = seed.validate_unique_entry(
#         models.Competition, 
#         test_session, 
#         '2024-25'
#     )
#     assert result is False

# def test_validate_season_entry_does_not_load_duplicate_table_data(
#     test_session, 
#     tmp_path,
# ):
#     test_session.add(
#         models.Season(
#             year='2025-26'
#         )
#     )
#     test_session.commit()

#     csv_file = tmp_path / 'test_data.csv'
#     csv_file.write_text(
#         'year\n'
#         '2025-26\n'
#     )
    
#     seed.load_csv_to_table(test_session, csv_file, models.Season)

#     all_entries = test_session.exec(select(models.Season)).all()
#     assert len(all_entries) == 1

#     tids = [entry.year for entry in all_entries]
#     assert tids.count('2025-26') == 1

# def test_validate_unique_season_entry_loads_to_table(
#     test_session, 
#     tmp_path,
# ):
#     test_session.add(
#         models.Season(
#             year='2025-26'
#         )
#     )
#     test_session.commit()

#     csv_file = tmp_path / 'test_data.csv'
#     csv_file.write_text(
#         'year\n'
#         '2024-25\n'
#     )
    
#     seed.load_csv_to_table(test_session, csv_file, models.Season)

#     all_entries = test_session.exec(select(models.Season)).all()
#     assert len(all_entries) == 2

#     tids = [entry.year for entry in all_entries]
#     assert tids.count('2025-26') == 1
#     assert tids.count('2024-25') == 1
