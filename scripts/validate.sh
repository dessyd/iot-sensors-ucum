#!/bin/bash

# Script de validation du projet IoT Sensors UCUM
# Auteur: Dominique Dessy
# Version: 1.0

echo "=== Validation du projet IoT Sensors UCUM ==="
echo ""

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de validation
validate_item() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        return 0
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

validate_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

validate_info() {
    echo -e "ℹ️  $1"
}

errors=0

echo "📁 Vérification de la structure des fichiers..."

# Vérification des fichiers principaux
[ -f "README.md" ] && validate_item 0 "README.md présent" || { validate_item 1 "README.md manquant"; ((errors++)); }
[ -f "docker-compose.yml" ] && validate_item 0 "docker-compose.yml présent" || { validate_item 1 "docker-compose.yml manquant"; ((errors++)); }
[ -f ".gitignore" ] && validate_item 0 ".gitignore présent" || { validate_item 1 ".gitignore manquant"; ((errors++)); }

# Vérification du lien symbolique Arduino
if [ -L "arduino" ]; then
    target=$(readlink arduino)
    if [ -d "$target" ]; then
        validate_item 0 "Lien symbolique Arduino correct → $target"
    else
        validate_item 1 "Lien symbolique Arduino pointe vers un répertoire inexistant"
        ((errors++))
    fi
else
    validate_item 1 "Lien symbolique Arduino manquant"
    ((errors++))
fi

# Vérification des fichiers Arduino
arduino_path="/Users/dominique/Documents/Arduino/iot-sensors-ucum"
if [ -d "$arduino_path" ]; then
    validate_item 0 "Répertoire Arduino présent"
    
    [ -f "$arduino_path/iot-sensors-ucum.ino" ] && validate_item 0 "Code Arduino principal présent" || { validate_item 1 "Code Arduino principal manquant"; ((errors++)); }
    [ -f "$arduino_path/config.h" ] && validate_item 0 "Configuration Arduino présente" || { validate_item 1 "Configuration Arduino manquante"; ((errors++)); }
    [ -f "$arduino_path/arduino_secrets.h.template" ] && validate_item 0 "Template secrets présent" || { validate_item 1 "Template secrets manquant"; ((errors++)); }
    
    if [ -f "$arduino_path/arduino_secrets.h" ]; then
        validate_warning "Fichier arduino_secrets.h présent (ne sera pas commité)"
    else
        validate_info "Fichier arduino_secrets.h absent (normal, à créer depuis le template)"
    fi
else
    validate_item 1 "Répertoire Arduino manquant"
    ((errors++))
fi

echo ""
echo "🐳 Vérification de la configuration Docker..."

# Vérification des fichiers Docker
[ -f "telegraf/telegraf.conf" ] && validate_item 0 "Configuration Telegraf présente" || { validate_item 1 "Configuration Telegraf manquante"; ((errors++)); }
[ -f "mosquitto/config/mosquitto.conf" ] && validate_item 0 "Configuration Mosquitto présente" || { validate_item 1 "Configuration Mosquitto manquante"; ((errors++)); }
[ -f "grafana/provisioning/datasources/influxdb.yml" ] && validate_item 0 "Datasource Grafana configuré" || { validate_item 1 "Datasource Grafana manquant"; ((errors++)); }
[ -f "grafana/dashboards/iot-ucum-dashboard.json" ] && validate_item 0 "Dashboard UCUM présent" || { validate_item 1 "Dashboard UCUM manquant"; ((errors++)); }

echo ""
echo "🔧 Vérification des scripts et outils..."

[ -f "scripts/deploy.sh" ] && [ -x "scripts/deploy.sh" ] && validate_item 0 "Script de déploiement exécutable" || { validate_item 1 "Script de déploiement manquant ou non exécutable"; ((errors++)); }
[ -f "validation/ucum_validator.py" ] && validate_item 0 "Validateur UCUM présent" || { validate_item 1 "Validateur UCUM manquant"; ((errors++)); }

echo ""
echo "📚 Vérification de la documentation..."

[ -f "docs/TECHNICAL.md" ] && validate_item 0 "Documentation technique présente" || { validate_item 1 "Documentation technique manquante"; ((errors++)); }

echo ""
echo "🔍 Vérification des prérequis système..."

# Vérification Docker
if command -v docker &> /dev/null; then
    validate_item 0 "Docker installé"
else
    validate_item 1 "Docker non installé"
    ((errors++))
fi

# Vérification Docker Compose
if command -v docker-compose &> /dev/null; then
    validate_item 0 "Docker Compose installé"
else
    validate_item 1 "Docker Compose non installé"
    ((errors++))
fi

# Vérification Python
if command -v python3 &> /dev/null; then
    validate_item 0 "Python 3 installé"
else
    validate_item 1 "Python 3 non installé"
    ((errors++))
fi

echo ""
echo "🔬 Test de validation UCUM..."

if [ -f "validation/ucum_validator.py" ]; then
    cd validation
    python3 ucum_validator.py > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        validate_item 0 "Validation UCUM réussie"
    else
        validate_item 1 "Échec de la validation UCUM"
        ((errors++))
    fi
    cd ..
else
    validate_warning "Validateur UCUM introuvable, test ignoré"
fi

echo ""
echo "📊 Git et versioning..."

if [ -d ".git" ]; then
    validate_item 0 "Dépôt Git initialisé"
    
    # Vérification du statut Git
    git_status=$(git status --porcelain | wc -l)
    if [ $git_status -eq 0 ]; then
        validate_item 0 "Tous les fichiers sont commités"
    else
        validate_warning "$git_status fichier(s) non commité(s)"
    fi
else
    validate_item 1 "Dépôt Git non initialisé"
    ((errors++))
fi

echo ""
echo "=== Résumé de la validation ==="

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}🎉 Validation réussie ! Le projet est prêt à être utilisé.${NC}"
    echo ""
    echo "📋 Étapes suivantes :"
    echo "  1. Configurer arduino_secrets.h avec vos paramètres WiFi"
    echo "  2. Uploader le code vers votre Arduino MKR1010"
    echo "  3. Lancer le déploiement : ./scripts/deploy.sh"
    echo "  4. Accéder à Grafana : http://localhost:3000"
    echo ""
    echo "📖 Consultez le README.md pour des instructions détaillées"
else
    echo -e "${RED}❌ Validation échouée avec $errors erreur(s).${NC}"
    echo ""
    echo "🔧 Corrigez les erreurs ci-dessus avant de continuer."
    echo "📖 Consultez la documentation pour plus d'aide."
fi

echo ""
echo "🏷️  Projet IoT Sensors UCUM v1.0 - Dominique Dessy"
exit $errors
