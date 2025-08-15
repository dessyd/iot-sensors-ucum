# IoT Sensors UCUM - Monitoring Environnemental Arduino

**Système de monitoring IoT utilisant Arduino MKR WiFi 1010 avec conformité aux standards UCUM (Unified Code for Units of Measure)**

[![Version](https://img.shields.io/badge/Version-1.8-blue.svg)](CHANGELOG.md)
[![Arduino](https://img.shields.io/badge/Arduino-MKR_WiFi_1010-green.svg)](https://www.arduino.cc/en/Guide/MKR1000)
[![UCUM](https://img.shields.io/badge/Standard-UCUM-orange.svg)](https://ucum.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Démarrage rapide

### Prérequis
- Arduino MKR WiFi 1010 + MKR ENV Shield
- Docker & Docker Compose
- Arduino IDE avec bibliothèques : WiFiNINA, ArduinoMqttClient, Arduino_MKRENV, ArduinoECCX08, ArduinoJson

### Installation en 5 minutes

1. **Configuration Arduino**
   ```bash
   cd ~/Documents/Arduino/iot-sensors-ucum
   cp arduino_secrets.h.template arduino_secrets.h
   # Éditer avec vos paramètres WiFi
   ```

2. **Déploiement des services**
   ```bash
   cd /Users/dominique/Documents/Programmation/iot-sensors-ucum
   ./install.sh
   docker-compose up -d
   ```

3. **Upload du firmware Arduino** via Arduino IDE

4. **Vérification**
   ```bash
   docker-compose ps
   open http://localhost:3000  # Grafana (admin/admin123)
   ```

## 📊 Fonctionnalités

### Capteurs supportés
- **Température** : Standard UCUM `Cel` (°C)
- **Humidité** : Standard UCUM `%` (% RH)
- **Pression** : Standard UCUM `hPa` (hectopascal)
- **Luminosité** : Standard UCUM `lx` (lux)

### Caractéristiques techniques
- **ID unique** basé sur puce crypto ECCX08
- **Transmission MQTT** avec métadonnées UCUM complètes
- **Détection de changement** intelligente avec seuils configurables
- **Calibration** des capteurs avec offsets personnalisables
- **Profils de fréquence** prédéfinis (HIGH/MEDIUM/LOW)
- **Surveillance connexion** avec keepalive configurable

### Stack technologique
- **Arduino** : Firmware avec support UCUM complet
- **MQTT** : Broker Mosquitto sécurisé
- **InfluxDB** : Base de données time-series
- **Telegraf** : Collecte et enrichissement des données
- **Grafana** : Dashboards et alerting temps réel
- **Docker** : Orchestration complète

## ⚙️ Configuration

### Profils de fréquence (v1.8)
```cpp
// Configuration ultra-simple dans config.h
#define MEASUREMENT_FREQUENCY HIGH    // Temps réel (10s)
#define MEASUREMENT_FREQUENCY MEDIUM  // Équilibré (30s) - défaut
#define MEASUREMENT_FREQUENCY LOW     // Économe (60s)
```

### Calibration des capteurs (v1.6)
```cpp
// Corrections dans config.h (valeurs à soustraire)
#define TEMPERATURE_OFFSET 2.5    // °C
#define HUMIDITY_OFFSET 0.0       // %RH  
#define PRESSURE_OFFSET 0.0       // hPa
#define ILLUMINANCE_OFFSET 0.0    // lx
```

### Messages MQTT compacts (v1.1)
```cpp
// Format optimisé pour réseaux contraints
#define USE_COMPACT_FORMAT true   // Messages 68% plus petits
#define USE_COMPACT_FORMAT false  // Format UCUM complet (défaut)
```

## 📡 Données et API

### Messages MQTT exemple
```json
{
  "device_id": "mkr1010_AA1D11EE",
  "sensor_type": "temperature", 
  "value": 23.5,
  "ucum": {"code": "Cel", "display": "°C"},
  "validation": {"in_range": true},
  "timestamp": "2025-08-13T15:06:05Z"
}
```

### Endpoints services
- **Grafana** : http://localhost:3000 (admin/admin123)
- **InfluxDB** : http://localhost:8086 (admin/password123)  
- **MQTT** : localhost:1883 (mqtt_user/mqtt_password)

## 🔧 Administration

### Surveillance système
```bash
# État des services
docker-compose ps

# Logs en temps réel
docker-compose logs -f telegraf

# Test des messages MQTT
mosquitto_sub -h localhost -p 1883 -u mqtt_user -P mqtt_password -t "sensors/+/+"
```

### Validation complète
```bash
# Vérifier les services Docker
docker-compose ps

# Test de connectivité MQTT
mosquitto_pub -h localhost -p 1883 -u mqtt_user -P mqtt_password -t "test" -m "hello"

# Vérification base de données
curl http://localhost:8086/health
```

## 📚 Documentation

- **[Guide technique](docs/TECHNICAL.md)** : Architecture et implémentation détaillées
- **[Configuration](docs/CONFIGURATION.md)** : Guide de configuration complète
- **[Déploiement](docs/DEPLOYMENT.md)** : Installation et mise en production
- **[Dépannage](docs/TROUBLESHOOTING.md)** : Solutions aux problèmes courants
- **[Historique](CHANGELOG.md)** : Versions et améliorations
- **[Archives versions](docs/versions/)** : Notes détaillées des versions

## 🏆 Standards et conformité

### Standards respectés
- **UCUM** : Unified Code for Units of Measure
- **IEEE** : Standards de communication électronique  
- **ISO 11240:2012** : Identification des unités
- **MQTT 3.1.1** : Protocole messaging IoT
- **JSON** : Format d'échange de données

### Validations
- **Codes UCUM** vérifiés selon spécifications officielles
- **Métadonnées** complètes pour interopérabilité
- **Validation temps réel** des plages de valeurs
- **Monitoring** de santé du système

## 🚨 Support et contribution

### Signaler un problème
1. Vérifier l'état des services : `docker-compose ps`
2. Consulter [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. Créer une issue avec les logs

### Développement
```bash
# Environnement de développement
git clone [repository]
cd iot-sensors-ucum
./install.sh

# Tests manuels
docker-compose up -d
docker-compose logs
```

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour détails complets.

---

**Projet IoT Sensors UCUM v1.8** - *Monitoring environnemental Arduino avec conformité UCUM*  
Développé par **Dominique Dessy** - Août 2025
