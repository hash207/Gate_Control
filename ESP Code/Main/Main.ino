#include <WiFi.h>
#include <PubSubClient.h>
#include <esp_task_wdt.h>

#define WDT_TIMEOUT 15

const char* ssid = "HUAWEI-4gNy";
const char* password = "csffb76673";
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;
const int MQTT_LED = 0;
const int WiFi_LED = 1;
const int RELAY_PIN = 21;

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
    esp_task_wdt_reset(); // تصفير المؤقت أثناء الانتظار
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
  if (message == "toggle") {
      Serial.println("Triggering relay pulse (Direct Active Low)...");
      
      pinMode(RELAY_PIN, OUTPUT);
      digitalWrite(RELAY_PIN, LOW); 
      
      delay(500);           
      
      pinMode(RELAY_PIN, INPUT);
      
      Serial.println("Relay pulse completed");
  }

  client.publish("relay/feedback", "success");
}

void callback(char* topic, byte* payload, unsigned int length) {
  // استخدام مصفوفة أحرف ثابتة بدلاً من String لتفادي تشتت الذاكرة
  char message[length + 1];
  for (int i = 0; i < length; i++) {
    message[i] = (char)payload[i];
  }
  message[length] = '\0';

  trig(message);
}

void reconnect() {
  while (!client.connected()) {
    esp_task_wdt_reset(); // تصفير المؤقت أثناء محاولة إعادة الاتصال
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    
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
      delay(2000);
    }
  }
}

String reciev(){
  String incomingMessage;
  return incomingMessage;
}

void setup() {
  // تأمين حالة المنفذ برمجياً قبل تفعيل الدوائر
  digitalWrite(RELAY_PIN, HIGH);
  pinMode(RELAY_PIN, INPUT); 

  Serial.begin(9600);
  pinMode(WiFi_LED, OUTPUT);
  pinMode(MQTT_LED, OUTPUT);

  // إعداد Watchdog Timer لمعمارية ESP32 v3.x
  esp_task_wdt_config_t wdt_config = {
    .timeout_ms = WDT_TIMEOUT * 1000,
    .idle_core_mask = (1 << portNUM_PROCESSORS) - 1,
    .trigger_panic = true
  };
  esp_task_wdt_init(&wdt_config);
  esp_task_wdt_add(NULL);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  esp_task_wdt_reset(); 
  
    if (!client.connected()) {
    reconnect();
  }
  client.loop();

  reciev();
}