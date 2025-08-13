/*
 * Corrections pour la gestion du flag RETAIN dans les messages MQTT
 */

// Option 1: Tous les status sans retain (recommandé pour du monitoring temps réel)
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

  // CORRECTION: Supprimer le flag retain pour éviter la duplication
  mqttClient.beginMessage(topic, false);  // false = pas de retain
  mqttClient.print(payload);
  mqttClient.endMessage();

  if (DEBUG_SERIAL) {
    Serial.println("-> Keepalive Compact Sent (no retain): " + payload);
  }
}

// Option 2: Retain uniquement pour les changements d'état (offline/online)
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

  // CORRECTION: Retain uniquement pour le premier message ou après reconnexion
  static bool firstStatusSent = false;
  bool useRetain = !firstStatusSent;
  firstStatusSent = true;

  mqttClient.beginMessage(topic, useRetain);
  mqttClient.print(payload);
  mqttClient.endMessage();

  if (DEBUG_SERIAL) {
    Serial.println("-> Keepalive Compact Sent " + String(useRetain ? "(retained)" : "(no retain)") + ": " + payload);
  }
}

// Option 3: Configuration via define dans config.h
#ifndef USE_RETAIN_STATUS
#define USE_RETAIN_STATUS false  // true = status retained, false = pas de retain
#endif

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

  // Configuration via define
  mqttClient.beginMessage(topic, USE_RETAIN_STATUS);
  mqttClient.print(payload);
  mqttClient.endMessage();

  if (DEBUG_SERIAL) {
    Serial.println("-> Keepalive Compact Sent " + String(USE_RETAIN_STATUS ? "(retained)" : "(no retain)") + ": " + payload);
  }
}
