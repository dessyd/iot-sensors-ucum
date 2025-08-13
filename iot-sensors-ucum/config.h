/*
 * Configuration générale du projet IoT Sensors
 * Conforme au standard UCUM (Unified Code for Units of Measure)
 * 
 * Auteur: Dominique Dessy
 * Version: 1.0
 */

#ifndef CONFIG_H
#define CONFIG_H

// Paramètres réseau
#define MQTT_SERVER "192.168.1.15"  // Adresse du serveur MQTT (à adapter)
#define MQTT_PORT 1883
#define MQTT_CLIENT_PREFIX "arduino_mkr_"

// Intervalles de mesure (en millisecondes)
#define MEASUREMENT_INTERVAL 30000    // 30 secondes (Int1)
#define KEEPALIVE_INTERVAL 300000     // 5 minutes (Int2)
#define SENSOR_READ_DELAY 2000        // Délai entre lectures capteurs

// Topics MQTT
#define TOPIC_PREFIX "sensors/"
#define TOPIC_TEMPERATURE "temperature"
#define TOPIC_HUMIDITY "humidity"
#define TOPIC_PRESSURE "pressure"
#define TOPIC_ILLUMINANCE "illuminance"
#define TOPIC_STATUS "status"

// Configuration des LEDs et debug
#define DEBUG_SERIAL true
#define SERIAL_BAUD 9600

// Format des messages MQTT
#define USE_COMPACT_FORMAT true  // true = format compact, false = format UCUM complet

// Gestion du flag RETAIN pour les messages MQTT
#define USE_RETAIN_STATUS false        // true = status retained, false = monitoring temps réel
#define USE_RETAIN_MEASUREMENTS false  // true = mesures retained, false = flux temps réel

// Corrections de calibration des capteurs (valeurs à soustraire aux lectures)
#define TEMPERATURE_OFFSET 2.5    // °C - Correction température (valeur à soustraire)
#define HUMIDITY_OFFSET 0.0       // %RH - Correction humidité  
#define PRESSURE_OFFSET 0.0       // hPa - Correction pression
#define ILLUMINANCE_OFFSET 0.0    // lx - Correction luminosité

// Structure pour les capteurs avec codes UCUM standardisés
struct SensorConfigUCUM {
  String name;                    // Nom du capteur
  String ucum_code;              // Code UCUM officiel
  String ucum_display;           // Représentation d'affichage UCUM
  String common_name;            // Nom commun
  float threshold;               // Seuil de changement
  float min_value;               // Valeur minimale
  float max_value;               // Valeur maximale
  String quantity_type;          // Type de quantité physique
};

// Configuration des capteurs MKR ENV Shield selon standard UCUM
const SensorConfigUCUM SENSOR_CONFIGS[] = {
  {
    "temperature",               // nom
    "Cel",                      // Code UCUM pour degrés Celsius
    "°C",                       // Affichage
    "Temperature",              // Nom commun
    0.5,                        // Seuil 0.5°C
    -40.0, 85.0,               // Plage -40°C à +85°C
    "thermodynamic-temperature" // Type de quantité
  },
  {
    "humidity", 
    "%",                        // Code UCUM pour pourcentage
    "%",                        // Affichage (même chose)
    "Relative Humidity",        // Nom commun
    2.0,                        // Seuil 2%
    0.0, 100.0,                // Plage 0% à 100%
    "dimensionless-ratio"       // Type de quantité
  },
  {
    "pressure",
    "hPa",                      // Code UCUM pour hectopascal
    "hPa",                      // Affichage
    "Atmospheric Pressure",     // Nom commun
    1.0,                        // Seuil 1 hPa
    300.0, 1100.0,             // Plage typique
    "pressure"                  // Type de quantité
  },
  {
    "illuminance",
    "lx",                       // Code UCUM pour lux
    "lx",                       // Affichage
    "Illuminance",             // Nom commun
    10.0,                       // Seuil 10 lux
    0.0, 100000.0,             // Plage 0 à 100k lux
    "illuminance"               // Type de quantité
  }
};

// Fonction helper pour obtenir la config UCUM d'un capteur
SensorConfigUCUM getSensorConfigUCUM(String sensorType) {
  for (int i = 0; i < sizeof(SENSOR_CONFIGS) / sizeof(SensorConfigUCUM); i++) {
    if (SENSOR_CONFIGS[i].name == sensorType) {
      return SENSOR_CONFIGS[i];
    }
  }
  // Fallback pour capteurs non configurés
  return {"unknown", "1", "", "Unknown", 0.1, -999999.0, 999999.0, "unknown"};
}

// Codes UCUM supplémentaires pour extension future
namespace UCUM_CODES {
  // Température
  const String CELSIUS = "Cel";
  const String FAHRENHEIT = "[degF]";
  const String KELVIN = "K";
  
  // Pression
  const String PASCAL = "Pa";
  const String HECTOPASCAL = "hPa";
  const String KILOPASCAL = "kPa";
  const String BAR = "bar";
  const String ATMOSPHERE = "atm";
  
  // Luminosité
  const String LUX = "lx";
  const String CANDELA_PER_M2 = "cd/m2";
  
  // Électrique
  const String VOLT = "V";
  const String AMPERE = "A";
  const String WATT = "W";
  const String JOULE = "J";
  
  // Longueur/Distance
  const String METER = "m";
  const String CENTIMETER = "cm";
  const String MILLIMETER = "mm";
  const String KILOMETER = "km";
  
  // Vitesse
  const String METER_PER_SECOND = "m/s";
  const String KILOMETER_PER_HOUR = "km/h";
  
  // Masse
  const String GRAM = "g";
  const String KILOGRAM = "kg";
  
  // Concentration
  const String PPM = "[ppm]";
  const String PPB = "[ppb]";
  const String MOLE_PER_LITER = "mol/L";
  
  // Son
  const String DECIBEL = "dB";
  
  // Pourcentages et ratios
  const String PERCENT = "%";
  const String RATIO = "1";          // Unité sans dimension
}

#endif
