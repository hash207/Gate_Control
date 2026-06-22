#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "HUAWEI-4gNy";
const char* password = "csffb76673";
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;

// المنافذ الآمنة في ESP8266 (حسب المسميات المطبوعة على لوحة NodeMCU)
const int CLOSE_PIN = D1;  // D1
const int OPEN_PIN = D2;   // D2
const int WiFi_LED = D5;  // D5
const int MQTT_LED = D6;  // D6

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500); // الـ delay هنا يقوم أوتوماتيكياً بتصفير الـ Watchdog الداخلي
    Serial.print(".");
    digitalWrite(WiFi_LED,  !digitalRead(WiFi_LED));
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(WiFi_LED, 1);
}

void trig(String message){
  if (message == "open") {
      Serial.println("Triggering OPEN relay pulse...");
      
      pinMode(OPEN_PIN, OUTPUT);
      digitalWrite(OPEN_PIN, LOW); 
      
      delay(500);           
      
      pinMode(OPEN_PIN, INPUT);
      Serial.println("OPEN pulse completed");
  }
  else if (message == "close") {
      Serial.println("Triggering CLOSE relay pulse...");
      
      pinMode(CLOSE_PIN, OUTPUT);
      digitalWrite(CLOSE_PIN, LOW); 
      
      delay(500);           
      
      pinMode(CLOSE_PIN, INPUT);
      Serial.println("CLOSE pulse completed");
  }

  client.publish("relay/feedback", "success");
}

void callback(char* topic, byte* payload, unsigned int length) {
  char message[length + 1];
  for (int i = 0; i < length; i++) {
    message[i] = (char)payload[i];
  }
  message[length] = '\0';

  trig(message);
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    
    digitalWrite(MQTT_LED, !digitalRead(MQTT_LED));
    
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe("relay/switch");
      digitalWrite(MQTT_LED, 1);
    } else {
      digitalWrite(MQTT_LED, 0);
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      
      delay(2000); 
    }
  }
}

void setup() {
  // تأمين المنافذ قبل تهيئتها كمدخلات (Floating High)
  digitalWrite(OPEN_PIN, HIGH);
  digitalWrite(CLOSE_PIN, HIGH);
  pinMode(OPEN_PIN, INPUT); 
  pinMode(CLOSE_PIN, INPUT); 

  Serial.begin(9600);
  
  pinMode(WiFi_LED, OUTPUT);
  pinMode(MQTT_LED, OUTPUT);
  
  // إطفاء اللمبات كحالة افتراضية
  digitalWrite(WiFi_LED, 0);
  digitalWrite(MQTT_LED, 0);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {  
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}