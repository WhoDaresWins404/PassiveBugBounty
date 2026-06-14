import subprocess
from flask import Flask
from src.mitm_plugin import endpoint_analyzer


app = Flask(__name__)

@app.route('/')
def index():
    return "Traffic Analyzer Web UI"


def start_mitmproxy():
    """Starts mitmproxy in the background on all interfaces."""
    cmd = [
        'mitmproxy',
        '-s', 'src.mitm_plugin',
        '--set', 'mitmproxy_bind_address=0.0.0.0',
        '--listen-port', '8080'  # Explicitly bind to 8080 on all interfaces
    ]
    subprocess.Popen(cmd, stdout=None, stderr=None)


if __name__ == "__main__":
    start_mitmproxy()
    app.run(host='0.0.0.0', port=5000)
