#!/bin/bash

# Script de déploiement du projet IoT Sensors UCUM
# Auteur: Dominique Dessy
# Version: 1.0

set -e  # Arrêt en cas d'erreur

echo "=== Déploiement du projet IoT Sensors UCUM ==="
echo "Auteur: Dominique Dessy"
echo "Version: 1.0"
echo ""

# Vérification des prérequis
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé"
    exit 1
fi

echo "✅ Prérequis Docker validés"

# Création des répertoires nécessaires
echo "📁 Création des répertoires de données..."
mkdir -p mosquitto/{data,log}
mkdir -p influxdb/config

# Configuration des permissions
echo "🔐 Configuration des permissions..."
sudo chown -R 1883:1883 mosquitto/data mosquitto/log 2>/dev/null || echo "⚠️  Permissions mosquitto à ajuster manuellement"

# Génération du fichier de mots de passe MQTT
echo "🔑 Configuration de l'authentification MQTT..."
if [ ! -f mosquitto/config/passwd ]; then
    echo "Création du fichier de mots de passe MQTT..."
    docker run --rm -v $(pwd)/mosquitto/config:/config eclipse-mosquitto:2.0 \
        mosquitto_passwd -b /config/passwd mqtt_user mqtt_password
    echo "✅ Utilisateur MQTT créé: mqtt_user/mqtt_password"
else
    echo "✅ Fichier de mots de passe MQTT déjà existant"
fi

# Vérification du lien symbolique Arduino
if [ -L "arduino" ]; then
    echo "✅ Lien symbolique Arduino configuré"
else
    echo "⚠️  Lien symbolique Arduino manquant - voir README.md"
fi

# Démarrage des services
echo "🚀 Démarrage des services..."
docker-compose up -d

# Attente du démarrage
echo "⏳ Attente du démarrage des services..."
sleep 15

# Vérification du statut
echo "📊 Vérification du statut des services..."
docker-compose ps

echo ""
echo "=== Déploiement terminé! ==="
echo ""
echo "🌐 Services disponibles:"
echo "  - Grafana:  http://localhost:3000 (admin/admin123)"
echo "  - InfluxDB: http://localhost:8086 (admin/password123)"
echo "  - MQTT:     localhost:1883 (mqtt_user/mqtt_password)"
echo ""
echo "📖 Consultez le README.md pour les instructions d'utilisation"
echo "🔧 Configuration Arduino dans: ~/Documents/Arduino/iot-sensors-ucum/"
