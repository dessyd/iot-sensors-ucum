/*
 * Projet IoT Sensors - Arduino MKR1010 + MKR ENV Shield
 * Conforme au standard UCUM pour les unités
 * Version optimisée avec RTC et contrôle des flags RETAIN MQTT
 * 
 * Auteur: Dominique Dessy
 * Date: Août 2025
 * Version: 1.5
 */

#include <RTCZero.h>
#include <WiFiNINA.h>
#include <ArduinoMqttClient.h>
#include <Arduino_MKRENV.h>
#include <ArduinoECCX08.h>
#include <ArduinoJson.h>
#include "config.h"
#include "arduino_secrets.h"

// Clients réseau et temps
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);
RTCZero rtc; // RTC pour la gestion du temps

// Variables globales
String deviceId;
String siteLocation;
unsigned long lastMeasurement = 0;
unsigned long lastKeepalive = 0;
unsigned long nextConnectionAttempt = 0;

// Dernières valeurs pour détecter les changements
float lastTemperature = -999;
float lastHumidity = -999;
float lastPressure = -999;
float lastIlluminance = -999;

void setup() {
  if (DEBUG_SERIAL) {
    Serial.begin(SERIAL_BAUD);
    while (!Serial);
    Serial.println("=== Arduino IoT Sensors - Standard UCUM ===");
    Serial.println("Version: 1.5 (MQTT RETAIN Fix)");
    Serial.println("Auteur: Dominique Dessy");
  }

  // Initialisation du shield ENV
  if (!ENV.begin()) {
    Serial.println("ERREUR: Impossible d'initialiser le shield MKR ENV!");
    while (1);
  }

  // Initialisation du RTC
  rtc.begin();

  // Génération de l'ID unique basé sur la puce crypto
  generateDeviceId();
  
  // Configuration MQTT
  setupMQTT();

  // Démarrage de la connexion WiFi (non-bloquant)
  connectToWiFi();
  
  Serial.println("Arduino prêt - ID: " + deviceId);
  Serial.println("Unités conformes standard UCUM");
  
  // Test des tailles de messages (optionnel)
  if (DEBUG_SERIAL) {
    testMessageSizes();
  }
  
  // Envoi du premier keepalive
  sendKeepalive();
  lastKeepalive = millis();
}

void loop() {
  // Gestionnaire de connexion non-bloquant
  if (WiFi.status() != WL_CONNECTED) {
    // Si le WiFi est perdu, on gère la reconnexion.
    // La boucle s'arrête ici jusqu'à ce que le WiFi soit rétabli.
    connectToWiFi();
    delay(1000); // Courte pause pour éviter de surcharger le processeur
    return;
  }

  if (!mqttClient.connected()) {
    // Si le WiFi est OK mais MQTT déconnecté, on tente de reconnecter MQTT.
    reconnectMQTT();
  } else {
    // Si tout est connecté, on poll le client MQTT.
    mqttClient.poll();
  }

  unsigned long currentTime = millis();

  // Lecture et envoi des mesures si changement détecté
  if (currentTime - lastMeasurement >= MEASUREMENT_INTERVAL) {
    readAndSendIfChanged();
    lastMeasurement = currentTime;
  }

  // Envoi du keepalive complet
  if (currentTime - lastKeepalive >= KEEPALIVE_INTERVAL) {
    #if USE_COMPACT_FORMAT
      sendKeepaliveCompact();
    #else
      sendKeepalive();
    #endif
    lastKeepalive = currentTime;
  }

  delay(1000); // Pause courte
}

void generateDeviceId() {
  // Utilisation du numéro de série de la puce crypto ECCX08
  if (!ECCX08.begin()) {
    Serial.println("ATTENTION: Puce crypto non disponible, utilisation d'un ID par défaut");
    deviceId = "mkr1010_default_" + String(random(1000, 9999));
    return;
  }

  String serialNumber = ECCX08.serialNumber();
  deviceId = "mkr1010_" + serialNumber.substring(serialNumber.length() - 8);
  
  Serial.println("ID device généré: " + deviceId);
}

void connectToWiFi() {
  // Tente la connexion WiFi de manière non-bloquante
  if (WiFi.status() == WL_CONNECTED) {
    return; // Déjà connecté
  }

  Serial.print("Tentative de connexion au WiFi...");
  WiFi.begin(SECRET_SSID, SECRET_PASS);

  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) {
    Serial.print(".");
    delay(500);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connecté!");
    Serial.print("Adresse IP: ");
    Serial.println(WiFi.localIP());
    // Une fois le WiFi connecté, on synchronise l'heure
    syncRTCTime();
  } else {
    Serial.println("\nÉchec de la connexion WiFi. Nouvelle tentative à venir...");
  }
}

void setupMQTT() {
  mqttClient.setUsernamePassword(SECRET_MQTT_USER, SECRET_MQTT_PASS);
  
  String clientId = MQTT_CLIENT_PREFIX + deviceId;
  mqttClient.setId(clientId);
  
  // Message de dernière volonté (LWT)
  String willTopic = String(TOPIC_PREFIX) + deviceId + "/" + TOPIC_STATUS;
  mqttClient.beginWill(willTopic, true, 1);
  String willPayload = "{\"status\":\"offline\",\"timestamp\":\"" + getTimestamp() + "\"}";
  mqttClient.print(willPayload);
  mqttClient.endWill();
}

void reconnectMQTT() {
  // Tente la connexion MQTT de manière non-bloquante
  if (millis() < nextConnectionAttempt) {
    return; // Attendre avant la prochaine tentative
  }

  Serial.print("Tentative de connexion au broker MQTT... ");

  if (mqttClient.connect(MQTT_SERVER, MQTT_PORT)) {
    Serial.println("Connecté!");
    // Réinitialiser le timer de tentative après une connexion réussie
    nextConnectionAttempt = 0;
  } else {
    Serial.println("Échec. Nouvelle tentative dans 5 secondes.");
    // Planifier la prochaine tentative dans 5 secondes
    nextConnectionAttempt = millis() + 5000;
  }
}

void readAndSendIfChanged() {
  // Lecture des capteurs
  float temperature = ENV.readTemperature();
  float humidity = ENV.readHumidity();  
  float pressure = ENV.readPressure();
  float illuminance = ENV.readIlluminance();

  delay(SENSOR_READ_DELAY);

  // Utilisation des configurations UCUM pour l'envoi
  SensorConfigUCUM tempConfig = getSensorConfigUCUM("temperature");
  if (abs(temperature - lastTemperature) >= tempConfig.threshold) {
    #if USE_COMPACT_FORMAT
      sendMeasurementUCUMCompact("temperature", temperature, tempConfig);
    #else
      sendMeasurementUCUM("temperature", temperature, tempConfig);
    #endif
    lastTemperature = temperature;
  }

  SensorConfigUCUM humConfig = getSensorConfigUCUM("humidity");
  if (abs(humidity - lastHumidity) >= humConfig.threshold) {
    #if USE_COMPACT_FORMAT
      sendMeasurementUCUMCompact("humidity", humidity, humConfig);
    #else
      sendMeasurementUCUM("humidity", humidity, humConfig);
    #endif
    lastHumidity = humidity;
  }

  SensorConfigUCUM pressConfig = getSensorConfigUCUM("pressure");
  if (abs(pressure - lastPressure) >= pressConfig.threshold) {
    #if USE_COMPACT_FORMAT
      sendMeasurementUCUMCompact("pressure", pressure, pressConfig);
    #else
      sendMeasurementUCUM("pressure", pressure, pressConfig);
    #endif
    lastPressure = pressure;
  }

  SensorConfigUCUM lightConfig = getSensorConfigUCUM("illuminance");
  if (abs(illuminance - lastIlluminance) >= lightConfig.threshold) {
    #if USE_COMPACT_FORMAT
      sendMeasurementUCUMCompact("illuminance", illuminance, lightConfig);
    #else
      sendMeasurementUCUM("illuminance", illuminance, lightConfig);
    #endif
    lastIlluminance = illuminance;
  }
}

void sendMeasurementUCUM(String sensorType, float value, SensorConfigUCUM config) {
  String topic = String(TOPIC_PREFIX) + deviceId + "/" + config.name;
  
  DynamicJsonDocument doc(256);

  doc["quantity"] = config.quantity_type;
  doc["value"] = round(value * 100.0) / 100.0;
  doc["unit"] = config.ucum_code;
  doc["display_unit"] = config.ucum_display;
  doc["timestamp"] = getTimestamp();

  String payload;
  serializeJson(doc, payload);
  
  // Utilisation de la configuration pour le flag retain
  mqttClient.beginMessage(topic, USE_RETAIN_MEASUREMENTS);
  mqttClient.print(payload);
  mqttClient.endMessage();

  if (DEBUG_SERIAL) {
    Serial.println("-> Sent" + String(USE_RETAIN_MEASUREMENTS ? " (retained)" : "") + ": " + payload);
  }
}

// Version compacte de sendMeasurementUCUM 
void sendMeasurementUCUMCompact(String sensorType, float value, SensorConfigUCUM config) {
  String topic = String(TOPIC_PREFIX) + deviceId + "/" + config.name;
  
  DynamicJsonDocument doc(128);

  doc["v"] = round(value * 100.0) / 100.0;
  doc["u"] = config.ucum_code;
  doc["t"] = getTimestamp();

  String payload;
  serializeJson(doc, payload);
  
  // Utilisation de la configuration pour le flag retain
  mqttClient.beginMessage(topic, USE_RETAIN_MEASUREMENTS);
  mqttClient.print(payload);
  mqttClient.endMessage();

  if (DEBUG_SERIAL) {
    Serial.println("-> Sent Compact" + String(USE_RETAIN_MEASUREMENTS ? " (retained)" : "") + ": " + payload);
  }
}

void sendKeepalive() {
  String topic = String(TOPIC_PREFIX) + deviceId + "/" + TOPIC_STATUS;
  
  DynamicJsonDocument doc(512);
  doc["status"] = "online";
  doc["ip_address"] = WiFi.localIP().toString();
  doc["firmware_version"] = "1.5";
  doc["timestamp"] = getTimestamp();

  JsonObject sensors = doc.createNestedObject("sensors");
  sensors["temperature"] = round(lastTemperature * 100.0) / 100.0;
  sensors["humidity"] = round(lastHumidity * 100.0) / 100.0;
  sensors["pressure"] = round(lastPressure * 100.0) / 100.0;
  sensors["illuminance"] = round(lastIlluminance * 100.0) / 100.0;

  String payload;
  serializeJson(doc, payload);

  // Utilisation de la configuration pour le flag retain des status
  mqttClient.beginMessage(topic, USE_RETAIN_STATUS);
  mqttClient.print(payload);
  mqttClient.endMessage();

  if (DEBUG_SERIAL) {
    Serial.println("-> Keepalive Sent" + String(USE_RETAIN_STATUS ? " (retained)" : "") + ": " + payload);
  }
}

// Version compacte de keepalive
void sendKeepaliveCompact() {
  String topic = String(TOPIC_PREFIX) + deviceId + "/" + TOPIC_STATUS;
  
  DynamicJsonDocument doc(256);
  doc["st"] = "on";
  doc["ip"] = WiFi.localIP().toString();
  doc["t"] = getTimestamp();

  JsonObject s = doc.createNestedObject("s");
  s["temp"] = round(lastTemperature * 100.0) / 100.0;
  s["hum"] = round(lastHumidity * 100.0) / 100.0;
  s["press"] = round(lastPressure * 100.0) / 100.0;
  s["lux"] = round(lastIlluminance * 100.0) / 100.0;

  String payload;
  serializeJson(doc, payload);

  // Utilisation de la configuration pour le flag retain des status
  mqttClient.beginMessage(topic, USE_RETAIN_STATUS);
  mqttClient.print(payload);
  mqttClient.endMessage();

  if (DEBUG_SERIAL) {
    Serial.println("-> Keepalive Compact Sent" + String(USE_RETAIN_STATUS ? " (retained)" : "") + ": " + payload);
  }
}

// ===== Fonctions utilitaires pour le temps =====

// Met à jour l'heure du RTC via NTP
void syncRTCTime() {
  unsigned long epoch;
  int attempts = 0;
  
  Serial.print("Synchronisation du RTC via NTP...");
  do {
    epoch = WiFi.getTime();
    if (epoch == 0) {
      Serial.print(".");
      delay(2000);
      attempts++;
    }
  } while (epoch == 0 && attempts < 5);

  if (epoch > 0) {
    rtc.setEpoch(epoch);
    Serial.println("\nRTC synchronisé!");
    Serial.println("Heure actuelle: " + getTimestamp());
  } else {
    Serial.println("\nERREUR: Impossible de synchroniser le RTC. Utilisation de l'heure par défaut.");
  }
}

// Retourne un timestamp formaté ISO 8601
String getTimestamp() {
  char timestamp[25];
  sprintf(timestamp, "%04d-%02d-%02dT%02d:%02d:%02dZ",
          2000 + rtc.getYear(),
          rtc.getMonth(),
          rtc.getDay(),
          rtc.getHours(),
          rtc.getMinutes(),
          rtc.getSeconds());
  return String(timestamp);
}


// Fonction pour tester la taille des messages
void testMessageSizes() {
  if (DEBUG_SERIAL) {
    Serial.println("=== Test tailles messages ===");
    
    // Test message normal
    SensorConfigUCUM config = getSensorConfigUCUM("temperature");
    
    StaticJsonDocument<512> docNormal;
    docNormal["device_id"] = deviceId;
    docNormal["sensor_type"] = "temperature";
    docNormal["value"] = 23.5;
    docNormal["timestamp"] = WiFi.getTime();
    docNormal["location"] = "test_location";
    docNormal["measurement_type"] = "sensor_reading";
    
    JsonObject ucum = docNormal.createNestedObject("ucum");
    ucum["code"] = config.ucum_code;
    ucum["display"] = config.ucum_display;
    ucum["common_name"] = config.common_name;
    ucum["quantity_type"] = config.quantity_type;
    
    JsonObject validation = docNormal.createNestedObject("validation");
    validation["min_value"] = config.min_value;
    validation["max_value"] = config.max_value;
    validation["in_range"] = true;
    
    String normalOutput;
    serializeJson(docNormal, normalOutput);
    
    // Test message compact
    StaticJsonDocument<256> docCompact;
    docCompact["id"] = deviceId;
    docCompact["type"] = "temperature";
    docCompact["val"] = 23.5;
    docCompact["ts"] = WiFi.getTime();
    docCompact["unit"] = config.ucum_code;
    docCompact["sym"] = config.ucum_display;
    docCompact["ok"] = true;
    
    String compactOutput;
    serializeJson(docCompact, compactOutput);
    
    Serial.println("Message normal: " + String(normalOutput.length()) + " chars");
    Serial.println("Message compact: " + String(compactOutput.length()) + " chars");
    Serial.println("Gain: " + String(normalOutput.length() - compactOutput.length()) + " chars");
    
    if (normalOutput.length() < 400) {
      Serial.println("✅ Taille normale acceptable");
    } else {
      Serial.println("⚠️ Taille normale élevée - considérer le format compact");
    }
    
    Serial.println("Normal: " + normalOutput);
    Serial.println("Compact: " + compactOutput);
  }
}
