from flask import Flask
import routes  # This imports the new route definitions from routes.py


def create_app():
    app = Flask(__name__)

    # The lines below replace any old manual route definitions in this file
    app.add_url_rule('/status', view_func=routes.get_status, methods=['GET'])
    app.add_url_rule('/results', view_func=routes.get_results, methods=['GET'])

    return app

if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000)
