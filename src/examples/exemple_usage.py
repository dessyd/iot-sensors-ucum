#!/usr/bin/env python3
"""
Exemple d'utilisation du client MQTT IoT Sensors UCUM
Simule des capteurs envoyant des données périodiquement
"""

import sys
import os
import asyncio
import json
import random
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from iot_sensors_mcp import create_mqtt_client


class SensorSimulator:
    """Simulateur de capteurs IoT"""
    
    def __init__(self, mqtt_client):
        self.client = mqtt_client
        self.sensors = {
            "temp_bureau": {"type": "temperature", "unit": "Cel", "base": 22.0, "variation": 3.0},
            "temp_exterieur": {"type": "temperature", "unit": "Cel", "base": 15.0, "variation": 8.0},
            "hum_bureau": {"type": "humidity", "unit": "%", "base": 45.0, "variation": 15.0},
            "pression_ext": {"type": "pressure", "unit": "hPa", "base": 1013.25, "variation": 20.0},
        }
        
    def generate_value(self, sensor_config):
        """Générer une valeur aléatoire pour un capteur"""
        base = sensor_config["base"]
        variation = sensor_config["variation"]
        # Valeur avec variation aléatoire
        value = base + random.uniform(-variation/2, variation/2)
        return round(value, 2)
    
    async def publish_sensor_reading(self, sensor_id, config):
        """Publier une lecture de capteur"""
        value = self.generate_value(config)
        topic = f"iot/sensors/{config['type']}/{sensor_id}"
        
        # Données supplémentaires
        additional_data = {
            "location": "Bureau Dominique" if "bureau" in sensor_id else "Extérieur",
            "battery_level": random.randint(80, 100),
            "signal_strength": random.randint(-60, -30)
        }
        
        success = await self.client.publish_sensor_data(
            topic=topic,
            sensor_id=sensor_id,
            value=value,
            unit=config["unit"],
            additional_data=additional_data
        )
        
        if success:
            print(f"📊 {sensor_id}: {value} {config['unit']} → {topic}")
        else:
            print(f"❌ Échec publication {sensor_id}")
        
        return success
    
    async def run_simulation(self, duration_minutes=5, interval_seconds=10):
        """Lancer la simulation pendant une durée donnée"""
        print(f"🚀 Démarrage simulation ({duration_minutes} min, intervalle {interval_seconds}s)")
        print(f"📡 Capteurs: {list(self.sensors.keys())}")
        print("" + "="*60)
        
        end_time = asyncio.get_event_loop().time() + (duration_minutes * 60)
        
        while asyncio.get_event_loop().time() < end_time:
            print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Cycle de mesures")
            
            # Publier toutes les mesures
            tasks = []
            for sensor_id, config in self.sensors.items():
                task = self.publish_sensor_reading(sensor_id, config)
                tasks.append(task)
            
            # Attendre que toutes les publications soient terminées
            results = await asyncio.gather(*tasks)
            success_count = sum(results)
            
            print(f"✅ {success_count}/{len(self.sensors)} capteurs publiés")
            
            # Attendre le prochain cycle
            await asyncio.sleep(interval_seconds)
        
        print(f"\n🏁 Simulation terminée après {duration_minutes} minutes")


async def demo_basic():
    """Démonstration basique"""
    print("🧪 Démonstration IoT Sensors UCUM")
    print("================================\n")
    
    # Créer le client MQTT
    client = create_mqtt_client(client_id="demo_iot_sensors")
    
    try:
        # Connexion
        print("🔗 Connexion au broker MQTT...")
        connected = await client.connect()
        
        if not connected:
            print("❌ Impossible de se connecter à MQTT")
            print("💡 Assurez-vous que Mosquitto est démarré:")
            print("   brew install mosquitto")
            print("   brew services start mosquitto")
            return
        
        print("✅ Connexion MQTT établie!")
        
        # S'abonner aux topics de capteurs
        await client.subscribe("iot/sensors/#")
        print("✅ Abonné aux topics iot/sensors/#")
        
        # Publier quelques mesures manuelles
        print("\n📊 Publication de mesures de test...")
        
        test_readings = [
            {"topic": "iot/sensors/temperature/test_temp", "sensor_id": "test_temp", "value": 23.5, "unit": "Cel"},
            {"topic": "iot/sensors/humidity/test_hum", "sensor_id": "test_hum", "value": 65.2, "unit": "%"},
            {"topic": "iot/sensors/pressure/test_press", "sensor_id": "test_press", "value": 1013.25, "unit": "hPa"},
        ]
        
        for reading in test_readings:
            await client.publish_sensor_data(**reading)
            await asyncio.sleep(0.5)
        
        # Attendre un peu pour recevoir les messages
        print("\n⏳ Attente des messages (3 secondes)...")
        await asyncio.sleep(3)
        
        # Afficher l'historique
        print("\n📜 Historique des messages reçus:")
        all_topics = client.get_all_topics()
        
        if all_topics:
            for topic in sorted(all_topics):
                history = client.get_message_history(topic, limit=5)
                print(f"\n🔖 {topic}:")
                for msg in history:
                    if msg.sensor_id and msg.value and msg.unit:
                        print(f"   • {msg.sensor_id}: {msg.value} {msg.unit} [{msg.timestamp.strftime('%H:%M:%S')}]")
                    else:
                        print(f"   • {msg.payload[:50]}... [{msg.timestamp.strftime('%H:%M:%S')}]")
        else:
            print("📭 Aucun message reçu")
        
        # Afficher le statut
        status = client.get_status()
        print(f"\n📊 Statut final:")
        print(f"   Topics abonnés: {status['subscribed_topics']}")
        print(f"   Messages stockés: {status['total_messages_stored']}")
        
    finally:
        await client.disconnect()
        print("\n👋 Déconnexion MQTT")


async def demo_simulation():
    """Démonstration avec simulation de capteurs"""
    print("🏭 Simulation de capteurs IoT")
    print("============================\n")
    
    client = create_mqtt_client(client_id="simulator_iot_sensors")
    
    try:
        connected = await client.connect()
        if not connected:
            print("❌ Connexion MQTT impossible")
            return
        
        print("✅ Connexion établie")
        
        # S'abonner pour voir tous les messages
        await client.subscribe("iot/sensors/#")
        
        # Créer et lancer le simulateur
        simulator = SensorSimulator(client)
        await simulator.run_simulation(duration_minutes=2, interval_seconds=5)
        
        # Résumé final
        print("\n📈 Résumé de la simulation:")
        all_topics = client.get_all_topics()
        for topic in sorted(all_topics):
            count = len(client.get_message_history(topic))
            print(f"   {topic}: {count} messages")
        
    finally:
        await client.disconnect()


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Exemple IoT Sensors UCUM")
    parser.add_argument("--simulation", action="store_true", help="Lancer la simulation de capteurs")
    parser.add_argument("--duration", type=int, default=2, help="Durée simulation en minutes")
    
    args = parser.parse_args()
    
    if args.simulation:
        # Modifier la durée si spécifiée
        original_duration = 2
        SensorSimulator.run_simulation.__defaults__ = (args.duration, 5)
        await demo_simulation()
    else:
        await demo_basic()
    
    print("\n🎉 Démonstration terminée!")
    print("\n💡 Essayez aussi:")
    print("   python3 exemple_usage.py --simulation")
    print("   python3 exemple_usage.py --simulation --duration 5")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
