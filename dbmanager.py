from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SaEnum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    def get_weight(self):
        weights = {Severity.LOW: 1, Severity.MEDIUM: 5, Severity.HIGH: 10}
        return weights.get(self)


class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True)
    name = Column(String))


class Finding(Base):
    __tablename__ = "findings"
    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer)
    severity = Column(SaEnum(Severity))
    title = Column(String))
    description = Column(String))


class DatabaseManager:

def get_session(self):
    return session

engine = create_engine("sqlite:///scans.db")

def init_db():
    Base.metadata.create_all(bind=engine)
