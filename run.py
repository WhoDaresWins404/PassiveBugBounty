from flask import Flask, render_template # Assuming a simple index.html template
from src.storage import init_db, get_all_endpoints

app = Flask(__name__)

@app.route('/')
def dashboard():
    data = get_all_endpoints()
    return f"<h1>Traffic Analyzer Dashboard</h1><p>Total endpoints captured: {len(data)}</p>"

if __name__ == "__main__":
    init_db()  # Ensure tables exist on startup
    app.run(host='0.0.0.0', port=5000)
