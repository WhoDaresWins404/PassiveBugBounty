from flask_sqlalchemy import SQLAlchemy


dbmanager = SQLAlchemy()


class Finding(dbmanager.Model):
    __tablename__ = "findings"
    id = dbmanager.Column(sa.Integer, primary_key=True)
    title = dbmanager.Column(sa.String)
    severity = dbmanager.Column(sa.Enum("low", "medium", "high"), nullable=False)


class Severity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @staticmethod
    def get_weight(severity):
        weights = {"low": 10, "medium": 50, "high": 100}
        return weights.get(severity, 20)


class DatabaseManager:
    def __init__(self):
        if not dbmanager.config.get("SQLALCHEMY_DATABASE_URI"):
            dbmanager.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bugscan.db"

    def get_session(self):
        return dbmanager.sessionmaker().bind()


def init_db():
    dbmanager.create_all()
