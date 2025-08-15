# Documentation technique - IoT Sensors UCUM

## Architecture système

### Vue d'ensemble
Le système IoT Sensors UCUM est conçu autour d'une architecture microservices containerisée, avec un Arduino MKR WiFi 1010 comme capteur principal.

```
┌─────────────────┐    MQTT     ┌──────────────┐    HTTP    ┌─────────────┐
│  Arduino MKR    │────────────▶│   Mosquitto  │───────────▶│  Telegraf   │
│  WiFi 1010      │             │   (Broker)   │            │ (Collector) │
│  + ENV Shield   │             └──────────────┘            └─────────────┘
└─────────────────┘                                                │
                                                                   │ Line Protocol
                                                                   ▼
┌─────────────────┐                                         ┌─────────────┐
│    Grafana      │◀────────────── HTTP API ──────────────▶│  InfluxDB   │
│  (Dashboard)    │                                         │ (Time-series)│
└─────────────────┘                                         └─────────────┘
```

### Composants

#### Arduino MKR WiFi 1010
- **Firmware** : Code C++ avec bibliothèques Arduino standard
- **Capteurs** : MKR ENV Shield (température, humidité, pression, luminosité)
- **Sécurité** : Puce crypto ECCX08 pour ID unique
- **Communication** : WiFi + MQTT avec authentification

#### Stack Docker
- **Mosquitto** : Broker MQTT avec authentification
- **InfluxDB v2** : Base de données time-series
- **Telegraf** : Agent de collecte et transformation
- **Grafana** : Interface de visualisation et alerting

## Protocole de données

### Format des messages MQTT

#### Messages de mesure (Topic: `sensors/{device_id}/{sensor_type}`)
```json
{
  "device_id": "mkr1010_AA1D11EE",
  "sensor_type": "temperature",
  "value": 23.5,
  "ucum": {
    "code": "Cel",
    "display": "°C",
    "definition": "degree Celsius"
  },
  "validation": {
    "in_range": true,
    "min_value": -40.0,
    "max_value": 85.0
  },
  "timestamp": "2025-08-13T15:06:05Z",
  "metadata": {
    "location": "indoor",
    "calibration_applied": true
  }
}
```

#### Messages de statut (Topic: `sensors/{device_id}/status`)
```json
{
  "device_id": "mkr1010_AA1D11EE",
  "status": "online",
  "uptime": 3600,
  "ip_address": "192.168.1.218",
  "wifi_rssi": -65,
  "memory_free": 25600,
  "timestamp": "2025-08-13T15:06:05Z",
  "measurements": {
    "temperature": {"value": 23.5, "ucum": "Cel"},
    "humidity": {"value": 45.2, "ucum": "%"},
    "pressure": {"value": 1013.25, "ucum": "hPa"},
    "illuminance": {"value": 350, "ucum": "lx"}
  }
}
```

### Codes UCUM utilisés

| Grandeur physique | Code UCUM | Symbole | Définition |
|------------------|-----------|---------|------------|
| Température | `Cel` | °C | Degré Celsius |
| Humidité relative | `%` | % | Pourcentage |
| Pression atmosphérique | `hPa` | hPa | Hectopascal |
| Éclairement lumineux | `lx` | lx | Lux |

## Configuration Arduino

### Structure des fichiers
```
iot-sensors-ucum/
├── iot-sensors-ucum.ino     # Programme principal
├── config.h                 # Configuration globale
├── arduino_secrets.h        # Credentials (non versionné)
└── arduino_secrets.h.template  # Template pour credentials
```

### Configuration globale (config.h)

#### Profils de fréquence (v1.8)
```cpp
// Profils prédéfinis
#define LOW    1    // Économe en énergie  
#define MEDIUM 2    // Équilibré (défaut)
#define HIGH   3    // Temps réel

// Configuration simple
#define MEASUREMENT_FREQUENCY MEDIUM

// Résolution automatique des intervalles
#if MEASUREMENT_FREQUENCY == HIGH
  #define MEASUREMENT_INTERVAL 10000    // 10 secondes
  #define KEEPALIVE_MULTIPLIER 6        // 6 × 10s = 1 minute
#elif MEASUREMENT_FREQUENCY == LOW  
  #define MEASUREMENT_INTERVAL 60000    // 60 secondes
  #define KEEPALIVE_MULTIPLIER 15       // 15 × 1min = 15 minutes
#else
  #define MEASUREMENT_INTERVAL 30000    // 30 secondes (MEDIUM)
  #define KEEPALIVE_MULTIPLIER 10       // 10 × 30s = 5 minutes
#endif
```

#### Calibration des capteurs (v1.6)
```cpp
// Corrections de calibration (valeurs à soustraire aux lectures)
#define TEMPERATURE_OFFSET 2.5    // °C
#define HUMIDITY_OFFSET 0.0       // %RH
#define PRESSURE_OFFSET 0.0       // hPa  
#define ILLUMINANCE_OFFSET 0.0    // lx
```

#### Seuils de détection de changement
```cpp
// Seuils pour envoi des mesures
#define TEMP_THRESHOLD 0.5        // °C
#define HUMIDITY_THRESHOLD 2.0    // %RH
#define PRESSURE_THRESHOLD 1.0    // hPa
#define ILLUMINANCE_THRESHOLD 10  // lx
```

### Formats de message

#### Format complet (défaut)
```cpp
#define USE_COMPACT_FORMAT false
```
- Messages avec métadonnées UCUM complètes
- ~380 caractères par message
- Compatibilité maximale

#### Format compact (optimisé)  
```cpp
#define USE_COMPACT_FORMAT true
```
- Messages optimisés pour réseaux contraints
- ~120 caractères par message (-68%)
- Codes UCUM préservés

## Pipeline de données

### Transformation Telegraf

#### Processeur MQTT Consumer
```toml
[[inputs.mqtt_consumer]]
  servers = ["tcp://mosquitto:1883"]
  topics = ["sensors/+/+"]
  username = "mqtt_user"
  password = "mqtt_password"
  data_format = "json"
  
  # Enrichissement des tags
  [[inputs.mqtt_consumer.tags]]
    source = "arduino_iot_sensors"
```

#### Processeurs de transformation
```toml
# Conversion des codes UCUM en unités SI
[[processors.converter]]
  [processors.converter.fields]
    temperature = "float"
    humidity = "float" 
    pressure = "float"
    illuminance = "float"

# Enrichissement métadonnées
[[processors.enum]]
  [[processors.enum.mapping]]
    tag = "sensor_type"
    dest = "sensor_category"
    [processors.enum.mapping.value_mappings]
      temperature = "environmental"
      humidity = "environmental"
      pressure = "atmospheric"
      illuminance = "optical"
```

#### Output InfluxDB
```toml
[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "$INFLUX_TOKEN"
  organization = "iot-sensors"
  bucket = "sensor-data"
  
  # Gestion de la rétention
  bucket_tag = "sensor_type"
  exclude_bucket_tag = true
```

### Structure des données InfluxDB

#### Measurement: `sensor_readings`
```
sensor_readings,device_id=mkr1010_AA1D11EE,sensor_type=temperature,ucum_code=Cel value=23.5,in_range=true 1692892800000000000
sensor_readings,device_id=mkr1010_AA1D11EE,sensor_type=humidity,ucum_code=% value=45.2,in_range=true 1692892800000000000
```

**Tags** (indexés):
- `device_id` : Identifiant unique du device
- `sensor_type` : Type de capteur (temperature, humidity, etc.)
- `ucum_code` : Code UCUM de l'unité
- `location` : Localisation (si configurée)

**Fields** (valeurs):
- `value` : Valeur numérique du capteur
- `in_range` : Validation de la plage (boolean)
- `calibration_applied` : Application de la calibration (boolean)

## Sécurité

### Authentification MQTT
- **Utilisateur** : `mqtt_user`
- **Mot de passe** : Défini dans `.env`
- **ACL** : Restriction des topics par device

### Tokens InfluxDB
- **Token admin** : Accès complet via API
- **Token lecture** : Grafana read-only
- **Rotation** : Recommandée tous les 90 jours

### Isolation réseau
```yaml
# docker-compose.yml
networks:
  iot-network:
    driver: bridge
    internal: false  # Accès externe via ports mappés uniquement
```

### Sécurisation Arduino
- **ID unique** : Basé sur puce crypto ECCX08
- **Credentials** : Stockés dans `arduino_secrets.h` (non versionné)
- **TLS** : Recommandé en production

## Monitoring et alerting

### Métriques système
- **Connectivité** : Dernière réception de données par device
- **Qualité signal** : RSSI WiFi
- **Performance** : Latence des messages MQTT
- **Santé** : Uptime et mémoire libre Arduino

### Dashboards Grafana

#### Dashboard principal : "IoT Sensors - Conforme UCUM"
- **Variables** : Device, type de capteur, période
- **Panneaux** : Séries temporelles par type UCUM
- **Alertes** : Seuils configurables par grandeur

#### Dashboard système : "IoT Infrastructure"
- **MQTT** : Statistiques broker Mosquitto  
- **InfluxDB** : Utilisation storage et performance
- **Telegraf** : Métriques de collecte

### Règles d'alerte

#### Alertes capteurs
```json
{
  "alert": "Température critique",
  "condition": "avg(temperature) > 35 OR avg(temperature) < 5",
  "frequency": "10s",
  "notifications": ["email", "webhook"]
}
```

#### Alertes infrastructure
```json
{
  "alert": "Device offline", 
  "condition": "last(status) > 2 * keepalive_interval",
  "frequency": "1m",
  "notifications": ["slack"]
}
```

## Déploiement et maintenance

### Scripts de déploiement
```bash
# Déploiement complet
./scripts/deploy.sh

# Validation post-déploiement  
./scripts/validate.sh

# Backup des données
./scripts/backup.sh

# Mise à jour
./scripts/update.sh
```

### Rétention des données
- **Données brutes** : 30 jours
- **Agrégations horaires** : 1 an
- **Agrégations journalières** : 5 ans
- **Nettoyage automatique** : Tâche InfluxDB

### Maintenance périodique
- **Logs** : Rotation automatique via Docker
- **Certificats** : Renouvellement si TLS activé
- **Base de données** : Compaction automatique InfluxDB
- **Monitoring** : Vérification des alertes

## Troubleshooting

### Diagnostics automatiques
```bash
# Test complet de la chaîne
./scripts/validate.sh

# Test connectivité MQTT
mosquitto_pub -h localhost -p 1883 -u mqtt_user -P mqtt_password -t "test" -m "hello"

# Vérification InfluxDB
curl -H "Authorization: Token $INFLUX_TOKEN" http://localhost:8086/api/v2/ready
```

### Logs principaux
```bash
# Arduino (via serial monitor)
# MQTT broker
docker-compose logs mosquitto

# Collecteur Telegraf
docker-compose logs telegraf

# Base de données  
docker-compose logs influxdb

# Dashboard
docker-compose logs grafana
```

### Problèmes courants et solutions

Voir [TROUBLESHOOTING.md](TROUBLESHOOTING.md) pour le guide complet de résolution des problèmes.

---

**Documentation technique v1.8** - *Architecture et implémentation détaillées*  
Dernière mise à jour : Août 2025
