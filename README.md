# G-Guard: Full-Stack IoT Gate Automation System

## 📝 Overview

**G-Guard** is a robust, full-stack Internet of Things (IoT) home automation system designed to control and monitor a garage/gate motor securely. Evolving from a simple direct-MQTT controller, the system is now built with a centralized middleware architecture, ensuring high reliability, activity logging, and security.

## 🏗️ System Architecture

The project is divided into three main layers:

1. **Client Layer (Mobile App):** A custom-built Android application using Python and KivyMD. It sends asynchronous HTTP POST requests to the backend server.
2. **Middleware Layer (Flask Server):** Hosted on an Ubuntu Linux machine and managed via `systemd`. It receives HTTP requests, logs every action into an SQLite database, and acts as a bridge to publish commands to the MQTT broker. It is exposed securely to the internet via an `ngrok` tunnel.
3. **Hardware Layer (ESP8266 NodeMCU):** The physical execution node. It subscribes to the MQTT broker, receives `open` or `close` payloads, and controls physical relays connected to the gate motor.

## ✨ Key Features

* **Decoupled Architecture:** The mobile app never communicates directly with the hardware, enhancing security and allowing for centralized logging.
* **Hardware Reliability:** The ESP8266 firmware includes a built-in Watchdog Timer (WDT) and non-blocking delays to automatically recover from network drops or freezes, preventing the infamous "Zombie State".
* **Safe Boot Sequence:** Hardware pull-up resistors and strict boot-sequence programming ensure the gate relays never trigger accidentally during power outages or system restarts.
* **Persistent Background Services:** The Flask backend and Ngrok tunnel are managed via a custom Bash script and Linux `systemd` to ensure 100% uptime and automatic restarts on failure.
* **Asynchronous UI:** The Android app utilizes Kivy's `UrlRequest` to ensure the UI remains smooth and responsive while waiting for server replies.

## 🛠️ Tech Stack

### Hardware

* **Microcontroller:** NodeMCU ESP8266
* **Actuators:** 5V Relay Modules (Active Low)
* **Gate Motor:** LIFE Home Integration Gate Motor (or any motor with dedicated Open/Close dry-contact inputs)
* **Components:** 10kΩ Pull-up resistors, LEDs for WiFi and MQTT status indication.

### Software

* **Backend:** Python, Flask, SQLite, Pyngrok
* **Mobile App:** Python, Kivy, KivyMD
* **Firmware:** C++ (Arduino IDE format), `PubSubClient` library for MQTT
* **Server Infrastructure:** Ubuntu Linux, Bash scripting, `systemd`
* **Protocol:** MQTT (via EMQX public broker), HTTP/REST

## 🔌 Hardware Pinout (ESP8266)

| Component | ESP8266 Pin (NodeMCU) | Note |
| --- | --- | --- |
| **Close Relay** | `GPIO 5` (D1) | Active Low, pulled-up |
| **Open Relay** | `GPIO 4` (D2) | Active Low, pulled-up |
| **WiFi Status LED** | `GPIO 14` (D5) | Indicates Router Connection |
| **MQTT Status LED** | `GPIO 12` (D6) | Indicates Broker Connection |

## 🚀 Installation & Setup

### 1. Flask Backend

1. Clone the repository and navigate to the backend directory.
2. Create a virtual environment: `python3 -m venv venv` and activate it.
3. Install dependencies: `pip install -r requirements.txt`
4. Run the setup script: `chmod +x run.sh`
5. Configure `systemd` using the provided `gate_app.service` template and start the service: `sudo systemctl start gate_app`

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

**Hashem Osama Khair alla Alsharif** *Electrical Engineering Student at Al Hussein Technical University*