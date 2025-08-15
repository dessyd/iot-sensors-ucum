#!/usr/bin/env python3
"""
Test de la nouvelle structure src/
"""

import sys
import os

# Ajouter src au path (depuis src/tests vers src)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.insert(0, src_dir)

def test_imports():
    print('🧪 Test de la nouvelle structure src/')
    print('=' * 50)
    
    try:
        # Test import du module principal
        import iot_sensors_mcp
        print('✅ Module iot_sensors_mcp importé')
        
        # Test import des sous-modules
        from iot_sensors_mcp.mqtt_client import MQTTClient, MQTTConfig
        print('✅ Client MQTT importé')
        
        from iot_sensors_mcp.server import main, mqtt_config
        print('✅ Serveur MCP importé')
        
        # Test de création du client
        client = iot_sensors_mcp.create_mqtt_client()
        print('✅ Client MQTT créé')
        
        # Test des unités UCUM
        ucum_count = sum(len(units) for units in client.ucum_units.values())
        print(f'✅ {ucum_count} unités UCUM disponibles')
        
        print()
        print('🎉 Tous les imports fonctionnent avec la nouvelle structure!')
        print('📁 Structure src/ validée')
        
        return True
        
    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
