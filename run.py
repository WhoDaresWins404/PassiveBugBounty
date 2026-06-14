import subprocess
from flask import Flask
from src.mitm_plugin import endpoint_analyzer  # Import from our new module


app = Flask(__name__)

@app.route('/')
def index():
    return "Traffic Analyzer Web UI"


def start_mitmproxy():
    """Starts mitmproxy in the background on all interfaces."""
    cmd = [
        'mitmproxy',
        '-s', 'src.mitm_plugin',  # Point to our module instead of a script file
        '--set', 'mitmproxy_bind_address=0.0.0.0'
    ]
    subprocess.Popen(cmd, stdout=None, stderr=None)


if __name__ == "__main__":
    start_mitmproxy()
    app.run(host='0.0.0.0', port=5000)
