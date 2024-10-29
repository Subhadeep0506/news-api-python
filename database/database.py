from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.fastapi_config import FastAPIConfig

engine = create_engine(FastAPIConfig.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)
