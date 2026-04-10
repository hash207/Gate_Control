#include <WiFi.h>
#include <PubSubClient.h>
//#include <SoftwareSerial.h>

const char* ssid = "HUAWEI-4gNy";
const char* password = "csffb76673";
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;
const int MQTT_LED = 0;
const int WiFi_LED = 1;
const int RELAY_PIN = 21;

WiFiClient espClient;
PubSubClient client(espClient);

// RX = D1 (GPIO 5) 
// TX = D2 (GPIO 4)
//SoftwareSerial arduino(D2, D3); // RX, TX

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    digitalWrite(WiFi_LED,  !digitalRead(WiFi_LED));
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(WiFi_LED,  1);
}

void trig(String message){
  // إذا كانت الرسالة "toggle"
  if (message == "toggle") {
      Serial.println("Triggering relay pulse (Direct Active Low)...");
      
      // 1. لتشغيل الريلاي: نحول المنفذ إلى مخرج ونعطيه صفر فولت (GND)
      pinMode(RELAY_PIN, OUTPUT);
      digitalWrite(RELAY_PIN, LOW); 
      
      // 2. الانتظار لمدة نصف ثانية (النبضة)
      delay(500);           
      
      // 3. لإطفاء الريلاي: نعيد المنفذ كـ "مدخل" ليطفو (يقطع التيار تماماً)
      pinMode(RELAY_PIN, INPUT);
      
      Serial.println("Relay pulse completed");
  }

  client.publish("relay/feedback", "success");
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  trig(message);
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    digitalWrite(MQTT_LED, !digitalRead(0));
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe("relay/switch");
      digitalWrite(MQTT_LED, 1);
    } else {
      digitalWrite(MQTT_LED, 0);
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      // Wait 2 seconds before retrying
      delay(2000);
    }
  }
}

String reciev(){
  String incomingMessage;
  /*if (arduino.available() > 0) {
    
    // Read the incoming data until the newline character '\n'
    // This captures the whole string sent by nodemcu.println()
    incomingMessage += arduino.readStringUntil('\n');
    Serial.println(incomingMessage);
    client.publish("hash/Test", incomingMessage.c_str());
    
  }*/
  return incomingMessage;
}

void setup() {
  // نجعل المنفذ "مدخل" كحالة افتراضية ليكون الريلاي مطفأً عند بدء التشغيل
  pinMode(RELAY_PIN, INPUT); 

  // باقي الكود الخاص بك
  Serial.begin(9600);
  pinMode(WiFi_LED, OUTPUT);
  pinMode(MQTT_LED, OUTPUT);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  reciev();
}