from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import settings

engine = create_engine(
    str(settings.database_url),
    future=True,
    echo=settings.debug,
    pool_pre_ping=True
)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
