/*
 * Projet IoT Sensors - Arduino MKR1010 + MKR ENV Shield
 * Conforme au standard UCUM pour les unités
 * Version 2.1.0 - Format unifié avec robustesse améliorée
 *
 * Auteur: Dominique Dessy
 * Date: Août 2025
 * Version: 2.1.0
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
unsigned long nextConnectionAttempt = 0;

// Dernières valeurs pour détecter les changements
float lastTemperature = -999;
float lastHumidity = -999;
float lastPressure = -999;
float lastIlluminance = -999;

// ===== NOUVEAU: Compteur pour le keepalive unifié =====
unsigned long measurementCounter = 0; // Compteur de cycles de mesure (unsigned long pour éviter débordement)

void setup()
{
  if (DEBUG_SERIAL)
  {
    Serial.begin(SERIAL_BAUD);

    unsigned long startTime = millis();
    while (!Serial)
    {
      if (millis() - startTime > 5000)
      {
        break;
      }
    }

    Serial.println("=== Arduino IoT Sensors - Standard UCUM ===");
    Serial.println("Version: 2.1.0 (Format unifié robuste)");
    Serial.println("Auteur: Dominique Dessy");
  }

  // Initialisation du shield ENV
  if (!ENV.begin())
  {
    Serial.println("ERREUR: Impossible d'initialiser le shield MKR ENV!");
    while (1)
      ;
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

  // Affichage de la configuration
  if (DEBUG_SERIAL)
  {
    Serial.println("=== Configuration v2.1 ===");
#if defined(MEASUREMENT_FREQUENCY) && (MEASUREMENT_FREQUENCY == HIGH)
    Serial.println("Fréquence: HIGH (temps réel)");
#elif defined(MEASUREMENT_FREQUENCY) && (MEASUREMENT_FREQUENCY == LOW)
    Serial.println("Fréquence: LOW (économe en énergie)");
#else
    Serial.println("Fréquence: MEDIUM (équilibré)");
#endif
    Serial.println("Mesure: " + String(MEASUREMENT_INTERVAL / 1000) + "s");
    Serial.println("Keepalive: toutes les " + String(KEEPALIVE_MEASUREMENT_COUNT) + " mesures");
    Serial.println("=> Keepalive tous les " + String((KEEPALIVE_MEASUREMENT_COUNT * MEASUREMENT_INTERVAL) / 1000) + "s");

    Serial.println("=== Corrections de calibration ===");
    Serial.println("Température: -" + String(TEMPERATURE_OFFSET) + " °C");
    Serial.println("Humidité: -" + String(HUMIDITY_OFFSET) + " %RH");
    Serial.println("Pression: -" + String(PRESSURE_OFFSET) + " hPa");
    Serial.println("Luminosité: -" + String(ILLUMINANCE_OFFSET) + " lx");
  }

  // Initialiser le compteur et faire un premier envoi
  measurementCounter = 0;
}

void loop()
{
  // Gestionnaire de connexion non-bloquant
  if (WiFi.status() != WL_CONNECTED)
  {
    connectToWiFi();
    delay(1000);
    return;
  }

  if (!mqttClient.connected())
  {
    reconnectMQTT();
  }
  else
  {
    mqttClient.poll();
  }

  unsigned long currentTime = millis();

  // Lecture et envoi des mesures à intervalle régulier
  if (currentTime - lastMeasurement >= MEASUREMENT_INTERVAL)
  {
    readAndSendWithKeepaliveLogic();
    lastMeasurement = currentTime;
    measurementCounter++;

    // Protection contre le débordement: reset périodique du compteur
    // Reset tous les 1 million de cycles pour éviter tout problème
    if (measurementCounter >= 1000000UL)
    {
      measurementCounter = 0;
    }

    // Le modulo dans readAndSendWithKeepaliveLogic() gère automatiquement le cycle
  }

  delay(1000);
}

void generateDeviceId()
{
  if (!ECCX08.begin())
  {
    Serial.println("ATTENTION: Puce crypto non disponible, utilisation d'un ID par défaut");
    deviceId = "mkr1010_default_" + String(random(1000, 9999));
    return;
  }

  String serialNumber = ECCX08.serialNumber();
  deviceId = "mkr1010_" + serialNumber.substring(serialNumber.length() - 8);

  Serial.println("ID device généré: " + deviceId);
}

void connectToWiFi()
{
  if (WiFi.status() == WL_CONNECTED)
  {
    return;
  }

  Serial.print("Tentative de connexion au WiFi...");
  WiFi.begin(SECRET_SSID, SECRET_PASS);

  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000)
  {
    Serial.print(".");
    delay(500);
  }

  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println("\\nWiFi connecté!");
    Serial.print("Adresse IP: ");
    Serial.println(WiFi.localIP());
    syncRTCTime();
  }
  else
  {
    Serial.println("\\nÉchec de la connexion WiFi. Nouvelle tentative à venir...");
  }
}

void setupMQTT()
{
  mqttClient.setUsernamePassword(SECRET_MQTT_USER, SECRET_MQTT_PASS);

  String clientId = MQTT_CLIENT_PREFIX + deviceId;
  mqttClient.setId(clientId);

  // Message de dernière volonté (LWT)
  String willTopic = String(TOPIC_PREFIX) + deviceId + "/" + TOPIC_STATUS;
  mqttClient.beginWill(willTopic, true, 1);
  String willPayload = "{\"v\":\"offline\",\"t\":\"" + getTimestamp() + "\"}";
  mqttClient.print(willPayload);
  mqttClient.endWill();
}

void reconnectMQTT()
{
  if (millis() < nextConnectionAttempt)
  {
    return;
  }

  Serial.print("Tentative de connexion au broker MQTT... ");

  if (mqttClient.connect(MQTT_SERVER, MQTT_PORT))
  {
    Serial.println("Connecté!");
    nextConnectionAttempt = 0;
  }
  else
  {
    Serial.println("Échec. Nouvelle tentative dans 5 secondes.");
    nextConnectionAttempt = millis() + 5000;
  }
}

// ===== FONCTION PRINCIPALE UNIFIÉE =====
void readAndSendWithKeepaliveLogic()
{
  // Lecture des capteurs avec application des corrections de calibration
  float temperature = ENV.readTemperature(CELSIUS) - TEMPERATURE_OFFSET;
  float humidity = ENV.readHumidity() - HUMIDITY_OFFSET;
  float pressure = ENV.readPressure(MILLIBAR) - PRESSURE_OFFSET;
  float illuminance = ENV.readIlluminance(LUX) - ILLUMINANCE_OFFSET;

  delay(SENSOR_READ_DELAY);

  // Déterminer si c'est un cycle de keepalive (force l'envoi)
  bool forceKeepalive = (measurementCounter % KEEPALIVE_MEASUREMENT_COUNT) == 0;

  if (DEBUG_SERIAL && forceKeepalive)
  {
    Serial.println("=== CYCLE KEEPALIVE (mesure " + String(measurementCounter) + ", cycle " + String((unsigned long)(measurementCounter / KEEPALIVE_MEASUREMENT_COUNT) + 1) + ") ===");
  }

  // Test unifié pour chaque capteur: changement significatif OU keepalive
  SensorConfigUCUM tempConfig = getSensorConfigUCUM("temperature");
  if (abs(temperature - lastTemperature) >= tempConfig.threshold || forceKeepalive)
  {
    sendMeasurementUnified("temperature", temperature, tempConfig);
    lastTemperature = temperature;
  }

  SensorConfigUCUM humConfig = getSensorConfigUCUM("humidity");
  if (abs(humidity - lastHumidity) >= humConfig.threshold || forceKeepalive)
  {
    sendMeasurementUnified("humidity", humidity, humConfig);
    lastHumidity = humidity;
  }

  SensorConfigUCUM pressConfig = getSensorConfigUCUM("pressure");
  if (abs(pressure - lastPressure) >= pressConfig.threshold || forceKeepalive)
  {
    sendMeasurementUnified("pressure", pressure, pressConfig);
    lastPressure = pressure;
  }

  SensorConfigUCUM lightConfig = getSensorConfigUCUM("illuminance");
  if (abs(illuminance - lastIlluminance) >= lightConfig.threshold || forceKeepalive)
  {
    sendMeasurementUnified("illuminance", illuminance, lightConfig);
    lastIlluminance = illuminance;
  }

  // Envoi d'un message de statut lors du keepalive
  if (forceKeepalive)
  {
    sendStatusUnified();
  }
}

// ===== FONCTIONS D'ENVOI UNIFIÉES (FORMAT COMPACT SEULEMENT) =====
void sendMeasurementUnified(String sensorType, float value, SensorConfigUCUM config)
{
  String topic = String(TOPIC_PREFIX) + deviceId + "/" + config.name;

  DynamicJsonDocument doc(128);
  doc["v"] = round(value * 100.0) / 100.0;
  doc["u"] = config.ucum_code;
  doc["t"] = getTimestamp();

  String payload;
  serializeJson(doc, payload);

  mqttClient.beginMessage(topic, USE_RETAIN_MEASUREMENTS);
  mqttClient.print(payload);
  mqttClient.endMessage();

  if (DEBUG_SERIAL)
  {
    String reason = (measurementCounter % KEEPALIVE_MEASUREMENT_COUNT) == 0 ? " [KEEPALIVE]" : " [CHANGE]";
    Serial.println("-> " + config.name + reason + ": " + payload);
  }
}

void sendStatusUnified()
{
  String topic = String(TOPIC_PREFIX) + deviceId + "/" + TOPIC_STATUS;

  DynamicJsonDocument doc(128);
  doc["v"] = "online";
  doc["ip"] = WiFi.localIP().toString();
  doc["t"] = getTimestamp();
  doc["c"] = (unsigned long)(measurementCounter / KEEPALIVE_MEASUREMENT_COUNT) + 1; // Numéro du cycle keepalive (division entière explicite)

  String payload;
  serializeJson(doc, payload);

  mqttClient.beginMessage(topic, USE_RETAIN_STATUS);
  mqttClient.print(payload);
  mqttClient.endMessage();

  if (DEBUG_SERIAL)
  {
    Serial.println("-> STATUS [KEEPALIVE]: " + payload);
  }
}

// ===== Fonctions utilitaires pour le temps =====
void syncRTCTime()
{
  unsigned long epoch;
  int attempts = 0;

  Serial.print("Synchronisation du RTC via NTP...");
  do
  {
    epoch = WiFi.getTime();
    if (epoch == 0)
    {
      Serial.print(".");
      delay(2000);
      attempts++;
    }
  } while (epoch == 0 && attempts < 5);

  if (epoch > 0)
  {
    rtc.setEpoch(epoch);
    Serial.println("\\nRTC synchronisé!");
    Serial.println("Heure actuelle: " + getTimestamp());
  }
  else
  {
    Serial.println("\\nERREUR: Impossible de synchroniser le RTC. Utilisation de l'heure par défaut.");
  }
}

String getTimestamp()
{
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
