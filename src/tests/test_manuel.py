#!/usr/bin/env python3
"""
Test manuel du serveur MCP - Version structure src/
"""

import sys
import os
import asyncio

# Ajouter src au path (depuis src/tests vers src)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.insert(0, src_dir)

async def test_serveur():
    print('🧪 Test manuel du serveur MCP IoT Sensors')
    print('=' * 50)
    
    try:
        # Import du serveur
        from iot_sensors_mcp.server import mqtt_client, mqtt_config
        print(f'✅ Serveur importé: {mqtt_config.host}:{mqtt_config.port}')
        
        # Test de connexion MQTT
        print('🔗 Test de connexion MQTT...')
        connected = await mqtt_client.connect()
        
        if connected:
            print('✅ Connexion MQTT réussie!')
            
            # Test de publication
            success = await mqtt_client.publish('test/manual/structure', 'Test nouvelle structure src/')
            if success:
                print('✅ Publication de test réussie')
            
            # Test de données capteur
            success = await mqtt_client.publish_sensor_data(
                topic='test/sensor/temperature',
                sensor_id='test_temp_structure',
                value=24.5,
                unit='Cel'
            )
            if success:
                print('✅ Publication capteur réussie')
            
            # Statut
            status = mqtt_client.get_status()
            print(f'📊 Statut: {status["connected"]} - {status["total_messages_stored"]} messages')
            
            await mqtt_client.disconnect()
            print('✅ Test complet réussi avec la nouvelle structure!')
            
        else:
            print('❌ Connexion MQTT échouée')
            print('💡 Vérifiez que Mosquitto est démarré: brew services start mosquitto')
        
    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_serveur())
