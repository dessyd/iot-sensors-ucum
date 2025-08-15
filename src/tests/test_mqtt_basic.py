#!/usr/bin/env python3
"""
Test de base du client MQTT sans MCP (Python 3.9 compatible)
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_mqtt_basic():
    """Test de base du client MQTT"""
    try:
        from iot_sensors_mcp.mqtt_client import MQTTClient, MQTTConfig
        
        print("✅ Import du client MQTT réussi")
        
        # Configuration
        config = MQTTConfig(host="localhost", port=1883)
        client = MQTTClient(config)
        
        print(f"✅ Configuration: {config.host}:{config.port}")
        
        # Test de connexion
        print("🔗 Test de connexion MQTT...")
        connected = await client.connect()
        
        if connected:
            print("✅ Connexion MQTT réussie!")
            
            # Test de publication
            topic = "test/iot-sensors-ucum"
            message = json.dumps({
                "sensor_id": "test_sensor",
                "value": 23.5,
                "unit": "Cel",
                "timestamp": datetime.now().isoformat(),
                "source": "test_script"
            })
            
            success = await client.publish(topic, message)
            if success:
                print(f"✅ Message publié sur {topic}")
                print(f"📄 Contenu: {message}")
            else:
                print("❌ Échec de publication")
            
            # Test d'abonnement
            await client.subscribe("test/#")
            print("✅ Abonnement au topic test/#")
            
            # Attendre un peu pour recevoir des messages
            print("⏳ Attente de messages... (3 secondes)")
            await asyncio.sleep(3)
            
            # Vérifier l'historique
            history = client.get_message_history(topic)
            if history:
                print(f"📜 Messages reçus: {len(history)}")
                for msg in history:
                    print(f"   - [{msg.timestamp.strftime('%H:%M:%S')}] {msg.payload[:50]}...")
            else:
                print("📭 Aucun message dans l'historique")
            
            # Statut
            status = client.get_status()
            print("📊 Statut:")
            print(f"   - Connecté: {status['connected']}")
            print(f"   - Topics abonnés: {status['subscribed_topics']}")
            print(f"   - Messages stockés: {status['total_messages_stored']}")
            
            # Nettoyage
            if client.client:
                client.client.loop_stop()
                client.client.disconnect()
            
            print("\n🎉 Test MQTT réussi!")
            return True
            
        else:
            print("❌ Impossible de se connecter à MQTT")
            print("💡 Vérifiez que Mosquitto est démarré:")
            print("   brew services start mosquitto")
            return False
            
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Lancez d'abord: ./install_basic.sh")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

async def main():
    print("🧪 Test MQTT de base - IoT Sensors UCUM")
    print("=======================================\n")
    
    success = await test_mqtt_basic()
    
    if success:
        print("\n✅ Le client MQTT fonctionne correctement!")
        print("\nPour utiliser avec Claude Desktop:")
        print("1. Installer Python 3.10+: brew install python@3.11")
        print("2. Réinstaller avec MCP support")
        print("3. Configurer Claude Desktop")
    else:
        print("\n❌ Test échoué - vérifiez la configuration")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
