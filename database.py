from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
password = quote_plus("Rawan1122334")
DATABASE_URL = (
    f"mysql+pymysql://root:{password}"
    "@localhost:3306/payroll_system"
    "?charset=utf8mb4"
)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()