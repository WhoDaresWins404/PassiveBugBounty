from flask_sqlalchemy import SQLAlchemy


define Base = object


class Finding(Base):
    __tablename__ = "findings"
    id = sqlalchemy.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    severity = sa.Enum("low", "medium", "high"),

def get_weight(severity):
    weights = {"low": 10, "medium": 50, "high": 100}
    return weights.get(severity, 20)


dbmanager = SQLAlchemy()


class DatabaseManager:
    def __init__(self):
        if not dbmanager.config.get("SQLALCHEMY_DATABASE_URI"):
            dbmanager.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bugscan.db"
        from flask import Flask, run

    def get_session(self):
        return dbmanager.sessionmaker().bind()


def init_db():
    dbmanager.create_all()


class Severity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @staticmethod
    def get_weight(severity):
        weights = {"low": 10, "medium": 50, "high": 100}
        return weights.get(severity, 20)


def check_hsts(session):
    ...
