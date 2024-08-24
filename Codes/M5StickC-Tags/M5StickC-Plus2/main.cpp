//=============================================================================//
// Project/Tutorial       - CompanionCare: Empowering Independence
// Author                 - https://www.hackster.io/maheshyadav216
// Hardware               - UNIHIKER, M5StickC Plus, XIAO ESP32S3       
// Sensors                - Fermion BLE Sensor Beacon
// Software               - Arduino IDE, PlatformIO
// GitHub Repo of Project - https://github.com/maheshyadav216/Project-CompanionCare-Empowering-Independence 
// Code last Modified on  - 22/08/2024
// Code/Content license   - (CC BY-NC-SA 4.0) https://creativecommons.org/licenses/by-nc-sa/4.0/
//============================================================================//

// Project code for Smart Tag. M5StickC Plus2
// This Tag will be attached to Keychain

#include <M5StickCPlus2.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <BLEDevice.h>
#include <BLEScan.h>

const int scanTime = 5; // Duration of BLE scan in seconds
BLEScan* pBLEScan;

// WiFi settings
const char* ssid = "xxxxxxxxxx";
const char* password = "xxxxxxxxxxx";

// MQTT settings
const char* mqtt_server = "192.168.0.107";
const int mqtt_port = 1883;
const char* topic_subscribe = "home/UNIHIKER/keychain_buzzer";
const char* topic_publish = "home/keychain";
const char* mqtt_username = "siot";
const char* mqtt_password = "dfrobot";

const int buzzerPin = 2;
volatile bool buzzerState = false;

WiFiClient espClient;
PubSubClient client(espClient);

void playTone(int pin, int frequency, int duration) {
  tone(pin, frequency, duration);
  delay(duration); // Wait for the tone to finish
  noTone(pin);     // Stop the tone on the pin
}

void buzzerON(){
  playTone(buzzerPin, 1000, 150); // Play 1000 Hz for 500 milliseconds
  delay(50);                    // Wait for a second
  playTone(buzzerPin, 1000, 150); // Play 1000 Hz for 500 milliseconds
  delay(1000);                    // Wait for a second
  playTone(buzzerPin, 1000, 150); // Play 1000 Hz for 500 milliseconds
  delay(50);                    // Wait for a second
  playTone(buzzerPin, 1000, 150); // Play 1000 Hz for 500 milliseconds
  delay(1000); 
}

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
    if (messageTemp == "Buzzer: Keychain") {
      buzzerState = true;
    }
  }
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("Keychain", mqtt_username, mqtt_password)) {
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
  auto cfg = M5.config();
  StickCP2.begin(cfg);
  Serial.begin(115200);
  
  StickCP2.Display.setRotation(1);
  StickCP2.Display.setTextSize(2);
  StickCP2.Display.fillScreen(BLACK);

  // Initialize BLE
  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan(); // Create a BLE scan object
  pBLEScan->setActiveScan(true); // Active scan uses more power but gets results faster
  
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
  StickCP2.update();

  if (StickCP2.BtnA.wasPressed()) {
    StickCP2.Speaker.end();
    buzzerState = false;
    Serial.println("Buzzer turned off");
  }

  StickCP2.Display.setCursor(0, 10);
  StickCP2.Display.setTextColor(ORANGE, BLACK);
  StickCP2.Display.print("Keychain TAG");
  StickCP2.Display.setCursor(0, 50);
  StickCP2.Display.setTextColor(WHITE, BLACK);
  StickCP2.Display.print("Scanning...");

  // Start BLE scan
  BLEScanResults foundDevices = pBLEScan->start(scanTime, false);

  int bestRSSI = -100; // Initialize with a very low RSSI
  String nearestRoom = "Unknown";

  // Iterate through found devices
  for (int i = 0; i < foundDevices.getCount(); i++) {
    BLEAdvertisedDevice device = foundDevices.getDevice(i);

    // Check if the device is one of our room beacons
    if (device.haveName()) {
      String deviceName = device.getName().c_str();
      if (deviceName == "Bedroom-Beacon" || 
          deviceName == "Kitchen-Beacon" || 
          deviceName == "LivingRoom-Beacon" || 
          deviceName == "Office-Beacon") {
        
        int rssi = device.getRSSI();
        if (rssi > bestRSSI) {
          bestRSSI = rssi;
          // Map beacon name to room name
          if (deviceName == "Bedroom-Beacon") nearestRoom = "Bedroom";
          else if (deviceName == "Kitchen-Beacon") nearestRoom = "Kitchen";
          else if (deviceName == "LivingRoom-Beacon") nearestRoom = "Living Room";
          else if (deviceName == "Office-Beacon") nearestRoom = "Office";
        }
      }
    }
  }

  if ((buzzerState == true) && (nearestRoom != "Unknown")){
    buzzerON();
  }

  // Display the room with the strongest signal
  StickCP2.Display.fillScreen(BLACK);
  if (nearestRoom != "Unknown") {
    StickCP2.Display.setCursor(0, 90);
    StickCP2.Display.setTextColor(GREEN, BLACK);
    StickCP2.Display.printf("Nearest Room:\n%s", nearestRoom.c_str());
  } else {
    StickCP2.Display.setCursor(0, 90);
    StickCP2.Display.setTextColor(RED, BLACK);
    StickCP2.Display.print("No beacons found");
  }

  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  static unsigned long lastPublish = 0;
  if (millis() - lastPublish > 5000) {
    lastPublish = millis();
  // Example: Publish a message
  client.publish(topic_publish, nearestRoom.c_str());
  }
}
