#!/bin/bash

# Script d'installation du serveur MCP IoT Sensors UCUM
set -e

PROJECT_DIR="/Users/dominique/Documents/Programmation/iot-sensors-ucum"
VENV_NAME="venv"

echo "🚀 Installation du serveur MCP IoT Sensors UCUM"
echo "================================================"

cd "$PROJECT_DIR"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d" " -f2)
echo "✅ Python trouvé: $PYTHON_VERSION"

# Créer l'environnement virtuel
if [ ! -d "$VENV_NAME" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv $VENV_NAME
    echo "✅ Environnement virtuel créé"
else
    echo "✅ Environnement virtuel existant trouvé"
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source $VENV_NAME/bin/activate

# Mettre à jour pip
echo "⬆️  Mise à jour de pip..."
pip install --upgrade pip

# Installer les dépendances essentielles
echo "📥 Installation des dépendances..."
pip install mcp paho-mqtt python-dotenv pydantic

# Créer le fichier .env
if [ ! -f ".env" ]; then
    echo "⚙️  Création du fichier de configuration..."
    cp .env.example .env
    echo "✅ Fichier .env créé"
else
    echo "✅ Fichier .env existant trouvé"
fi

echo ""
echo "🎉 Installation terminée!"
echo ""
echo "Prochaines étapes:"
echo "1. Installer Mosquitto: brew install mosquitto"
echo "2. Démarrer Mosquitto: brew services start mosquitto"
echo "3. Tester: python test_installation.py"
echo "4. Configurer Claude Desktop avec claude_desktop_config.json"
