#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "HUAWEI-4gNy";
const char* password = "csffb76673";
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;

// --- LWT Configuration ---
const char* lwt_topic   = "esp8266/status";
const char* lwt_payload = "offline";
const int   lwt_qos     = 1;
const bool  lwt_retain  = true;

// Pins
const int CLOSE_PIN = D0;
const int OPEN_PIN = D1;
const int WiFi_LED = D5;
const int MQTT_LED = D6;

WiFiClient espClient;
PubSubClient client(espClient);

// Non-blocking timer variables for background tasks
unsigned long lastReconnectAttempt = 0;

// Non-blocking relay variables
unsigned long relayTimer = 0;
bool pulsingOpen = false;
bool pulsingClose = false;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print(F("Connecting to "));
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500); 
    Serial.print(F("."));
    digitalWrite(WiFi_LED, !digitalRead(WiFi_LED));
    yield(); // explicitly feed the watchdog during WiFi connection
  }

  randomSeed(micros());

  Serial.println(F("\nWiFi connected"));
  Serial.print(F("IP address: "));
  Serial.println(WiFi.localIP());
  digitalWrite(WiFi_LED, HIGH);
}

void trig(const char* message){
  // Prevent triggering a new pulse if one is currently active
  if (pulsingOpen || pulsingClose) {
    Serial.println(F("Relay is busy, ignoring command..."));
    return; 
  }

  if (strcmp(message, "open") == 0) {
      Serial.println(F("Triggering OPEN relay pulse..."));
      pinMode(OPEN_PIN, OUTPUT);
      digitalWrite(OPEN_PIN, LOW); 
      pulsingOpen = true;
      relayTimer = millis(); // Start the timer
  }
  else if (strcmp(message, "close") == 0) {
      Serial.println(F("Triggering CLOSE relay pulse..."));
      pinMode(CLOSE_PIN, OUTPUT);
      digitalWrite(CLOSE_PIN, LOW); 
      pulsingClose = true;
      relayTimer = millis(); // Start the timer
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Safe string array initialization without using dynamic RAM heap
  char message[32]; 
  if (length > 31) length = 31; // Prevent buffer overflow crashes

  for (unsigned int i = 0; i < length; i++) {
    message[i] = (char)payload[i];
  }
  message[length] = '\0';

  trig(message);
}

boolean reconnect() {
  Serial.print(F("Attempting MQTT connection..."));
  
  // Clean, static creation of a unique Client ID without dynamic strings
  char clientId[30];
  snprintf(clientId, sizeof(clientId), "ESP8266-%04X", (uint16_t)random(0xffff));
  
  digitalWrite(MQTT_LED, !digitalRead(MQTT_LED));
  
  // Connect with LWT parameters
  if (client.connect(clientId, NULL, NULL, lwt_topic, lwt_qos, lwt_retain, lwt_payload)) {
    Serial.println(F("connected"));
    
    // Publish "online" status to overwrite the LWT
    client.publish(lwt_topic, "online", true);
    
    client.subscribe("relay/switch");
    digitalWrite(MQTT_LED, HIGH);
    return true;
  } else {
    digitalWrite(MQTT_LED, LOW);
    Serial.print(F("failed, rc="));
    Serial.print(client.state());
    Serial.println(F(" will try again."));
    return false;
  }
}

void setup() {
  digitalWrite(OPEN_PIN, HIGH);
  digitalWrite(CLOSE_PIN, HIGH);
  pinMode(OPEN_PIN, INPUT); 
  pinMode(CLOSE_PIN, INPUT); 

  Serial.begin(115200);
  
  pinMode(WiFi_LED, OUTPUT);
  pinMode(MQTT_LED, OUTPUT);
  
  digitalWrite(WiFi_LED, LOW);
  digitalWrite(MQTT_LED, LOW);

  setup_wifi();
  
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  client.setKeepAlive(5); // 5-second Keep-Alive
}

void loop() {  
  if (!client.connected()) {
    unsigned long now = millis();
    if (now - lastReconnectAttempt > 5000) {
      lastReconnectAttempt = now;
      if (reconnect()) {
        lastReconnectAttempt = 0;
      }
    }
  } else {
    client.loop();
  }

  // --- Non-Blocking Relay Logic ---
  // Check if 500ms has passed since the OPEN pulse started
  if (pulsingOpen && (millis() - relayTimer >= 500)) {
    pinMode(OPEN_PIN, INPUT);
    pulsingOpen = false;
    Serial.println(F("OPEN pulse completed"));
    client.publish("relay/feedback", "success");
  }

  // Check if 500ms has passed since the CLOSE pulse started
  if (pulsingClose && (millis() - relayTimer >= 500)) {
    pinMode(CLOSE_PIN, INPUT);
    pulsingClose = false;
    Serial.println(F("CLOSE pulse completed"));
    client.publish("relay/feedback", "success");
  }
}