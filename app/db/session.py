from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create the engine
engine = create_engine(settings.DATABASE_URL) #he thing that knows how to talk to the database.

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency Function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()