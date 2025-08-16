# Guide de déploiement - IoT Sensors UCUM

## 🎯 Vue d'ensemble

Ce guide détaille le processus complet de déploiement du système IoT Sensors UCUM, de l'installation initiale à la mise en production.

## 📋 Prérequis système

### Matériel requis

- **Arduino MKR WiFi 1010** avec shield MKR ENV
- **Ordinateur hôte** : macOS, Linux ou Windows avec Docker
- **Réseau WiFi** 2.4GHz ou 5GHz avec accès Internet
- **Thermomètre de référence** pour calibration (recommandé)

### Logiciels requis

- **Docker** >= 20.10.0
- **Docker Compose** >= 2.0.0  
- **Arduino IDE** >= 2.0.0
- **Git** pour le clonage du repository

### Bibliothèques Arduino

```text
WiFiNINA >= 1.8.13
ArduinoMqttClient >= 0.1.5
Arduino_MKRENV >= 1.2.1
ArduinoECCX08 >= 1.3.7
ArduinoJson >= 6.19.4
```

## 🚀 Installation initiale

### 1. Clonage du projet

```bash
git clone <repository-url> iot-sensors-ucum
cd iot-sensors-ucum
```

### 2. Vérification des prérequis

```bash
# Vérifier Docker
docker --version
docker-compose --version

# Vérifier l'espace disque (minimum 2GB)
df -h .

# Tester la connectivité réseau
ping google.com
```

### 3. Configuration de l'environnement

```bash
# Copier le template d'environnement
cp .env.example .env

# Éditer les credentials
nano .env
```

## ⚙️ Configuration pré-déploiement

### 1. Configuration des credentials

```bash
# Copier le template d'environnement
cp .env.example .env

# Éditer les credentials
nano .env
```

**Variables importantes dans .env :**

```bash
# MQTT
MQTT_USERNAME=mqtt_user
MQTT_PASSWORD=changez_moi_securise

# InfluxDB
INFLUX_USERNAME=admin
INFLUX_PASSWORD=changez_moi_admin
INFLUX_ORG=iot-sensors
INFLUX_BUCKET=sensor-data

# Grafana  
GRAFANA_USERNAME=admin
GRAFANA_PASSWORD=changez_moi_grafana
```

### 2. Configuration Arduino

```bash
# Aller dans le dossier Arduino (lien symbolique ou copie)
cd ~/Documents/Arduino/iot-sensors-ucum

# Copier le template de secrets
cp arduino_secrets.h.template arduino_secrets.h

# Éditer les paramètres WiFi et MQTT
nano arduino_secrets.h
```

**Contenu arduino_secrets.h :**

```cpp
#define SECRET_SSID "VotreReseauWiFi"
#define SECRET_PASS "VotreMotDePasseWiFi"
#define SECRET_MQTT_USER "mqtt_user"
#define SECRET_MQTT_PASS "changez_moi_securise"
```

### 3. Configuration des profils (optionnel)

```bash
# Éditer la configuration Arduino pour profil de fréquence
nano iot-sensors-ucum/config.h

# Exemples de profils :
# #define MEASUREMENT_FREQUENCY HIGH    # Temps réel
# #define MEASUREMENT_FREQUENCY MEDIUM  # Équilibré (défaut)
# #define MEASUREMENT_FREQUENCY LOW     # Économe
```

## 🐳 Déploiement des services Docker

### 1. Déploiement complet

```bash
# Lancer tous les services
docker-compose up -d

# Vérifier le démarrage
docker-compose logs --tail=50
```

### 2. Vérification des services

```bash
# État des conteneurs
docker-compose ps

# Logs de démarrage
docker-compose logs --tail=50

# Santé des services
./scripts/check-services.sh
```

**Services attendus :**

```text
NAME                STATE
mosquitto          Up (healthy)
influxdb           Up (healthy)  
telegraf           Up
grafana            Up (healthy)
```

### 3. Configuration initiale InfluxDB

```bash
# Les services se configurent automatiquement via compose.yml
# Vérifier que InfluxDB est opérationnel
curl http://localhost:8086/health

# Accéder à l'interface web (optionnel)
open http://localhost:8086
# Credentials: admin / password123
```

### 4. Accès aux dashboards Grafana

```bash
# Les dashboards sont automatiquement provisionnés via compose.yml
# Accéder à l'interface web
open http://localhost:3000
# Credentials: admin / admin123
```

## 📱 Configuration et upload Arduino

### 1. Préparation de l'Arduino IDE

```bash
# Installer les bibliothèques via Library Manager
# Ou script automatique
./scripts/install-arduino-libs.sh
```

### 2. Configuration de la carte

- **Outil → Type de carte** : Arduino MKR WiFi 1010
- **Outil → Port** : Sélectionner le port USB approprié
- **Outil → Programmateur** : Arduino as ISP

### 3. Compilation et upload

```bash
# Via Arduino IDE : Sketch → Vérifier/Compiler
# Puis : Sketch → Téléverser

# Ou via ligne de commande (si arduino-cli installé)
arduino-cli compile --fqbn arduino:samd:mkrwifi1010 iot-sensors-ucum/
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:samd:mkrwifi1010 iot-sensors-ucum/
```

### 4. Vérification du fonctionnement

```bash
# Moniteur série Arduino IDE : 9600 bauds
# Vérifier les logs de connexion WiFi et MQTT
```

**Logs attendus :**

```text
=== Arduino IoT Sensors - Standard UCUM ===
Version: 1.8 (Frequency Profiles)
=== Configuration fréquence ===
Fréquence: MEDIUM (équilibré)
Mesure: 30s
Keepalive: 300s (10x mesure)
=== Connexion WiFi ===
Connecté! IP: 192.168.1.218
=== Connexion MQTT ===
Connecté au broker MQTT
```

## ✅ Validation du déploiement

### 1. Tests automatiques

```bash
# Validation complète du système
./scripts/validate.sh

# Tests spécifiques
./scripts/test-mqtt.sh
./scripts/test-influxdb.sh  
./scripts/test-grafana.sh
```

### 2. Vérification manuelle des services

#### Test MQTT

```bash
# Écouter les messages en temps réel
mosquitto_sub -h localhost -p 1883 \
  -u mqtt_user -P changez_moi_securise \
  -t "sensors/+/+" -v

# Publier un message de test
mosquitto_pub -h localhost -p 1883 \
  -u mqtt_user -P changez_moi_securise \
  -t "test/topic" -m "hello world"
```

#### Test InfluxDB

```bash
# Interface web
open http://localhost:8086

# API de santé
curl http://localhost:8086/health

# Requête de test
curl -H "Authorization: Token $INFLUX_TOKEN" \
  "http://localhost:8086/api/v2/query" \
  --data-urlencode 'q=buckets()'
```

#### Test Grafana

```bash
# Interface web
open http://localhost:3000

# Login : admin / changez_moi_grafana
# Vérifier le dashboard "IoT Sensors - Conforme UCUM"
```

### 3. Vérification des données

#### Réception des données Arduino

```bash
# Logs Telegraf pour voir les données reçues
docker-compose logs -f telegraf | grep "sensors/"

# Vérification dans InfluxDB via interface web
# Data Explorer → Bucket: sensor-data → Measurement: sensor_readings
```

#### Dashboard fonctionnel  

- **Variables** : Device ID sélectionnable
- **Panneaux** : Séries temporelles pour chaque type UCUM
- **Données** : Mise à jour temps réel selon profil de fréquence

## 🔧 Optimisation post-déploiement

### 1. Calibration des capteurs

```bash
# Comparer avec instruments de référence
# Éditer les offsets dans config.h si nécessaire
nano iot-sensors-ucum/config.h

# Exemples :
# #define TEMPERATURE_OFFSET 2.5  # Si +2.5°C d'erreur
# #define HUMIDITY_OFFSET -1.2    # Si -1.2% d'erreur
```

### 2. Ajustement des profils de fréquence

```bash
# Selon les besoins opérationnels
# HIGH : Monitoring critique (10s)
# MEDIUM : Standard (30s) - recommandé
# LOW : Économie d'énergie (60s)
```

### 3. Configuration des alertes Grafana

```bash
# Via interface Grafana : Alerting → Alert Rules
# Configurer seuils selon environnement :
# - Température : < 5°C ou > 35°C
# - Humidité : < 20% ou > 80%
# - Pression : < 980hPa ou > 1050hPa
```

## 📊 Monitoring de production

### 1. Surveillance continue

```bash
# Script de monitoring automatique
./scripts/monitor.sh

# Logs centralisés
docker-compose logs -f --tail=100

# Métriques système
docker stats
```

### 2. Maintenance périodique

```bash
# Nettoyage des logs (hebdomadaire)
./scripts/cleanup-logs.sh

# Backup des données (quotidien)  
./scripts/backup.sh

# Mise à jour des services (mensuel)
./scripts/update.sh
```

### 3. Alertes opérationnelles

- **Device offline** : Pas de données depuis > 2 × keepalive_interval
- **Valeurs aberrantes** : Capteurs hors plages normales
- **Services down** : Conteneurs Docker non opérationnels
- **Espace disque** : < 10% disponible
- **Mémoire** : > 80% utilisée

## 🚨 Troubleshooting déploiement

### Problèmes Docker fréquents

#### Services ne démarrent pas

```bash
# Vérifier les logs d'erreur
docker-compose logs [service-name]

# Reconstruire les images
docker-compose build --no-cache

# Nettoyer et redémarrer
docker-compose down -v
docker-compose up -d
```

#### Problèmes de ports

```bash
# Vérifier les ports utilisés
sudo netstat -tulpn | grep :1883
sudo netstat -tulpn | grep :8086
sudo netstat -tulpn | grep :3000

# Modifier les ports dans .env si conflit
MQTT_PORT=1884
INFLUX_PORT=8087
GRAFANA_PORT=3001
```

#### Problèmes de permissions

```bash
# Fixer les permissions des volumes
sudo chown -R $USER:$USER ./data
sudo chmod -R 755 ./logs

# Recréer les volumes si nécessaire
docker-compose down -v
docker volume prune
docker-compose up -d
```

### Problèmes Arduino fréquents

#### Compilation échoue

```bash
# Vérifier les bibliothèques installées
arduino-cli lib list

# Réinstaller les bibliothèques manquantes
arduino-cli lib install "WiFiNINA@1.8.13"
arduino-cli lib install "ArduinoMqttClient@0.1.5"
arduino-cli lib install "Arduino_MKRENV@1.2.1"
arduino-cli lib install "ArduinoECCX08@1.3.7"
arduino-cli lib install "ArduinoJson@6.19.4"
```

#### Arduino ne se connecte pas au WiFi

```bash
# Vérifier arduino_secrets.h
grep SECRET_SSID ~/Documents/Arduino/iot-sensors-ucum/arduino_secrets.h

# Tester avec un SSID simple (pas de caractères spéciaux)
# Vérifier que le réseau est en 2.4GHz
# Redémarrer le routeur si nécessaire
```

#### Connexion MQTT échoue

```bash
# Vérifier les credentials MQTT dans arduino_secrets.h
# Tester la connexion depuis l'ordinateur :
mosquitto_pub -h localhost -p 1883 -u mqtt_user -P password -t "test" -m "test"

# Vérifier les logs Mosquitto
docker-compose logs mosquitto
```

### Problèmes de données

#### Pas de données dans InfluxDB

```bash
# Vérifier la réception MQTT
mosquitto_sub -h localhost -p 1883 -u mqtt_user -P password -t "sensors/+/+" -v

# Vérifier les logs Telegraf
docker-compose logs telegraf | grep ERROR

# Tester l'écriture manuelle InfluxDB
curl -X POST "http://localhost:8086/api/v2/write?org=iot-sensors&bucket=sensor-data" \
  -H "Authorization: Token $INFLUX_TOKEN" \
  -H "Content-Type: text/plain; charset=utf-8" \
  --data-raw 'test,device=manual value=42'
```

#### Grafana n'affiche pas les données

```bash
# Vérifier la connexion InfluxDB dans Grafana
# Configuration → Data Sources → InfluxDB
# Test & Save doit être vert

# Vérifier les requêtes dans Data Explorer
from(bucket: "sensor-data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_readings")
```

## 🔄 Mise à jour du système

### Mise à jour mineure (patch)

```bash
# Sauvegarder les données
./scripts/backup.sh

# Mettre à jour le code
git pull origin main

# Redémarrer les services
docker-compose restart

# Valider le fonctionnement
./scripts/validate.sh
```

### Mise à jour majeure (version)

```bash
# Sauvegarder complètement
./scripts/full-backup.sh

# Arrêter les services
docker-compose down

# Mettre à jour le code
git fetch --tags
git checkout v1.9.0  # exemple

# Migrer la configuration si nécessaire
./scripts/migrate-config.sh

# Reconstruire et redémarrer
docker-compose build
docker-compose up -d

# Validation complète
./scripts/validate.sh
```

### Mise à jour firmware Arduino

```bash
# Télécharger la nouvelle version
cd ~/Documents/Arduino/iot-sensors-ucum
git pull origin main

# Vérifier la configuration
nano config.h

# Compiler et uploader via Arduino IDE
# Vérifier les logs de démarrage
```

## 📋 Checklist de déploiement

### Pré-déploiement

- [ ] Prérequis système vérifiés
- [ ] Credentials configurés dans .env
- [ ] Credentials Arduino configurés
- [ ] Profil de fréquence sélectionné
- [ ] Réseau WiFi accessible depuis Arduino

### Déploiement

- [ ] Services Docker démarrés sans erreur
- [ ] InfluxDB initialisé et accessible
- [ ] Grafana accessible avec dashboards
- [ ] Mosquitto accepte les connexions
- [ ] Arduino compilé et uploadé
- [ ] Arduino connecté WiFi et MQTT

### Post-déploiement

- [ ] Messages MQTT reçus dans broker
- [ ] Données visibles dans InfluxDB
- [ ] Dashboards Grafana mis à jour
- [ ] Alertes configurées et testées
- [ ] Calibration des capteurs effectuée
- [ ] Documentation mise à jour

### Production

- [ ] Monitoring automatique activé
- [ ] Backup planifiés configurés
- [ ] Alertes opérationnelles testées
- [ ] Procédures de maintenance documentées
- [ ] Support et escalation définis

## 🎯 Déploiement multi-environnements

### Environnement de développement

```bash
# Profil haute fréquence pour tests rapides
MEASUREMENT_FREQUENCY=HIGH

# Rétention courte des données
INFLUX_RETENTION=24h

# Logs verbeux activés
DEBUG_SERIAL=true
```

### Environnement de test

```bash
# Profil équilibré
MEASUREMENT_FREQUENCY=MEDIUM

# Simulation de production
INFLUX_RETENTION=168h  # 7 jours

# Tests automatisés
./scripts/run-integration-tests.sh
```

### Environnement de production

```bash
# Profil selon besoins métier
MEASUREMENT_FREQUENCY=MEDIUM  # ou LOW pour économie

# Rétention complète
INFLUX_RETENTION=720h  # 30 jours

# Monitoring renforcé
./scripts/setup-production-monitoring.sh
```

## 📊 Métriques de déploiement

### Indicateurs de succès

- **Uptime Arduino** : > 99%
- **Latence MQTT** : < 1 seconde
- **Perte de messages** : < 0.1%
- **Disponibilité services** : > 99.9%
- **Temps de récupération** : < 5 minutes

### Monitoring de performance

```bash
# Script de métriques automatique
./scripts/collect-metrics.sh

# Dashboard dédié "IoT Infrastructure"
# Panneaux :
# - Taux de messages MQTT
# - Latence InfluxDB
# - Utilisation CPU/RAM
# - Espace disque
# - Disponibilité réseau
```

---

**Guide de déploiement v1.8** - *Installation et mise en production du système IoT Sensors UCUM*  
Dernière mise à jour : Août 2025
