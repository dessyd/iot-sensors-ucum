#!/usr/bin/env python3
"""
Script de test pour vérifier l'installation du serveur MCP IoT
"""

import sys
import os
import asyncio

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_mqtt_client():
    """Test du client MQTT"""
    try:
        from iot_sensors_mcp.mqtt_client import MQTTClient, MQTTConfig
        
        print("✅ Import du client MQTT réussi")
        
        # Test de configuration
        config = MQTTConfig(host="localhost", port=1883)
        client = MQTTClient(config)
        
        print(f"✅ Configuration MQTT: {config.host}:{config.port}")
        
        # Test de connexion (optionnel si Mosquitto disponible)
        try:
            connected = await client.connect()
            if connected:
                print("✅ Connexion MQTT réussie")
                
                # Test de publication
                await client.publish("test/installation", "Test message from installation script")
                print("✅ Test de publication réussi")
                
                # Nettoyage
                if client.client:
                    client.client.loop_stop()
                    client.client.disconnect()
            else:
                print("⚠️  Connexion MQTT échouée (Mosquitto peut-être non démarré)")
        except Exception as e:
            print(f"⚠️  Test de connexion échoué: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

async def test_server():
    """Test du serveur MCP"""
    try:
        from iot_sensors_mcp.server import app, mqtt_config
        
        print("✅ Import du serveur MCP réussi")
        print(f"✅ Configuration serveur: {mqtt_config.host}:{mqtt_config.port}")
        
        # Test de la liste des outils
        tools = await app.list_tools()
        print(f"✅ Outils MCP disponibles: {len(tools)}")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import serveur: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")
        return False

async def main():
    """Test principal"""
    print("🧪 Test d'installation du serveur MCP IoT Sensors UCUM")
    print("====================================================")
    print()
    
    # Test des imports et de la configuration
    print("1. Test du client MQTT...")
    mqtt_ok = await test_mqtt_client()
    print()
    
    print("2. Test du serveur MCP...")
    server_ok = await test_server()
    print()
    
    # Résumé
    print("📋 Résumé des tests:")
    print(f"   Client MQTT: {'✅ OK' if mqtt_ok else '❌ ÉCHEC'}")
    print(f"   Serveur MCP: {'✅ OK' if server_ok else '❌ ÉCHEC'}")
    print()
    
    if mqtt_ok and server_ok:
        print("🎉 Installation réussie! Le serveur MCP est prêt à utiliser.")
        print()
        print("Configuration Claude Desktop:")
        print("Ajoutez ceci dans votre configuration Claude Desktop:")
        print()
        print('{')
        print('  "mcpServers": {')
        print('    "iot-sensors-mqtt": {')
        print('      "command": "python",')
        print('      "args": ["-m", "iot_sensors_mcp.server"],')
        print(f'      "cwd": "{os.path.abspath(os.path.dirname(__file__))}",')
        print('      "env": {')
        print('        "MQTT_BROKER_HOST": "localhost",')
        print('        "MQTT_BROKER_PORT": "1883"')
        print('      }')
        print('    }')
        print('  }')
        print('}')
        return 0
    else:
        print("❌ Installation incomplète. Vérifiez les erreurs ci-dessus.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
