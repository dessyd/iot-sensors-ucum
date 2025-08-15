#!/bin/bash

# Installation de base sans MCP (Python 3.9 compatible)
set -e

PROJECT_DIR="/Users/dominique/Documents/Programmation/iot-sensors-ucum"
VENV_NAME="venv"

echo "🚀 Installation de base IoT Sensors UCUM (Python 3.9)"
echo "====================================================="

cd "$PROJECT_DIR"

# Vérifier Python
PYTHON_VERSION=$(python3 --version | cut -d" " -f2)
echo "✅ Python trouvé: $PYTHON_VERSION"

# Créer l'environnement virtuel
if [ ! -d "$VENV_NAME" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv $VENV_NAME
    echo "✅ Environnement virtuel créé"
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source $VENV_NAME/bin/activate

# Mettre à jour pip
echo "⬆️  Mise à jour de pip..."
pip install --upgrade pip

# Installer les dépendances compatibles Python 3.9
echo "📥 Installation des dépendances de base..."
pip install paho-mqtt python-dotenv pydantic

# Créer le fichier .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Fichier .env créé"
fi

echo ""
echo "✅ Installation de base terminée!"
echo ""
echo "⚠️  Note: MCP nécessite Python 3.10+"
echo "Pour l'installation complète:"
echo "1. Installer Python 3.10+: brew install python@3.11"
echo "2. Ou utiliser le client MQTT standalone"
echo ""
echo "Test du client MQTT:"
echo "python3 test_mqtt_basic.py"
