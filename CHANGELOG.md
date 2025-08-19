# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2025-08-19

### Ajouté
- **Guide Telegraf complet** : Documentation détaillée dans `docs/TELEGRAF_CONFIGURATION.md`
- **Processors expliqués** : Guide étape par étape des transformations de données
- **Monitoring Telegraf** : Métriques internes et debug avancé
- **Requêtes Flux optimisées** : Exemples pour InfluxDB v2
- **Variables d'environnement** : Configuration Telegraf externalisée
- **Support Feinstaub** : Documentation de l'intégration capteurs particules

### Modifié
- **README v2.2** : Mise à jour avec nouvelle documentation Telegraf
- **Section Documentation** : Ajout du guide Telegraf dans la liste
- **Nouveautés v2.2** : Focus sur documentation et maintenance
- **Version badges** : Mise à jour vers v2.2.0

### Documentation
- **Architecture des données** : Schéma complet Arduino → Feinstaub → Telegraf → InfluxDB
- **Configuration détaillée** : Tous les paramètres Telegraf expliqués
- **Troubleshooting avancé** : Solutions aux problèmes Telegraf courants
- **Bonnes pratiques** : Configuration, performance et sécurité
- **Exemples concrets** : Formats de données et transformations

### Technique
- **Standards rédaction** : Blocs de code avec tags appropriés (conformément aux préférences)
- **Structure organisée** : Documentation claire dans répertoire `docs/`
- **Git workflow** : Versioning sémantique et commits structurés
- **Maintenance projet** : Documentation technique complète pour faciliter contributions

## [2.1.1] - 2025-08-18

### Sécurité
- **Variables d'environnement Grafana** : Déplacement des identifiants vers `.env`
- **Configuration sécurisée** : Suppression des credentials codés en dur de `compose.yml`
- **Protection fichier .env** : Ajout au `.gitignore` pour éviter commit accidentel
- **Documentation sécurisée** : Mise à jour README avec références `.env`

### Ajouté
- **Répertoire assets/** : Structure pour ressources visuelles du projet
- **Capture d'écran dashboard** : Exemple visuel Grafana v2.0 en action
- **Variables Grafana** : `GRAFANA_ADMIN_USER` et `GRAFANA_ADMIN_PASSWORD`
- **Documentation visuelle** : Section dashboard avec image dans README

### Modifié
- **compose.yml** : Utilisation variables `${GRAFANA_ADMIN_USER}` et `${GRAFANA_ADMIN_PASSWORD}`
- **.env.example** : Ajout variables Grafana pour documentation
- **README.md** : Références identifiants via `.env` au lieu de valeurs codées
- **Timezone** : Mise à jour Europe/Brussels dans `.env.example`

### Corrigé
- **Sécurité credentials** : Plus d'identifiants visibles dans le repository
- **Configuration flexible** : Adaptation facile selon environnement
- **Documentation cohérente** : Suppression doublons section dashboard

### Technique
- **Variables Docker Compose** : Support complet des variables d'environnement
- **Structure assets/** : Préparation pour futures ressources visuelles
- **Capture d'écran** : dashboard-v2.1-screenshot.png (692 KB)
- **Configuration centralisée** : Toutes variables sensibles dans `.env`

## [2.1.0] - 2025-08-18

### Ajouté
- **Format unifié v2.0** : Un seul format de message pour tous les capteurs
- **Protection débordement** : Variables `unsigned long` avec reset préventif à 1M cycles
- **Dashboard Grafana v2.0** : Interface moderne avec emojis et table récapitulative
- **Variable template Grafana** : Filtrage par device_id
- **Requêtes optimisées** : Utilisation de `sensor_type` au lieu de `ucum_code`

### Modifié
- **Logique Arduino** : Test unifié `(changement >= seuil) OR (compteur % KEEPALIVE_COUNT == 0)`
- **Compteur keepalive** : Utilisation de l'opérateur modulo au lieu de reset manuel
- **Configuration Telegraf** : Collecte seulement les mesures, ignore les status/LWT
- **Messages MQTT** : Format compact `{"v": value, "u": "unit", "t": "timestamp"}`
- **Type variables** : `measurementCounter` en `unsigned long` (32 bits)

### Supprimé
- **Formats multiples** : Plus de gestion de deux formats différents
- **Reset manuel compteur** : Remplacé par l'opérateur modulo
- **Messages LWT** : Ignorés par Telegraf pour éviter la pollution
- **Fonctions obsolètes** : `sendKeepalive()`, `sendKeepaliveCompact()`, `sendMeasurementUCUM()`

### Corrigé
- **Débordement compteur** : Protection avec variables 32 bits
- **Simplicité code** : Une seule logique de test au lieu de deux
- **Performance Telegraf** : Configuration optimisée sans processeurs inutiles
- **Structure InfluxDB** : Données propres avec fields `value`, `ucum_code`, `sensor_timestamp`

### Technique
- **Arduino v2.0** : Code unifié avec robustesse améliorée
- **Telegraf v2.1** : Topics spécifiques pour mesures seulement
- **Grafana v2.0** : Dashboard avec panels optimisés et refresh 10s
- **Capacité système** : 1,360 années avant débordement (vs 91h avant)

## [1.2.0] - 2025-08-17

### Corrigé
- **Erreurs Mosquitto** : Résolution complète des erreurs de configuration MQTT
- **Paramètres invalides** : Suppression de `keepalive_interval` et `message_size_limit` non supportés
- **Configuration MQTT** : Simplification vers une configuration minimale et fonctionnelle
- **Fichiers obsolètes** : Suppression du fichier `passwd` inutilisé

### Amélioré
- **Stabilité Mosquitto** : Configuration robuste sans erreurs
- **Performance** : Configuration optimisée pour l'usage IoT
- **Logs propres** : Plus d'erreurs dans les logs des services
- **Documentation** : Stack complètement opérationnelle

### Technique
- **Configuration MQTT** : Listeners 1883 (MQTT) et 9001 (WebSocket)
- **Authentification** : Mode anonyme pour serveur externe
- **Persistance** : Données sauvegardées dans volumes Docker
- **Limites** : 100 connexions, 20 messages en vol, 1000 en file

## [1.1.1] - 2025-08-17

### Corrigé
- **Erreurs Grafana** : Résolution des erreurs de provisioning et de dashboard
- **Répertoires manquants** : Ajout des répertoires `plugins/`, `notifiers/`, `alerting/` pour le provisioning
- **Structure dashboard** : Correction de la structure JSON avec tous les champs requis
- **UID dashboard** : Suppression de l'UID fixe pour génération automatique par Grafana
- **Références datasource** : Ajout des références correctes au datasource InfluxDB

### Ajouté
- **Fichiers .gitkeep** : Maintien de la structure des répertoires de provisioning dans Git
- **Dashboard optimisé** : Structure JSON complète compatible Grafana v10.2.0

## [1.1.0] - 2025-08-17

### Ajouté
- **Support serveur MQTT externe** : Configuration pour utiliser un broker MQTT externe (192.168.1.15)
- **Dashboard Grafana optimisé** : Interface utilisateur améliorée avec codes UCUM
- **Authentification unifiée** : Possibilité d'utiliser les mêmes identifiants entre services

### Modifié
- **Configuration Telegraf** : Simplifiée et optimisée pour le serveur MQTT externe
- **Format des données** : Adaptation au format Arduino réel `{v, u, t}`
- **Topics MQTT** : Support du pattern `sensors/{device_id}/{sensor_type}`
- **Processeurs Telegraf** : Suppression du processeur Starlark problématique, utilisation de processeurs natifs
- **Organisation InfluxDB** : Changement vers `iot-sensors` et bucket `sensor-data`

### Supprimé
- **Fichiers obsolètes** : Nettoyage des configurations Telegraf inutilisées
- **Scripts Starlark** : Suppression des fichiers de test et conversion non fonctionnels
- **Broker MQTT local** : Configuration pour utiliser un serveur externe

### Corrigé
- **Erreurs Telegraf** : Résolution des problèmes de configuration avec les processeurs
- **Authentification InfluxDB** : Correction des tokens et organisation
- **Structure JSON Grafana** : Correction du format de dashboard
- **Parsing MQTT** : Adaptation au format réel des données Arduino

### Sécurité
- **Fichiers secrets** : Ajout des fichiers `.env.influxdb*` au .gitignore
- **Isolation des identifiants** : Meilleure séparation des secrets Docker

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
