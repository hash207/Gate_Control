# Activate the virtual environment
source /home/hashem-alsharif/Desktop/Hashem/My_Work/Gate_Control/gate_venv/bin/activate

# Start the Flask app in the background
python3 "/home/hashem-alsharif/Desktop/Hashem/My_Work/Gate_Control/web_app/main.py" &

# Wait a few seconds for Flask to start
sleep 3

# Start ngrok tunnel
python3 /home/hashem-alsharif/Desktop/Hashem/My_Work/Gate_Control/any/start_ngrok.py

# End working in background
python3 /home/hashem-alsharif/Desktop/Hashem/My_Work/Gate_Control/any/kill.py
