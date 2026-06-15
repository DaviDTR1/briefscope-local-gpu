from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import DB_PATH

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_conn, _record):
    """Enable WAL mode and foreign-key enforcement on every new connection."""
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL")       # concurrent reads while writing
    cur.execut