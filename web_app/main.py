import os
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
import paho.mqtt.client as mqtt

app = Flask(__name__)

JORDAN_TZ = ZoneInfo("Asia/Amman")

# Configure SQLite Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'garage.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(JORDAN_TZ))
    action = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(255), nullable=False)

# MQTT Configuration
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "relay/switch"

# Create MQTT Client (Compatible with paho-mqtt 1.x)
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        app.logger.info("Connected to MQTT Broker successfully!")
    else:
        app.logger.error("Failed to connect to MQTT Broker, return code %d\n", rc)

mqtt_client.on_connect = on_connect

def start_mqtt():
    try:
        app.logger.info(f"Attempting to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()  # Starts a background thread to handle network traffic
    except Exception as e:
        app.logger.error(f"MQTT Connection failed: {e}")

# Modern Dark Mode HTML Template for the Web Dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Garage Door Control Dashboard</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --text-color: #cbd5e1;
            --primary-color: #3b82f6;
            --primary-hover: #2563eb;
            --success-color: #10b981;
            --error-color: #ef4444;
            --card-bg: #1e293b;
            --table-header: #334155;
            --border-color: #475569;
        }
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background-color: var(--bg-color); 
            color: var(--text-color);
            margin: 0;
            padding: 2rem;
            display: flex;
            justify-content: center;
        }
        .container { 
            width: 100%;
            max-width: 900px; 
            background: var(--card-bg); 
            padding: 2.5rem; 
            border-radius: 16px; 
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5); 
        }
        h1 { 
            text-align: center; 
            color: #fff; 
            margin-bottom: 2rem;
            font-size: 2.5rem;
            font-weight: 700;
        }
        .controls {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 3rem;
            padding: 2.5rem;
            background: rgba(255,255,255,0.02);
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        .btn { 
            width: 220px; 
            padding: 1rem; 
            font-size: 1.125rem; 
            font-weight: 600;
            color: white; 
            background-color: var(--primary-color); 
            border: none; 
            border-radius: 9999px; 
            cursor: pointer; 
            transition: all 0.2s ease;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .btn:hover:not(:disabled) { 
            background-color: var(--primary-hover); 
            transform: translateY(-2px);
            box-shadow: 0 6px 8px -1px rgba(59, 130, 246, 0.6);
        }
        .btn:active:not(:disabled) {
            transform: translateY(0);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .msg {
            margin-top: 1.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;
            display: none;
            animation: fadeIn 0.3s ease;
            width: 100%;
            max-width: 300px;
            text-align: center;
            box-sizing: border-box;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        .success-msg { background: rgba(16, 185, 129, 0.1); color: var(--success-color); border: 1px solid rgba(16, 185, 129, 0.2); }
        .error-msg { background: rgba(239, 68, 68, 0.1); color: var(--error-color); border: 1px solid rgba(239, 68, 68, 0.2); }
        
        h2 { color: #f8fafc; font-size: 1.5rem; border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
        
        .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th, td { padding: 1rem; border-bottom: 1px solid var(--border-color); }
        th { background-color: var(--table-header); color: #f8fafc; font-weight: 600; text-transform: uppercase; font-size: 0.875rem; letter-spacing: 0.05em; }
        th:first-child { border-top-left-radius: 8px; }
        th:last-child { border-top-right-radius: 8px; }
        tr:hover { background-color: rgba(255,255,255,0.03); }
        td { font-size: 0.95rem; }
        .empty-state { text-align: center; padding: 2rem; color: #94a3b8; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Garage Control Center</h1>
        
        <div class="controls">
            <button id="toggleBtn" class="btn" onclick="toggleGate()">
                <svg style="width:24px;height:24px;margin-right:8px" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M11,16.5L18,12L11,7.5V11H6V13H11V16.5Z" />
                </svg>
                Toggle Gate
            </button>
            <div id="status-msg" class="msg success-msg">Gate toggled successfully!</div>
            <div id="error-msg" class="msg error-msg">Failed to toggle gate.</div>
        </div>

        <h2>Activity Logs</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%">ID</th>
                        <th style="width: 30%">Timestamp (UTC)</th>
                        <th style="width: 30%">Action</th>
                        <th style="width: 30%">Source</th>
                    </tr>
                </thead>
                <tbody>
                    {% if logs %}
                        {% for log in logs %}
                        <tr>
                            <td>#{{ log.id }}</td>
                            <td>{{ log.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</td>
                            <td>
                                <span style="display:inline-block;padding:4px 10px;background:rgba(59,130,246,0.1);color:#60a5fa;border-radius:12px;font-size:0.85em;border:1px solid rgba(59,130,246,0.2);font-weight:500">
                                    {{ log.action }}
                                </span>
                            </td>
                            <td>{{ log.source }}</td>
                        </tr>
                        {% endfor %}
                    {% else %}
                        <tr>
                            <td colspan="4" class="empty-state">No activity logs recorded yet.</td>
                        </tr>
                    {% endif %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function toggleGate() {
            const btn = document.getElementById('toggleBtn');
            const statusMsg = document.getElementById('status-msg');
            const errorMsg = document.getElementById('error-msg');
            
            btn.disabled = true;
            btn.innerHTML = '<svg style="width:24px;height:24px;margin-right:8px;animation:spin 1s linear infinite" viewBox="0 0 24 24"><path fill="currentColor" d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z"/></svg> Processing...';
            statusMsg.style.display = 'none';
            errorMsg.style.display = 'none';

            fetch('/api/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ source: 'Web Dashboard' })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    statusMsg.style.display = 'block';
                    setTimeout(() => location.reload(), 1200); // Reload to show new log
                } else {
                    errorMsg.innerText = data.message || 'Error occurred';
                    errorMsg.style.display = 'block';
                    resetBtn(btn);
                }
            })
            .catch(error => {
                errorMsg.innerText = 'Network error. Please try again.';
                errorMsg.style.display = 'block';
                resetBtn(btn);
            });
        }
        
        function resetBtn(btn) {
            btn.disabled = false;
            btn.innerHTML = '<svg style="width:24px;height:24px;margin-right:8px" viewBox="0 0 24 24"><path fill="currentColor" d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M11,16.5L18,12L11,7.5V11H6V13H11V16.5Z" /> </svg> Toggle Gate';
        }
        
        // Add CSS keyframes for loading spinner dynamically
        const style = document.createElement('style');
        style.innerHTML = '@keyframes spin { 100% { transform: rotate(360deg); } }';
        document.head.appendChild(style);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    try:
        # Fetch the most recent 20 logs from the database
        recent_logs = Log.query.order_by(Log.timestamp.desc()).limit(20).all()
        return render_template_string(HTML_TEMPLATE, logs=recent_logs)
    except Exception as e:
        app.logger.error(f"Database error rendering index: {e}")
        return f"System Error: {e}. If this is your first run, the database might not be initialized properly.", 500

@app.route('/api/control', methods=['POST'])
def control_gate():
    try:
        # قراءة البيانات القادمة من تطبيق الهاتف
        data = request.json
        command = data.get('command') # نتوقع أن يكون 'open' أو 'close'
        source = data.get('source', 'Unknown')

        # التحقق من صحة الأمر
        if command in ['open', 'close']:
            # إرسال الأمر عبر MQTT
            mqtt_client.publish("relay/switch", command)
            
            # تسجيل العملية في قاعدة البيانات
            # تأكد من تعديل كود الإضافة ليطابق اسم جدولك في SQLAlchemy أو SQLite
            new_log = Log(action=f"Gate {command.capitalize()}", source=source)
            db.session.add(new_log)
            db.session.commit()
            
            return jsonify({"status": "success", "message": f"Command '{command}' sent successfully!"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid command"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Initialize Database on boot
    with app.app_context():
        # Creates 'garage.db' file and the logs table if they don't exist
        db.create_all()
        
    # Start the MQTT network loop in a background thread
    start_mqtt()
    
    # Run the Flask Server
    # use_reloader=False prevents the app.run from running twice (and starting MQTT thread twice) under debug mode
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
