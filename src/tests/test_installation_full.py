#!/usr/bin/env python3
"""
Test d'installation complet avec Python 3.13 et MCP
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


async def test_python_version():
    """Test de la version Python"""
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 10):
        print("✅ Version Python compatible avec MCP")
        return True
    else:
        print("❌ Version Python trop ancienne pour MCP (requis: 3.10+)")
        return False


async def test_mcp_import():
    """Test d'import MCP"""
    try:
        import mcp
        from mcp.server import Server
        from mcp.types import Tool, TextContent
        print("✅ MCP importé avec succès")
        print(f"   Version MCP disponible")
        return True
    except ImportError as e:
        print(f"❌ Erreur import MCP: {e}")
        print("💡 Installez avec: pip install mcp")
        return False


async def test_mqtt_client():
    """Test du client MQTT"""
    try:
        from iot_sensors_mcp.mqtt_client import MQTTClient, MQTTConfig, create_mqtt_client
        
        print("✅ Client MQTT importé")
        
        # Test de configuration
        config = MQTTConfig(host="localhost", port=1883)
        client = MQTTClient(config)
        
        print(f"✅ Configuration: {config.host}:{config.port}")
        
        # Test des unités UCUM
        ucum_count = sum(len(units) for units in client.ucum_units.values())
        print(f"✅ {ucum_count} unités UCUM supportées")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import client MQTT: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur client MQTT: {e}")
        return False


async def test_server_mcp():
    """Test du serveur MCP"""
    try:
        from iot_sensors_mcp.server import app, mqtt_config
        
        print("✅ Serveur MCP importé")
        print(f"✅ Configuration serveur: {mqtt_config.host}:{mqtt_config.port}")
        
        # Test de la liste des outils
        tools = await app.list_tools()
        print(f"✅ {len(tools)} outils MCP disponibles:")
        for tool in tools:
            print(f"   • {tool.name}: {tool.description[:50]}...")
        
        # Test des ressources
        resources = await app.list_resources()
        print(f"✅ {len(resources)} ressources MCP disponibles")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import serveur MCP: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur serveur MCP: {e}")
        return False


async def test_mqtt_connection():
    """Test de connexion MQTT"""
    try:
        from iot_sensors_mcp import create_mqtt_client
        
        print("\n🔗 Test de connexion MQTT...")
        client = create_mqtt_client(client_id="test_installation_full")
        
        connected = await client.connect()
        
        if connected:
            print("✅ Connexion MQTT réussie!")
            
            # Test complet avec publication et abonnement
            await client.subscribe("test/installation/#")
            print("✅ Abonnement réussi")
            
            # Publier plusieurs types de capteurs
            sensors_data = [
                {"topic": "test/installation/temperature", "sensor_id": "temp_test", "value": 23.5, "unit": "Cel"},
                {"topic": "test/installation/humidity", "sensor_id": "hum_test", "value": 65.2, "unit": "%"},
                {"topic": "test/installation/pressure", "sensor_id": "press_test", "value": 1013.25, "unit": "hPa"}
            ]
            
            for sensor in sensors_data:
                success = await client.publish_sensor_data(**sensor)
                if success:
                    print(f"✅ Publié: {sensor['sensor_id']} = {sensor['value']} {sensor['unit']}")
                else:
                    print(f"❌ Échec publication: {sensor['sensor_id']}")
            
            # Attendre la réception
            await asyncio.sleep(2)
            
            # Vérifier l'historique
            total_messages = 0
            for sensor in sensors_data:
                history = client.get_message_history(sensor["topic"])
                total_messages += len(history)
                if history:
                    msg = history[-1]
                    print(f"📜 Dernier message {sensor['topic']}: {msg.payload[:50]}...")
            
            print(f"✅ {total_messages} messages reçus et stockés")
            
            # Statut final
            status = client.get_status()
            print(f"📊 Statut: {status['subscribed_topics']} abonnements, {status['total_messages_stored']} messages")
            
            await client.disconnect()
            return True
            
        else:
            print("⚠️ Connexion MQTT échouée")
            print("💡 Vérifiez que Mosquitto est démarré:")
            print("   brew services start mosquitto")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test connexion: {e}")
        return False


async def test_claude_integration():
    """Test de l'intégration Claude Desktop"""
    try:
        # Vérifier le fichier de configuration
        config_path = "claude_desktop_config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print("✅ Configuration Claude Desktop trouvée")
            
            if "mcpServers" in config and "iot-sensors-mqtt" in config["mcpServers"]:
                server_config = config["mcpServers"]["iot-sensors-mqtt"]
                print(f"✅ Serveur MCP configuré: {server_config.get('command', 'N/A')}")
                print(f"✅ Répertoire: {server_config.get('cwd', 'N/A')}")
                
                # Vérifier les variables d'environnement
                env_vars = server_config.get("env", {})
                print(f"✅ Variables d'environnement: {len(env_vars)} définies")
                
                return True
            else:
                print("❌ Configuration serveur MCP manquante")
                return False
        else:
            print("⚠️ Fichier de configuration Claude Desktop non trouvé")
            print("💡 Copiez claude_desktop_config.json dans votre configuration Claude")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test intégration Claude: {e}")
        return False


async def main():
    """Test principal complet"""
    print("🧪 Test d'installation complet - IoT Sensors UCUM avec Python 3.13")
    print("=" * 70)
    print()
    
    # Tests séquentiels
    tests = [
        ("Version Python", test_python_version),
        ("Import MCP", test_mcp_import),
        ("Client MQTT", test_mqtt_client),
        ("Serveur MCP", test_server_mcp),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Test: {test_name}")
        print("-" * 30)
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            results[test_name] = False
    
    # Tests optionnels (dépendent de Mosquitto et configuration)
    optional_tests = [
        ("Connexion MQTT", test_mqtt_connection),
        ("Intégration Claude", test_claude_integration),
    ]
    
    for test_name, test_func in optional_tests:
        print(f"\n🔍 Test optionnel: {test_name}")
        print("-" * 30)
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ Erreur: {e}")
            results[test_name] = False
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    core_tests = ["Version Python", "Import MCP", "Client MQTT", "Serveur MCP"]
    optional_tests_names = ["Connexion MQTT", "Intégration Claude"]
    
    core_passed = sum(1 for test in core_tests if results.get(test, False))
    optional_passed = sum(1 for test in optional_tests_names if results.get(test, False))
    
    print(f"\n✅ Tests principaux: {core_passed}/{len(core_tests)} réussis")
    print(f"✅ Tests optionnels: {optional_passed}/{len(optional_tests_names)} réussis")
    
    for test_name, passed in results.items():
        status = "✅ RÉUSSI" if passed else "❌ ÉCHEC"
        category = "[PRINCIPAL]" if test_name in core_tests else "[OPTIONNEL]"
        print(f"   {status} {category} {test_name}")
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS")
    print("-" * 30)
    
    if core_passed == len(core_tests):
        print("🎉 Installation principale réussie!")
        
        if not results.get("Connexion MQTT", False):
            print("📋 Pour activer MQTT:")
            print("   1. brew install mosquitto")
            print("   2. brew services start mosquitto")
            print("   3. Relancer ce test")
        
        if not results.get("Intégration Claude", False):
            print("📋 Pour activer Claude Desktop:")
            print("   1. Copier claude_desktop_config.json vers votre config Claude")
            print("   2. Redémarrer Claude Desktop")
            print("   3. Tester avec: 'Quel est le statut de ma connexion MQTT?'")
        
        if results.get("Connexion MQTT", False) and results.get("Intégration Claude", False):
            print("🚀 Installation complète réussie!")
            print("   Vous pouvez maintenant utiliser Claude avec MQTT pour vos projets IoT")
    
    else:
        print("❌ Installation incomplète - vérifiez les erreurs ci-dessus")
        print("💡 Relancez ./install_full.sh si nécessaire")
    
    return 0 if core_passed == len(core_tests) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
