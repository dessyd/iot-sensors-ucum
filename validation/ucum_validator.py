#!/usr/bin/env python3
"""
Validation des codes UCUM dans le système IoT
Auteur: Dominique Dessy
Version: 1.0
"""

import json
import re
from typing import Dict, List, Set, Tuple
import sys
import os

# Codes UCUM officiels pour IoT (subset)
OFFICIAL_UCUM_CODES = {
    # Température
    "Cel": {"name": "degree Celsius", "quantity": "thermodynamic temperature", "si_base": "K"},
    "[degF]": {"name": "degree Fahrenheit", "quantity": "thermodynamic temperature", "si_base": "K"},
    "K": {"name": "kelvin", "quantity": "thermodynamic temperature", "si_base": "K"},
    
    # Pression  
    "Pa": {"name": "pascal", "quantity": "pressure", "si_base": "Pa"},
    "hPa": {"name": "hectopascal", "quantity": "pressure", "si_base": "Pa"},
    "kPa": {"name": "kilopascal", "quantity": "pressure", "si_base": "Pa"}, 
    "bar": {"name": "bar", "quantity": "pressure", "si_base": "Pa"},
    "atm": {"name": "standard atmosphere", "quantity": "pressure", "si_base": "Pa"},
    
    # Luminosité
    "lx": {"name": "lux", "quantity": "illuminance", "si_base": "lx"},
    "cd/m2": {"name": "candela per square meter", "quantity": "luminance", "si_base": "cd/m2"},
    
    # Sans dimension
    "%": {"name": "percent", "quantity": "dimensionless", "si_base": "1"},
    "1": {"name": "unity", "quantity": "dimensionless", "si_base": "1"},
    
    # Électrique
    "V": {"name": "volt", "quantity": "electric potential", "si_base": "V"},
    "A": {"name": "ampere", "quantity": "electric current", "si_base": "A"},
    "W": {"name": "watt", "quantity": "power", "si_base": "W"},
    
    # Concentration
    "[ppm]": {"name": "parts per million", "quantity": "dimensionless", "si_base": "1"},
    "[ppb]": {"name": "parts per billion", "quantity": "dimensionless", "si_base": "1"},
}

class UCUMValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_arduino_config(self, config_path: str) -> bool:
        """Valide les codes UCUM dans la configuration Arduino"""
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Extraction des codes UCUM depuis config.h
            ucum_pattern = r'"([^"]*)",\s*//.*Code UCUM|"([^"]*)",.*// Code UCUM'
            matches = re.findall(ucum_pattern, content)
            
            valid = True
            for match in matches:
                code = match[0] or match[1]
                if code and code not in OFFICIAL_UCUM_CODES:
                    self.errors.append(f"Code UCUM non standard dans {config_path}: '{code}'")
                    valid = False
                elif code:
                    print(f"✓ Code UCUM valide: {code} ({OFFICIAL_UCUM_CODES[code]['name']})")
            
            return valid
        except FileNotFoundError:
            self.errors.append(f"Fichier de configuration Arduino non trouvé: {config_path}")
            return False
        except Exception as e:
            self.errors.append(f"Erreur lors de la lecture du fichier Arduino: {e}")
            return False
    
    def validate_mqtt_message(self, mqtt_payload: dict) -> bool:
        """Valide un message MQTT avec codes UCUM"""
        valid = True
        
        if "ucum" not in mqtt_payload:
            self.errors.append("Métadonnées UCUM manquantes dans le message MQTT")
            return False
        
        ucum_data = mqtt_payload["ucum"]
        ucum_code = ucum_data.get("code", "")
        
        if ucum_code not in OFFICIAL_UCUM_CODES:
            self.errors.append(f"Code UCUM invalide dans MQTT: '{ucum_code}'")
            valid = False
        
        return valid
    
    def suggest_corrections(self, invalid_code: str) -> List[str]:
        """Suggère des corrections pour un code UCUM invalide"""
        suggestions = []
        
        # Recherche par similarité
        for code, data in OFFICIAL_UCUM_CODES.items():
            if invalid_code.lower() in data["name"].lower():
                suggestions.append(f"{code} ({data['name']})")
        
        return suggestions[:3]
    
    def generate_report(self) -> str:
        """Génère un rapport de validation"""
        report = "=== Rapport de validation UCUM ===\n\n"
        
        if not self.errors and not self.warnings:
            report += "✅ Tous les codes UCUM sont conformes au standard!\n"
        else:
            if self.errors:
                report += f"❌ {len(self.errors)} erreur(s) trouvée(s):\n"
                for error in self.errors:
                    report += f"  - {error}\n"
                report += "\n"
            
            if self.warnings:
                report += f"⚠️  {len(self.warnings)} avertissement(s):\n"
                for warning in self.warnings:
                    report += f"  - {warning}\n"
                report += "\n"
        
        report += "\n=== Codes UCUM supportés ===\n"
        for code, data in OFFICIAL_UCUM_CODES.items():
            report += f"{code:<8} → {data['name']} ({data['quantity']})\n"
        
        return report

def main():
    validator = UCUMValidator()
    
    # Chemin vers la configuration Arduino
    arduino_config = "/Users/dominique/Documents/Arduino/iot-sensors-ucum/config.h"
    
    print("=== Validation UCUM du projet IoT ===\n")
    
    # Validation de la configuration Arduino
    if os.path.exists(arduino_config):
        print("Validation de la configuration Arduino...")
        validator.validate_arduino_config(arduino_config)
    else:
        print(f"⚠️  Configuration Arduino non trouvée: {arduino_config}")
    
    # Génération du rapport
    print("\n" + validator.generate_report())

if __name__ == "__main__":
    main()
