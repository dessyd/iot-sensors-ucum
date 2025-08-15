# Guide de Test - Serveur MCP IoT-Sensors MQTT

## 📋 Vue d'ensemble

Ce guide contient tous les prompts et exemples pour tester votre serveur MCP IoT-Sensors avec support des connexions MQTT multiples.

**Version:** Connexions Multiples v1.0  
**Auteur:** Dominique Dessy - Splunk Presales Engineer  
**Date:** Août 2025

---

## 🔗 Gestion des Connexions

### Statut et Monitoring

#### Voir le statut des connexions

```texttext
Affiche-moi le statut de toutes mes connexions MQTT
```

#### Lister toutes les connexions

```texttext
Liste toutes mes connexions MQTT disponibles
```

#### Rapport complet

```text
Donne-moi un rapport complet de toutes mes connexions MQTT avec leur statut
```

### Connexions

#### Se connecter à un nouveau serveur

```text
Connecte-toi au serveur MQTT 192.168.1.20 avec l'ID "bureau"
```

```text
Ajoute une connexion au serveur MQTT test.mosquitto.org sur le port 1883 avec l'ID "public"
```

```text
Connecte-toi au serveur 192.168.1.30 sur le port 8883 avec l'ID "secure"
```

#### Changer la connexion active

```text
Change la connexion active vers "localhost"
```

```text
Utilise maintenant la connexion "homelab" comme connexion active
```

#### Déconnexions

```text
Déconnecte la connexion "bureau"
```

---

## 📤 Publication de Messages

### Messages Simples

#### Publication basique

```text
Publie "Test message from Claude" sur le topic "test/messages"
```

```text
Envoie le message "Hello World" sur le topic "demo/test" via la connexion active
```

#### Test de connectivité

```text
Teste la connectivité en publiant un message "ping" sur "test/connectivity" sur chaque connexion active
```

### Données de Capteurs IoT (Format UCUM)

#### Capteurs de température

```text
Publie une température de 22.5°C du capteur "kitchen_temp" sur le topic "home/kitchen/temperature"
```

```text
Publie une température de 20°C du capteur "bedroom_sensor" sur "home/bedroom/temp"
```

```text
Simule un capteur de température qui publie 23.4°C sur "sensors/living/temp" avec l'ID "living_temp_01"
```

#### Capteurs d'humidité

```text
Envoie les données du capteur d'humidité "bathroom_hum" avec une valeur de 65% sur "home/bathroom/humidity"
```

#### Capteurs de pression

```text
Publie une pression de 1013.25 hPa du capteur "weather_station" sur "outdoor/weather/pressure"
```

#### Capteurs de distance

```text
Crée des données pour un capteur de distance qui mesure 2.5 mètres sur le topic "sensors/parking/distance" avec l'ID "parking_sensor"
```

```text
Mesure une distance de 150 cm du capteur "ultrasonic_01" sur "garage/distance"
```

#### Autres capteurs

```text
Envoie une mesure de vitesse de 45 km/h du capteur "car_gps" sur "vehicle/speed"
```

```text
Publie un poids de 2.5 kg du capteur "kitchen_scale" sur "home/kitchen/weight"
```

---

## 🧪 Tests Avancés

### Test de Connexions Multiples

```text
1. Connecte-toi au serveur 192.168.1.15 avec l'ID "local"
2. Connecte-toi aussi à test.mosquitto.org avec l'ID "public" 
3. Liste toutes les connexions
4. Publie "test local" sur "test/local" via la connexion "local"
5. Change vers la connexion "public" et publie "test public" sur "test/public"
```

### Test de Basculement de Serveurs

```text
1. Utilise la connexion "localhost" et publie "test local" sur "demo/test"
2. Bascule vers "homelab" et publie "test homelab" sur "demo/test"  
3. Reviens sur "localhost" et publie "retour local" sur "demo/test"
```

### Test de Reconnexion

```text
1. Liste mes connexions
2. Déconnecte la connexion "homelab"
3. Reconnecte-toi à 192.168.1.15 avec l'ID "homelab2"
4. Vérifie le statut
```

---

## 🏠 Scénarios de Test Réalistes

### Monitoring Domestique

```text
1. Connecte-toi à mon serveur domotique 192.168.1.50 avec l'ID "domotique"
2. Publie la température du salon (21.5°C) sur "maison/salon/temperature"
3. Publie l'humidité de la salle de bain (68%) sur "maison/sdb/humidite"
4. Vérifie que tout est bien publié
```

### Station Météo

```text
1. Connecte-toi au serveur météo 192.168.1.100 avec l'ID "meteo"
2. Publie température extérieure (18.3°C) sur "weather/outdoor/temp"
3. Publie humidité extérieure (72%) sur "weather/outdoor/humidity"
4. Publie pression atmosphérique (1015.2 hPa) sur "weather/outdoor/pressure"
```

### Monitoring Industriel

```text
1. Connecte-toi au serveur industriel 10.0.1.50 avec l'ID "factory"
2. Publie température machine A (85.2°C) sur "factory/machine_a/temp"
3. Publie vibration machine B (2.1 m/s) sur "factory/machine_b/vibration"
4. Publie niveau réservoir (75%) sur "factory/tank_01/level"
```

---

## 🔧 Tests de Robustesse

### Gestion d'Erreurs

```text
Essaie de te connecter à un serveur inexistant 192.168.999.999 avec l'ID "erreur"
```

```text
Tente de publier un message sur une connexion inexistante "fake_connection"
```

### Test de Performance

```text
1. Connecte-toi à 3 serveurs différents simultanément
2. Publie des messages sur chacun en basculant rapidement
3. Vérifie que toutes les connexions restent stables
```

---

## 📊 Unités UCUM Supportées

### Température

- `Cel` : Celsius
- `degF` : Fahrenheit  
- `K` : Kelvin

### Distance/Longueur

- `m` : mètres
- `cm` : centimètres
- `mm` : millimètres
- `ft` : pieds
- `in` : pouces

### Pression

- `Pa` : Pascal
- `hPa` : hectoPascal
- `mmHg` : millimètres de mercure
- `psi` : livres par pouce carré

### Vitesse

- `m/s` : mètres par seconde
- `km/h` : kilomètres par heure
- `mph` : miles par heure

### Masse

- `kg` : kilogrammes
- `g` : grammes
- `lb` : livres
- `oz` : onces

### Volume

- `L` : litres
- `mL` : millilitres
- `gal` : gallons
- `fl_oz` : onces liquides

### Humidité

- `%` : pourcentage

---

## 🚀 Exemples Rapides

### Test Rapide Complet

```text
1. Liste mes connexions MQTT
2. Connecte-toi à 192.168.1.15 avec l'ID "test"
3. Publie "Hello from test connection" sur "demo/hello"
4. Publie une température de 21°C du capteur "demo_temp" sur "demo/temperature"
5. Affiche le statut final
```

### Nettoyage après Tests

```text
1. Liste toutes mes connexions
2. Déconnecte toutes les connexions de test
3. Garde seulement la connexion "localhost"
```

---

## 📝 Notes Importantes

- **Connexion par défaut** : `localhost:1883` (toujours présente au démarrage)
- **Format des données capteurs** : JSON avec timestamp, sensor_id, value, unit
- **QoS par défaut** : 1 (au moins une fois)
- **Gestion automatique** : Reconnexion et réabonnement automatiques
- **Thread-safe** : Gestion sécurisée des connexions multiples

---

## 🔍 Debugging

### En cas de problème

```texttext
Affiche-moi le statut détaillé de toutes mes connexions MQTT
```

### Test de base

```texttext
Publie un simple "test" sur le topic "debug/test" pour vérifier la connectivité
```

---

## Fin du Guide de Test

*Pour plus d'informations, consultez la documentation technique ou contactez Dominique Dessy.*
