# Simple Flask web server (web_dashboard.py)
from flask import Flask, render_template, jsonify, send_file
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/status')
def status():
    # Return current system status
    status_info = {
        'last_check': datetime.now().isoformat(),
        'alerts_today': len([f for f in os.listdir('alerts') if f.endswith('.jpg')]),
        'system_status': 'running'
    }
    return jsonify(status_info)

@app.route('/alerts')
def list_alerts():
    alerts = sorted(os.listdir('alerts'), reverse=True)
    return jsonify(alerts[:10])  # Last 10 alerts

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)