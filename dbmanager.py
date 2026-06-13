import enum
from sqlalchemy import Column, Integer, String, Enum as SaEnum, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Severity(enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    def get_weight(self):
        weights = {Severity.LOW: 1, Severity.MEDIUM: 5, Severity.HIGH: 10}
        return weights.get(self)


class Scan(dbmanager.Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True)
    name = Column(String))


class Finding(dbmanager.Base):
    __tablename__ = "findings"
    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer)
    severity = Column(Enum[Severity]))
    title = Column(String))
    description = Column(String))


class DatabaseManager:

def get_session(self):
    return session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
