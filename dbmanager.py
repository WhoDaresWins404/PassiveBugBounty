from flask_sqlalchemy import SQLAlchemy


dbmanager = SQLAlchemy()


class Finding(dbmanager.Model):
    __tablename__ = "findings"
    id = dbmanager.Column(dbmanager.Integer, primary_key=True)
    title = dbmanager.Column(dbmanager.String)
    severity = dbmanager.Column(dbmanager.Enum("low", "medium", "high"), nullable=False)


class Severity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @staticmethod
    def get_weight(severity):
        weights = {"low": 10, "medium": 50, "high": 100}
        return weights.get(severity, 20)


class MockSession:
    """Fake session object for mocked imports."""
    commit = lambda self: None
    rollback = lambda self: None


class DatabaseManager:
    def __init__(self):
        pass

    def get_session(self):
        return MockSession()


def init_db():
    dbmanager.create_all()
