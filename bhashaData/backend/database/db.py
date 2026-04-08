from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from backend.config.settings import settings

engine_kwargs = {"future": True}

# Configure pooling based on database type
if settings.database_url.startswith("postgresql"):
    # Use NullPool for serverless/Railway deployments
    engine_kwargs.update({
        "poolclass": NullPool,
    })
elif settings.database_url.startswith("sqlite"):
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
    })

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
