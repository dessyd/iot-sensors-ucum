# IoT Sensors UCUM - Projet de monitoring environnemental

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/ddessy/iot-sensors-ucum)
[![UCUM](https://img.shields.io/badge/UCUM-compliant-green.svg)](https://ucum.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Description

Système IoT complet pour le monitoring environnemental utilisant des Arduino MKR1010 avec shields MKR ENV. Le projet est conforme au standard **UCUM (Unified Code for Units of Measure)** pour garantir l'interopérabilité et la standardisation des unités de mesure.

**Auteur:** Dominique Dessy  
**Version:** 1.0  
**Date:** Août 2025

## 🎯 Objectifs

- **Monitoring multi-sites** : Surveillance de température, humidité, pression et luminosité
- **Standard UCUM** : Conformité aux standards internationaux pour les unités
- **Scalabilité** : Support de multiples Arduino et sources de données
- **Alerting** : Détection d'anomalies et notifications automatiques
- **Historisation** : Stockage et analyse des tendances temporelles

## 🏗️ Architecture

```text
Arduino MKR1010 + ENV Shield
         ↓ WiFi + MQTT (codes UCUM)
    MQTT Broker (Mosquitto)
         ↓ Parsing & enrichissement
    Telegraf (processeur UCUM)
         ↓ Stockage time-series
    InfluxDB v2 (tags UCUM)
         ↓ Visualisation
    Grafana (dashboards UCUM)
```

## 📁 Structure du projet

```text
iot-sensors-ucum/
├── arduino/                          # → Lien vers ~/Documents/Arduino/iot-sensors-ucum/
│   ├── iot-sensors-ucum.ino         # Code principal Arduino
│   ├── config.h                      # Configuration avec codes UCUM
│   └── arduino_secrets.h.template   # Template pour paramètres WiFi/MQTT
├── docker/
│   └── docker-compose.yml           # Orchestration des services
├── telegraf/
│   └── telegraf.conf                # Configuration collecteur MQTT→InfluxDB
├── mosquitto/
│   └── config/
│       └── mosquitto.conf           # Configuration broker MQTT
├── grafana/
│   ├── provisioning/                # Configuration automatique
│   └── dashboards/                  # Dashboards pré-configurés
├── validation/
│   └── ucum_validator.py            # Script validation codes UCUM
├── scripts/
│   └── deploy.sh                    # Script de déploiement automatique
└── docs/
    └── README.md                    # Documentation détaillée
```

## 🚀 Démarrage rapide

### 1. Prérequis

- **Hardware** : Arduino MKR1010 + MKR ENV Shield
- **Software** : Docker, Docker Compose, Arduino IDE
- **Réseau** : WiFi disponible, ports 1883, 3000, 8086 libres

### 2. Installation

```bash
# Clonage du projet
cd /Users/dominique/Documents/Programmation
git clone <votre-repo> iot-sensors-ucum
cd iot-sensors-ucum

# Déploiement automatique
./scripts/deploy.sh
```

### 3. Configuration Arduino

```bash
# Navigation vers le code Arduino
cd ~/Documents/Arduino/iot-sensors-ucum

# Copie et édition des secrets
cp arduino_secrets.h.template arduino_secrets.h
# Éditer arduino_secrets.h avec vos paramètres WiFi
```

**Paramètres à configurer dans `arduino_secrets.h` :**
```cpp
#define SECRET_SSID "VotreSSID"
#define SECRET_PASS "VotreMotDePasse"
#define SECRET_MQTT_USER "mqtt_user"
#define SECRET_MQTT_PASS "mqtt_password"
```

### 4. Upload vers Arduino

1. Ouvrir Arduino IDE
2. Charger le projet depuis `~/Documents/Arduino/iot-sensors-ucum/`
3. Installer les bibliothèques requises :
   - WiFiNINA
   - ArduinoMqttClient
   - Arduino_MKRENV
   - ArduinoECCX08
   - ArduinoJson
4. Sélectionner la carte Arduino MKR WiFi 1010
5. Compiler et uploader

## 📊 Services et interfaces

Une fois déployé, les services sont accessibles :

| Service | URL | Identifiants | Description |
|---------|-----|--------------|-------------|
| **Grafana** | http://localhost:3000 | admin/admin123 | Dashboards et alerting |
| **InfluxDB** | http://localhost:8086 | admin/password123 | Base de données time-series |
| **MQTT Broker** | localhost:1883 | mqtt_user/mqtt_password | Messagerie IoT |

## 🏷️ Standard UCUM

Le projet utilise les codes UCUM officiels :

| Mesure | Code UCUM | Symbole | Type de quantité |
|--------|-----------|---------|------------------|
| Température | `Cel` | °C | thermodynamic-temperature |
| Humidité | `%` | % | dimensionless-ratio |
| Pression | `hPa` | hPa | pressure |
| Luminosité | `lx` | lx | illuminance |

### Avantages UCUM

- **Standardisation internationale** : IEEE, HL7, ISO 11240:2012
- **Interopérabilité** : Compatible systèmes médicaux/industriels
- **Conversion automatique** : Vers unités SI intégrée
- **Validation** : Codes vérifiés automatiquement

## 📡 Format des données MQTT

### Message de mesure
```json
{
  "device_id": "mkr1010_abc12345",
  "sensor_type": "temperature",
  "value": 23.5,
  "timestamp": 1692123456,
  "location": "bureau_paris",
  "measurement_type": "sensor_reading",
  "ucum": {
    "code": "Cel",
    "display": "°C",
    "common_name": "Temperature",
    "quantity_type": "thermodynamic-temperature"
  },
  "validation": {
    "min_value": -40.0,
    "max_value": 85.0,
    "in_range": true
  }
}
```

### Message keepalive
```json
{
  "device_id": "mkr1010_abc12345",
  "message_type": "keepalive",
  "timestamp": 1692123456,
  "location": "bureau_paris",
  "uptime": 3600000,
  "wifi_rssi": -65,
  "sensors": {
    "temperature": {"value": 23.5, "ucum_code": "Cel", "ucum_display": "°C"},
    "humidity": {"value": 45.2, "ucum_code": "%", "ucum_display": "%"},
    "pressure": {"value": 1013.2, "ucum_code": "hPa", "ucum_display": "hPa"},
    "illuminance": {"value": 350.0, "ucum_code": "lx", "ucum_display": "lx"}
  }
}
```

## 🔧 Configuration avancée

### Ajout d'un nouvel Arduino

1. **Configuration réseau** : Même SSID/mot de passe WiFi
2. **ID unique** : Généré automatiquement via puce crypto ECCX08
3. **Location** : Modifier `SECRET_DEVICE_LOCATION` dans `arduino_secrets.h`
4. **Topics MQTT** : Automatiquement `sensors/{device_id}/{sensor_type}`

### Personnalisation des seuils

Dans `config.h`, modifier les structures `SensorConfigUCUM` :

```cpp
{
  "temperature",
  "Cel", "°C", "Temperature",
  0.2,        // Seuil de changement (0.2°C au lieu de 0.5°C)
  -20.0, 60.0, // Nouvelle plage de valeurs
  "thermodynamic-temperature"
}
```

### Extension avec nouveaux capteurs

Pour ajouter un capteur de CO2 par exemple :

```cpp
// Dans config.h
{
  "co2",
  "[ppm]",     // Code UCUM pour parts per million
  "ppm",       // Affichage
  "CO2 Concentration",
  50.0,        // Seuil 50ppm
  300.0, 5000.0, // Plage CO2
  "dimensionless" // Type de quantité
}
```

## 📈 Dashboards Grafana

### Dashboard principal : IoT Sensors - Conforme UCUM

- **Température (UCUM: Cel)** : Graphique temporel avec codes UCUM
- **Humidité (UCUM: %)** : Suivi pourcentage humidité relative
- **Pression (UCUM: hPa)** : Évolution pression atmosphérique
- **Illuminance (UCUM: lx)** : Mesures de luminosité
- **Table UCUM** : Codes actifs et dernières valeurs

### Variables de template

- `device` : Filtrage par Arduino
- `ucum_quantity` : Filtrage par type de quantité physique

### Exemples de requêtes Flux

```flux
// Température avec conversion SI automatique
from(bucket: "sensor-data")
  |> range(start: v.timeRangeStart)
  |> filter(fn: (r) => r["ucum.code"] == "Cel")
  |> map(fn: (r) => ({
      r with
      value_kelvin: r._value + 273.15,
      display_name: r.device_id + " (" + r["ucum.display"] + ")"
    }))

// Agrégation par type de quantité UCUM
from(bucket: "sensor-data")
  |> range(start: -24h)
  |> filter(fn: (r) => r["ucum.quantity_type"] == "thermodynamic-temperature")
  |> aggregateWindow(every: 1h, fn: mean)
```

## ⚠️ Alerting et monitoring

### Règles d'alerte configurées

1. **Température critique** : < -10°C ou > 35°C
2. **Humidité anormale** : < 10% ou > 90%
3. **Device offline** : Pas de keepalive depuis 10 minutes
4. **Valeurs hors plage** : Selon validation UCUM

### Channels de notification

- **Email** : Configurable dans Grafana
- **Slack** : Webhook pour notifications équipe
- **SNMP** : Intégration systèmes de supervision

## 🧪 Tests et validation

### Validation des codes UCUM

```bash
# Exécution du validateur
cd validation
python3 ucum_validator.py

# Sortie attendue
=== Validation UCUM du projet IoT ===
✓ Code UCUM valide: Cel (degree Celsius)
✓ Code UCUM valide: % (percent)
✓ Code UCUM valide: hPa (hectopascal)
✓ Code UCUM valide: lx (lux)
✅ Tous les codes UCUM sont conformes au standard!
```

### Tests de connectivité

```bash
# Test MQTT
mosquitto_pub -h localhost -p 1883 -u mqtt_user -P mqtt_password \
  -t "test/topic" -m "Hello MQTT"

# Test InfluxDB
curl -X GET "http://localhost:8086/health"

# Test Grafana
curl -X GET "http://localhost:3000/api/health"
```

## 📚 Documentation technique

### Standards respectés

- **UCUM** : Unified Code for Units of Measure
- **IEEE** : Standards électroniques et communication
- **ISO 11240:2012** : Health informatics - Identification of medicinal products
- **MQTT 3.1.1** : Message Queuing Telemetry Transport
- **JSON** : JavaScript Object Notation pour échange de données

### Références

- [UCUM Official Site](https://ucum.org/)
- [UCUM Specification](https://ucum.org/ucum)
- [Arduino MKR1010 Documentation](https://docs.arduino.cc/hardware/mkr-wifi-1010)
- [MKR ENV Shield](https://docs.arduino.cc/hardware/mkr-env-shield)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Grafana Documentation](https://grafana.com/docs/)

## 🔒 Sécurité

### Bonnes pratiques implémentées

- **Authentification MQTT** : Utilisateur/mot de passe requis
- **Secrets séparés** : Fichier `arduino_secrets.h` exclu de Git
- **Tokens InfluxDB** : Authentication token pour API
- **Réseau isolé** : Docker network dédié
- **Logs de sécurité** : Connexions/déconnexions tracées

### Recommandations production

- **TLS/SSL** : Chiffrement MQTT et HTTPS
- **Certificats** : PKI pour authentification devices
- **Firewall** : Restriction accès ports
- **VPN** : Accès sécurisé aux dashboards
- **Backup** : Sauvegarde régulière des données

## 🚨 Troubleshooting

### Problèmes fréquents

**Arduino ne se connecte pas au WiFi**
```cpp
// Vérifier dans arduino_secrets.h
#define SECRET_SSID "VotreSSID"     // Correct ?
#define SECRET_PASS "VotrePassword" // Correct ?
```

**Pas de données dans Grafana**
```bash
# Vérifier les services Docker
docker-compose ps

# Vérifier les logs Telegraf
docker-compose logs telegraf

# Vérifier les messages MQTT
mosquitto_sub -h localhost -p 1883 -u mqtt_user -P mqtt_password -t "sensors/+/+"
```

**Codes UCUM non reconnus**
```bash
# Validation des codes
python3 validation/ucum_validator.py
```

### Logs utiles

```bash
# Logs de tous les services
docker-compose logs -f

# Logs spécifiques
docker-compose logs -f telegraf
docker-compose logs -f mosquitto
docker-compose logs -f influxdb
docker-compose logs -f grafana
```

## 🛠️ Maintenance

### Tâches régulières

- **Backup InfluxDB** : Export des données importantes
- **Mise à jour** : Images Docker et bibliothèques Arduino
- **Monitoring** : Surveillance espace disque et performances
- **Nettoyage** : Rotation des logs et données anciennes

### Scripts de maintenance

```bash
# Backup des données
docker-compose exec influxdb influx backup /tmp/backup
docker cp iot-influxdb:/tmp/backup ./backup-$(date +%Y%m%d)

# Mise à jour des images
docker-compose pull
docker-compose up -d

# Nettoyage des volumes orphelins
docker volume prune
```

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📞 Support

Pour toute question ou problème :

- **Email** : dominique.dessy@exemple.com
- **Issues** : GitHub Issues du projet
- **Documentation** : Consulter le dossier `docs/`

---

**Développé avec ❤️ par Dominique Dessy**  
*Système IoT conforme aux standards internationaux UCUM*
