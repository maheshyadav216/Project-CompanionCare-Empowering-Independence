//=============================================================================//
// Project/Tutorial       - CompanionCare: Empowering Independence
// Author                 - https://www.hackster.io/maheshyadav216
// Hardware               - UNIHIKER, M5StickC Plus, XIAO ESP32S3       
// Sensors                - Fermion BLE Sensor Beacon
// Software               - Arduino IDE, PlatformIO
// GitHub Repo of Project - https://github.com/maheshyadav216/Project-CompanionCare-Empowering-Independence 
// Code last Modified on  - 22/08/2024
//============================================================================//

// Project code for Caretaker Alert Device - XIAO ESP32S3

#include <WiFi.h>
#include <PubSubClient.h>

// WiFi settings
const char* ssid = "xxxxxxxxxxxx";
const char* password = "xxxxxxxxxx";

// MQTT settings
const char* mqtt_server = "192.168.0.107";
const int mqtt_port = 1883;
const char* topic_subscribe = "home/UNIHIKER/caretaker_buzzer";
const char* mqtt_username = "siot";
const char* mqtt_password = "dfrobot";

const int buzzerPin = 9;
volatile bool buzzerState = false;

const int redLED = 8;
const int greenLED = 7;

const int reset_button = 6;

WiFiClient espClient;
PubSubClient client(espClient);

void callback(char* topic, byte* message, unsigned int length) {
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
  }
  
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  Serial.println(messageTemp);

  if (String(topic) == topic_subscribe) {
    if (messageTemp == "Buzzer: SOS Alert") {
      digitalWrite(buzzerPin, LOW);
      digitalWrite(greenLED, LOW);
      digitalWrite(redLED, HIGH);
      buzzerState = true;
    }
  }
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("CareTaker", mqtt_username, mqtt_password)) {
      Serial.println("connected");
      client.subscribe(topic_subscribe);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(reset_button, INPUT_PULLUP);
  pinMode(greenLED, OUTPUT);
  pinMode(redLED, OUTPUT);
  pinMode(buzzerPin, OUTPUT);  
  digitalWrite(greenLED, HIGH);
  digitalWrite(redLED, LOW);
  digitalWrite(buzzerPin, HIGH);
  
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  reconnect();
}

void loop() {
  if (!digitalRead(reset_button)) {
    digitalWrite(greenLED, HIGH);
    digitalWrite(redLED, LOW);
    digitalWrite(buzzerPin, HIGH);
    buzzerState = false;
    Serial.println("Buzzer turned off");
  }

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  delay(1000);
}