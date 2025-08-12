# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-12

### Ajouté
- **Arduino MKR1010 + MKR ENV Shield** : Support complet des capteurs environnementaux
- **Standard UCUM** : Conformité aux codes internationaux pour les unités de mesure
  - `Cel` pour degrés Celsius
  - `%` pour pourcentage d'humidité relative  
  - `hPa` pour hectopascal (pression)
  - `lx` pour lux (illuminance)
- **Architecture Docker** : Stack complète avec orchestration
  - InfluxDB v2 pour stockage time-series
  - Telegraf pour collecte et enrichissement MQTT
  - Mosquitto comme broker MQTT sécurisé
  - Grafana pour visualisation et alerting
- **Sécurité** : Authentification MQTT, tokens InfluxDB, isolation réseau
- **Monitoring** : Dashboards temps réel avec codes UCUM
- **Validation** : Script de vérification conformité UCUM
- **Documentation** : README complet, documentation technique
- **Scripts** : Déploiement automatique et validation
- **Git** : Structure projet avec .gitignore approprié

### Caractéristiques techniques
- **ID unique** : Basé sur puce crypto ECCX08 Arduino
- **Transmission** : MQTT avec métadonnées UCUM complètes
- **Détection changement** : Envoi intelligent selon seuils configurables
- **Keepalive** : Surveillance connexion avec timeout configurable
- **Conversion SI** : Automatique via processeurs Telegraf
- **Rétention** : 30 jours par défaut avec nettoyage auto
- **Alerting** : Règles Grafana pour valeurs critiques

### Structure
- Code Arduino dans `~/Documents/Arduino/iot-sensors-ucum/`
- Lien symbolique depuis projet principal
- Configuration Docker compose pour services
- Dashboards Grafana pré-configurés
- Scripts de déploiement et validation

### Standards respectés
- **UCUM** : Unified Code for Units of Measure
- **IEEE** : Standards de communication électronique
- **ISO 11240:2012** : Identification des unités
- **MQTT 3.1.1** : Protocole messaging IoT
- **JSON** : Format d'échange de données

### Compatibilité
- **OS** : macOS (testé), Linux, Windows (Docker)
- **Arduino** : MKR1010 avec shield MKR ENV
- **Réseau** : WiFi 2.4GHz/5GHz
- **Navigateurs** : Chrome, Firefox, Safari (Grafana)

---

## Template pour futures versions

### [X.Y.Z] - YYYY-MM-DD

### Ajouté
- Nouvelles fonctionnalités

### Modifié  
- Changements de fonctionnalités existantes

### Déprécié
- Fonctionnalités bientôt supprimées

### Supprimé
- Fonctionnalités supprimées

### Corrigé
- Corrections de bugs

### Sécurité
- Mises à jour de sécurité
