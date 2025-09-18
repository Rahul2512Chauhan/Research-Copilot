from sqlalchemy import create_engine , Column , Integer , String , DateTime ,Text , Boolean
from sqlalchemy.orm import declarative_base , sessionmaker
from datetime import datetime, timezone

#Path to SQLite database file
DATABASE_URL = "sqlite:///db/rag.db"

# Base class for models
Base = declarative_base()

#Source table 
class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer , primary_key=True , index=True)
    source_id = Column(String, unique=True , index=True , nullable=False)
    filename = Column(String , nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

#Pages table
class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer , primary_key=True , index=True)
    source_id = Column(String ,index=True , nullable=False)
    page_number = Column(Integer , nullable=True)
    text = Column(Text , nullable=True)
    word_count = Column(Integer , default=0)
    ocr = Column(Boolean , default=False)
    parse_errors = Column(Integer , default=0)
    created_at = Column(DateTime , default = lambda: datetime.now(timezone.utc))


#Create engine + session
engine = create_engine(DATABASE_URL , connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False , autoflush=False , bind=engine)

#Create tables if they don't exist 
def init_db():
    Base.metadata.create_all(bind=engine)

