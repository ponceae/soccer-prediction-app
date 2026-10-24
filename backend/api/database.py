from pathlib import Path

from sqlmodel import create_engine, Session

BASE_DIR = Path(__file__).resolve().parents[1]
sqlite_file_path = BASE_DIR / 'soccer.db'
sqlite_url = f'sqlite:///{sqlite_file_path.as_posix()}'

engine = create_engine(
    sqlite_url, 
    echo=False, 
    connect_args={'check_same_thread': False}
)

def get_session():
    with Session(engine) as session:
        yield session
