# G-Guard: Advanced IoT Gate Controller

## 📝 Overview
**G-Guard** is a robust, full-stack Internet of Things (IoT) home automation system designed to control and monitor a garage/gate motor securely. Evolving from a simple direct-MQTT controller, the system is now built with a centralized middleware architecture, ensuring high reliability, real-time hardware state tracking, activity logging, and enterprise-grade security.

## 🏗️ System Architecture
The project is divided into three main layers:

1. **Client Layer (Mobile App):** A custom-built Android application using Python and KivyMD. It relies strictly on HTTP protocol (no client-side MQTT required). It sends asynchronous POST requests to control the gate and polls a GET endpoint for real-time status updates.
2. **Middleware Layer (Flask Server):** Hosted on an Ubuntu Linux machine. It runs a dedicated `paho-mqtt` background thread via `loop_start()` to handle MQTT traffic without blocking HTTP threads. It logs actions into an SQLite database, maintains a live global state dictionary, and bridges commands securely to the internet via an `ngrok` tunnel.
3. **Hardware Layer (ESP8266 NodeMCU):** The physical execution node. It subscribes to the EMQX public broker, receives `open` or `close` payloads, and utilizes non-blocking timers to control physical relays connected to the gate motor.

## ✨ Key Features
* **Decoupled Architecture:** The mobile app never communicates directly with the hardware, enhancing security and allowing for centralized control and logging.
* **Live Status Tracking (LWT):** Implements MQTT Last Will and Testament (LWT). The board registers a Retained QoS 1 offline message upon connection. The Flask server dynamically updates its global state dictionary the moment the hardware connects or disconnects.
* **Crash Prevention & Memory Management:** The ESP8266 firmware avoids `delay()` entirely, relying on `millis()` for non-blocking relay pulses. All capital-S `String` objects were replaced with `char` arrays and `snprintf()` to prevent heap memory fragmentation and random Watchdog Timer (WDT) resets.
* **Dynamic Asynchronous UI:** The Android app utilizes Kivy's `UrlRequest` and `Clock.schedule_interval` to poll the server's `/api/status` endpoint every 2 seconds. The UI dynamically reflects live hardware feedback and connection states (Online/Offline with color coding).
* **Safe Boot Sequence:** Hardware pull-up resistors and strict boot-sequence programming ensure the gate relays never trigger accidentally during power outages or system restarts.
* **Persistent Background Services:** Managed via Linux `systemd` unit files (with environment variables for ngrok authentication), ensuring the Flask app and tunnel achieve 100% uptime with automatic restart policies. *(Docker containerization is also supported).*

## 🛠️ Tech Stack

### Hardware
* **Microcontroller:** NodeMCU ESP8266
* **Actuators:** 5V Relay Modules (Active Low)
* **Gate Motor:** LIFE Home Integration Gate Motor (or any motor with dedicated Open/Close dry-contact inputs)
* **Components:** 10kΩ Pull-up resistors, LEDs for WiFi and MQTT status indication.

### Software
* **Backend:** Python, Flask, SQLite, Pyngrok, Paho-MQTT, Docker
* **Mobile App:** Python, Kivy, KivyMD
* **Firmware:** C++ (Arduino IDE format), `PubSubClient` library
* **Server Infrastructure:** Ubuntu Linux, Bash scripting, `systemd`, Docker Engine
* **Protocol:** MQTT (via EMQX public broker), HTTP/REST

## 🔌 API Endpoints (Flask Middleware)
* `POST /api/control` - Translates HTTP commands (`open`/`close`) into MQTT payloads and logs the action.
* `GET /api/status` - Instantly serves the `esp_state` dictionary to clients for UI updates.

## 🔌 Hardware Pinout (ESP8266)

| Component | ESP8266 Pin (NodeMCU) | Note |
| --- | --- | --- |
| **Close Relay** | `GPIO 5` (D1) | Active Low, pulled-up |
| **Open Relay** | `GPIO 4` (D2) | Active Low, pulled-up |
| **WiFi Status LED** | `GPIO 14` (D5) | Indicates Router Connection |
| **MQTT Status LED** | `GPIO 12` (D6) | Indicates Broker Connection |

## 🚀 Installation & Setup

### 1. Flask Backend (Systemd or Docker)
1. Clone the repository and navigate to the backend directory.
2. Create a virtual environment: `python3 -m venv venv` and activate it.
3. Install dependencies: `pip install -r requirements.txt`
4. Configure `systemd` using the provided `gate_app.service` template and start the service: `sudo systemctl start gate_app`
*(Alternatively, build and run the provided `Dockerfile` mapping the SQLite database as a volume).*

### 2. NodeMCU Firmware
1. Open `Main.ino` in the Arduino IDE.
2. Update your WiFi credentials and MQTT broker details.
3. Flash the code to the ESP8266. *Note: Ensure the 10kΩ pull-up resistors are connected to D1 and D2 before powering the gate motor to prevent floating signals.*

### 3. Android Application
1. Update the `FLASK_SERVER_URL` in `main.py` with your active Ngrok static URL.
2. Compile to an APK using Buildozer: `buildozer android debug`
3. Install the APK on your Android device.

## 🗺️ Roadmap & Future Developments
* [ ] **Bicycle Mobile Node:** Integrating a bicycle dynamo with an AC-to-DC rectification and TP4056 charging circuit to power an ESP32 BLE node. The ESP32 will send a Bluetooth signal to a smartphone (acting as a gateway) to automatically send the HTTP request and open the gate upon arrival.
* [ ] **Web Dashboard:** Expanding the Flask app to serve a frontend dashboard for viewing historical gate activity logs.
* [ ] **Authentication:** Adding token-based API authentication between the Android app and the Flask backend.

## 👨‍💻 Author
**Hashem Osama Khairalla Alsharif**
*Electrical Engineering Student at Al-Hussein Technical University (HTU)*