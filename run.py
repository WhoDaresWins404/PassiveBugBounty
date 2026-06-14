from src.db import init_db
from src.ui import app


def main():
    init_db()
    app.run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
