#!/usr/bin/env python3
"""
Test simple du client MQTT - fonctionne même sans broker
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_client_import():
    """Test d'import et configuration"""
    try:
        from iot_sensors_mcp.mqtt_client import MQTTClient, MQTTConfig, create_mqtt_client
        
        print("✅ Import réussi!")
        
        # Test de configuration
        config = MQTTConfig(host="localhost", port=1883)
        print(f"✅ Configuration: {config.host}:{config.port}")
        
        # Test de création du client
        client = MQTTClient(config)
        print(f"✅ Client créé: {client.config.client_id}")
        
        # Test des unités UCUM
        print("\n📏 Unités UCUM supportées:")
        for category, units in client.ucum_units.items():
            print(f"   {category}: {', '.join(units)}")
        
        # Test de création via fonction helper
        simple_client = create_mqtt_client()
        print(f"\n✅ Client simple créé: {simple_client.config.client_id}")
        
        # Test de statut (sans connexion)
        status = client.get_status()
        print("\n📊 Statut client:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

async def test_with_broker():
    """Test avec broker si disponible"""
    try:
        from iot_sensors_mcp.mqtt_client import create_mqtt_client
        
        print("\n🔗 Test de connexion MQTT...")
        client = create_mqtt_client()
        
        connected = await client.connect()
        
        if connected:
            print("✅ Connexion MQTT réussie!")
            
            # Test de publication
            sensor_data = {
                "sensor_id": "test_sensor_001",
                "value": 23.5,
                "unit": "Cel",
                "timestamp": datetime.now().isoformat(),
                "location": "Test Lab"
            }
            
            success = await client.publish("iot/test/temperature", json.dumps(sensor_data))
            if success:
                print("✅ Publication réussie!")
            
            # Test d'abonnement
            await client.subscribe("iot/test/#")
            print("✅ Abonnement réussi!")
            
            # Attendre un peu
            await asyncio.sleep(1)
            
            # Publier un autre message pour tester la réception
            await client.publish_sensor_data(
                topic="iot/test/humidity",
                sensor_id="hum_001",
                value=65.2,
                unit="%",
                additional_data={"location": "Test Lab"}
            )
            
            await asyncio.sleep(1)
            
            # Vérifier l'historique
            history = client.get_message_history("iot/test/humidity")
            if history:
                print(f"📜 Historique: {len(history)} messages")
                for msg in history:
                    print(f"   - {msg.sensor_id}: {msg.value} {msg.unit}")
            
            await client.disconnect()
            return True
            
        else:
            print("⚠️  Connexion MQTT échouée")
            print("💡 Pour utiliser MQTT, installez et démarrez Mosquitto:")
            print("   brew install mosquitto")
            print("   brew services start mosquitto")
            return False
            
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False

async def main():
    print("🧪 Test IoT Sensors UCUM - Client MQTT")
    print("======================================\n")
    
    # Test des imports et configuration
    import_ok = await test_client_import()
    
    if import_ok:
        print("\n" + "="*50)
        # Test avec broker
        broker_ok = await test_with_broker()
        
        print("\n📋 Résumé:")
        print(f"   Configuration: {'✅ OK' if import_ok else '❌ ÉCHEC'}")
        print(f"   Connexion MQTT: {'✅ OK' if broker_ok else '⚠️  Non disponible'}")
        
        if import_ok:
            print("\n🎉 Le client MQTT est prêt à utiliser!")
            if not broker_ok:
                print("\n💡 Prochaines étapes:")
                print("1. Installer Mosquitto: brew install mosquitto")
                print("2. Démarrer Mosquitto: brew services start mosquitto")
                print("3. Relancer ce test")
            else:
                print("\n🚀 Tout fonctionne! Vous pouvez maintenant:")
                print("   - Utiliser le client MQTT dans vos projets")
                print("   - Configurer Claude Desktop avec MCP (Python 3.10+ requis)")
        
        return 0 if import_ok else 1
    else:
        print("\n❌ Problème avec l'installation")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
