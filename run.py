import subprocess
import os
from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def index():
    return "Traffic Analyzer Web UI"


def start_mitmproxy():
    """Starts mitmproxy in the background on all interfaces."""
    # We force bind to 0.0.0.0 so it is reachable from your Windows machine
    cmd = [
        'mitmproxy',
        '-s', 'src.proxy',
        '--set', 'mitmproxy_bind_address=0.0.0.0'
    ]
    subprocess.Popen(cmd, stdout=None, stderr=None)


if __name__ == "__main__":
    start_mitmproxy()
    app.run(host='0.0.0.0', port=5000)
