# Guide de configuration - IoT Sensors UCUM

## 🎯 Vue d'ensemble

Ce guide détaille toutes les options de configuration disponibles pour personnaliser votre système IoT Sensors UCUM selon vos besoins spécifiques.

## ⚙️ Configuration Arduino

### Structure des fichiers de configuration

```
iot-sensors-ucum/
├── config.h                    # Configuration globale
├── arduino_secrets.h           # Credentials (non versionné)  
└── arduino_secrets.h.template  # Template pour credentials
```

### Fichier arduino_secrets.h

Créé à partir du template, contient les informations sensibles :

```cpp
// Configuration réseau WiFi
#define SECRET_SSID "VotreReseauWiFi"
#define SECRET_PASS "VotreMotDePasseWiFi"

// Configuration MQTT
#define SECRET_MQTT_USER "mqtt_user"
#define SECRET_MQTT_PASS "VotreMotDePasseMQTT"

// Configuration serveur MQTT (optionnel si différent du défaut)
#define SECRET_MQTT_BROKER "192.168.1.100"  // IP ou hostname
#define SECRET_MQTT_PORT 1883                // Port MQTT
```

## 🚀 Profils de fréquence (v1.8)

### Configuration ultra-simple

Configuration en une seule ligne dans `config.h` :

```cpp
#define MEASUREMENT_FREQUENCY HIGH    // Temps réel
#define MEASUREMENT_FREQUENCY MEDIUM  // Équilibré (défaut)
#define MEASUREMENT_FREQUENCY LOW     // Économe en énergie
```

### Profils disponibles

#### HIGH - Monitoring temps réel
```cpp
#define MEASUREMENT_FREQUENCY HIGH
```
- **Mesures** : Toutes les 10 secondes
- **Keepalive** : Toutes les 1 minute (6 × mesure)
- **Usage** : Monitoring critique, laboratoire, démo
- **Détection offline** : 2 minutes
- **Consommation** : Élevée, WiFi très actif

#### MEDIUM - Configuration équilibrée (recommandée)
```cpp
#define MEASUREMENT_FREQUENCY MEDIUM
```
- **Mesures** : Toutes les 30 secondes  
- **Keepalive** : Toutes les 5 minutes (10 × mesure)
- **Usage** : Monitoring standard, bureau, maison
- **Détection offline** : 10 minutes
- **Consommation** : Modérée, bon compromis

#### LOW - Économie d'énergie  
```cpp
#define MEASUREMENT_FREQUENCY LOW
```
- **Mesures** : Toutes les 1 minute
- **Keepalive** : Toutes les 15 minutes (15 × mesure)
- **Usage** : Monitoring longue durée, extérieur, batterie
- **Détection offline** : 30 minutes
- **Consommation** : Faible, autonomie maximale

### Guide de sélection

| Situation | Profil recommandé | Justification |
|-----------|------------------|---------------|
| Serveur critique | HIGH | Réactivité maximale aux incidents |
| Domicile/bureau | MEDIUM | Équilibre performance/énergie |
| Station météo | LOW | Autonomie batterie importante |
| Développement | HIGH | Feedback rapide pour debug |
| Démo/présentation | HIGH | Réponse immédiate visible |

## 🔧 Calibration des capteurs (v1.6)

### Principe

Correction des biais systématiques par soustraction d'un offset :

```cpp
// Dans config.h
#define TEMPERATURE_OFFSET 2.5    // °C à soustraire
#define HUMIDITY_OFFSET 0.0       // %RH à soustraire  
#define PRESSURE_OFFSET 0.0       // hPa à soustraire
#define ILLUMINANCE_OFFSET 0.0    // lx à soustraire
```

### Méthode de calibration

#### 1. Détermination des offsets

**Pour la température :**
1. Placer l'Arduino près d'un thermomètre de référence calibré
2. Attendre stabilisation (15-20 minutes)
3. Relever les valeurs simultanément :
   - Référence : 22.0°C
   - Arduino : 24.5°C
   - **Offset = 24.5 - 22.0 = 2.5°C**

**Pour l'humidité :**
1. Utiliser un hygromètre de référence
2. Tester à différents niveaux d'humidité si possible
3. Calculer l'écart moyen

**Pour la pression :**
1. Comparer avec station météo locale
2. Corriger l'altitude si nécessaire
3. Vérifier sur plusieurs jours

#### 2. Application des corrections

```cpp
// Exemple de configuration après calibration
#define TEMPERATURE_OFFSET 2.5    // Capteur lit 2.5°C trop élevé
#define HUMIDITY_OFFSET -1.2      // Capteur lit 1.2% trop bas  
#define PRESSURE_OFFSET 0.0       // Capteur précis
#define ILLUMINANCE_OFFSET 0.0    // Capteur précis
```

### Validation des corrections

Vérification dans les logs de démarrage Arduino :
```text
=== Arduino IoT Sensors - Standard UCUM ===
Version: 1.8 (Frequency Profiles)
=== Corrections de calibration ===
Température: -2.5 °C
Humidité: +1.2 %RH
Pression: -0.0 hPa
Luminosité: -0.0 lx
```

## 📡 Configuration des messages MQTT

### Format des messages

#### Format complet (défaut)
```cpp
#define USE_COMPACT_FORMAT false
```
- Messages avec métadonnées UCUM complètes (~380 caractères)
- Compatibilité maximale avec tous les systèmes
- Toutes les informations de validation incluses

#### Format compact (optimisé)
```cpp  
#define USE_COMPACT_FORMAT true
```
- Messages optimisés pour réseaux contraints (~120 caractères)
- Gain de 68% sur la taille
- Codes UCUM essentiels préservés

### Configuration des flags RETAIN (v1.5)

```cpp
// Dans config.h
#define USE_RETAIN_STATUS false        // Messages de statut
#define USE_RETAIN_MEASUREMENTS false  // Messages de mesure
```

**Recommandations :**
- **false/false** : Monitoring temps réel (recommandé)
- **true/false** : Statut persistant, mesures temps réel
- **true/true** : Tous messages persistants (systèmes critiques)

### Seuils de détection de changement

```cpp
// Seuils pour déclencher l'envoi de mesures
#define TEMP_THRESHOLD 0.5        // °C
#define HUMIDITY_THRESHOLD 2.0    // %RH  
#define PRESSURE_THRESHOLD 1.0    // hPa
#define ILLUMINANCE_THRESHOLD 10  // lx
```

**Ajustement des seuils :**
- **Valeurs plus faibles** : Plus de messages, monitoring plus fin
- **Valeurs plus élevées** : Moins de messages, économie de bande passante

## 🔄 Configuration avancée (intervalles personnalisés)

### Pour utilisateurs expérimentés uniquement

Si les profils HIGH/MEDIUM/LOW ne suffisent pas :

```cpp
// Désactiver les profils automatiques
#undef MEASUREMENT_FREQUENCY

// Configuration manuelle
#define MEASUREMENT_INTERVAL 45000      // 45 secondes
#define KEEPALIVE_MULTIPLIER 8          // 8 × 45s = 6 minutes
#define KEEPALIVE_INTERVAL (MEASUREMENT_INTERVAL * KEEPALIVE_MULTIPLIER)
```

### Règles de cohérence

- **KEEPALIVE_INTERVAL** doit être > **MEASUREMENT_INTERVAL**
- **Multiplicateur recommandé** : entre 6 et 20
- **Timeout détection** = 2 × KEEPALIVE_INTERVAL

## 🐳 Configuration Docker

### Fichier .env

Variables d'environnement pour les services :

```bash
# Credentials MQTT
MQTT_USERNAME=mqtt_user
MQTT_PASSWORD=VotreMotDePasseSecurise

# Credentials InfluxDB  
INFLUX_USERNAME=admin
INFLUX_PASSWORD=password123
INFLUX_ORG=iot-sensors
INFLUX_BUCKET=sensor-data
INFLUX_TOKEN=VotreTokenInfluxDB

# Credentials Grafana
GRAFANA_USERNAME=admin  
GRAFANA_PASSWORD=admin123

# Configuration réseau
MQTT_PORT=1883
INFLUX_PORT=8086
GRAFANA_PORT=3000
```

### Configuration Mosquitto MQTT

#### Fichier mosquitto/mosquitto.conf
```conf
# Configuration de base
listener 1883
allow_anonymous false
password_file /mosquitto/config/passwd

# Logs
log_dest file /mosquitto/log/mosquitto.log
log_type error
log_type warning  
log_type notice
log_type information

# Persistance
persistence true
persistence_location /mosquitto/data/

# Limites de connection
max_connections 100
```

#### Gestion des utilisateurs
```bash
# Créer un utilisateur MQTT
docker-compose exec mosquitto mosquitto_passwd -c /mosquitto/config/passwd mqtt_user

# Ajouter d'autres utilisateurs  
docker-compose exec mosquitto mosquitto_passwd /mosquitto/config/passwd autre_user
```

### Configuration Telegraf

#### Collecte MQTT
```toml
[[inputs.mqtt_consumer]]
  servers = ["tcp://mosquitto:1883"]
  topics = ["sensors/+/+"]
  username = "$MQTT_USERNAME"
  password = "$MQTT_PASSWORD"
  data_format = "json"
  
  # Tags automatiques
  [[inputs.mqtt_consumer.tags]]
    source = "arduino_iot_sensors"
    project = "iot-sensors-ucum"
```

#### Traitement des données
```toml
# Conversion types de données
[[processors.converter]]
  [processors.converter.fields]
    temperature = "float"
    humidity = "float"
    pressure = "float" 
    illuminance = "float"

# Enrichissement UCUM
[[processors.enum]]
  [[processors.enum.mapping]]
    tag = "ucum_code"
    dest = "unit_display"
    [processors.enum.mapping.value_mappings]
      Cel = "°C"
      "%" = "%"
      hPa = "hPa" 
      lx = "lx"
```

### Configuration InfluxDB

#### Rétention des données
```bash
# Politique de rétention (30 jours par défaut)
influx bucket update \
  --name sensor-data \
  --retention 720h \
  --org iot-sensors
```

#### Index optimisés
```sql
-- Requêtes Flux optimisées
from(bucket: "sensor-data")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "sensor_readings")
  |> filter(fn: (r) => r.device_id == "mkr1010_AA1D11EE")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
```

## 📊 Configuration Grafana

### Variables de dashboard

```json
{
  "name": "device_id",
  "type": "query", 
  "query": "from(bucket: \"sensor-data\") |> range(start: -7d) |> distinct(column: \"device_id\")",
  "multi": true,
  "includeAll": true
}
```

### Alertes configurables

```json
{
  "alert": {
    "name": "Température élevée",
    "conditions": [
      {
        "query": "A",
        "reducer": "avg",
        "type": "query"
      }
    ],
    "executionErrorState": "alerting",
    "frequency": "10s",
    "handler": 1,
    "noDataState": "no_data"
  }
}
```

## 🔍 Validation de la configuration

### Tests automatiques
```bash
# Validation complète
./scripts/validate.sh

# Test configuration Arduino
arduino-cli compile --verify iot-sensors-ucum/

# Test services Docker
docker-compose config
docker-compose ps
```

### Monitoring de la configuration
```bash
# Vérifier les logs de configuration Arduino
# Via Serial Monitor Arduino IDE

# Vérifier la réception MQTT
mosquitto_sub -h localhost -p 1883 -u mqtt_user -P mqtt_password -t "sensors/+/+" -v

# Vérifier les données InfluxDB
curl -H "Authorization: Token $INFLUX_TOKEN" \
  "http://localhost:8086/api/v2/query" \
  --data-urlencode 'q=from(bucket:"sensor-data") |> range(start:-1h) |> count()'
```

---

**Guide de configuration v1.8** - *Personnalisation complète du système IoT Sensors UCUM*  
Dernière mise à jour : Août 2025
