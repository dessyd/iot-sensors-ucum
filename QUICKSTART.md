# 🚀 Guide de démarrage rapide - IoT Sensors UCUM

## ⚡ Installation en 5 minutes

### 1. Prérequis
```bash
# Vérifier Docker
docker --version
docker-compose --version
```

### 2. Configuration Arduino
```bash
cd ~/Documents/Arduino/iot-sensors-ucum
cp arduino_secrets.h.template arduino_secrets.h

# Éditer avec vos paramètres WiFi
nano arduino_secrets.h
```

### 3. Déploiement
```bash
cd /Users/dominique/Documents/Programmation/iot-sensors-ucum
./scripts/deploy.sh
```

### 4. Upload Arduino
- Ouvrir Arduino IDE
- Charger le projet depuis `~/Documents/Arduino/iot-sensors-ucum/`
- Installer les bibliothèques : WiFiNINA, ArduinoMqttClient, Arduino_MKRENV, ArduinoECCX08, ArduinoJson
- Sélectionner Arduino MKR WiFi 1010
- Upload

### 5. Vérification
```bash
# Test de validation complète
./scripts/validate.sh

# Accès aux services
open http://localhost:3000  # Grafana (admin/admin123)
open http://localhost:8086  # InfluxDB (admin/password123)
```

## 📊 Premiers pas avec Grafana

1. **Connexion** : http://localhost:3000 (admin/admin123)
2. **Dashboard** : "IoT Sensors - Conforme UCUM"
3. **Variables** : Filtrer par device ou type de quantité UCUM
4. **Alertes** : Configurées automatiquement

## 🔧 Configuration WiFi Arduino

Dans `arduino_secrets.h` :
```cpp
#define SECRET_SSID "VotreReseau"
#define SECRET_PASS "VotreMotDePasse"
#define SECRET_MQTT_USER "mqtt_user"
#define SECRET_MQTT_PASS "mqtt_password"
```

## 📡 Vérification des données

### Messages MQTT
```bash
# Écouter les messages
mosquitto_sub -h localhost -p 1883 -u mqtt_user -P mqtt_password -t "sensors/+/+"
```

### Données InfluxDB
```bash
# Via interface web
open http://localhost:8086
# Organisation: iot-sensors
# Bucket: sensor-data
```

## 🏷️ Codes UCUM utilisés

| Capteur | Code UCUM | Affichage |
|---------|-----------|-----------|
| Température | `Cel` | °C |
| Humidité | `%` | % |
| Pression | `hPa` | hPa |
| Luminosité | `lx` | lx |

## 🆘 Résolution problèmes

### Arduino ne se connecte pas
```bash
# Vérifier les paramètres WiFi
grep SECRET_SSID ~/Documents/Arduino/iot-sensors-ucum/arduino_secrets.h
```

### Pas de données dans Grafana
```bash
# Vérifier les services
docker-compose ps

# Logs Telegraf
docker-compose logs telegraf
```

### Validation échoue
```bash
# Diagnostic complet
./scripts/validate.sh
```

## 📞 Support

- **Documentation** : README.md complet
- **Technique** : docs/TECHNICAL.md
- **Issues** : GitHub du projet
- **Validation** : ./scripts/validate.sh

---
**Projet IoT Sensors UCUM v1.0 - Dominique Dessy**
