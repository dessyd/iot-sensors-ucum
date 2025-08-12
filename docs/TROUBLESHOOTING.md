# Guide de résolution - Messages MQTT tronqués

## 🔍 Diagnostic du problème

### Symptômes observés
- Messages JSON incomplets dans MQTT
- Troncature après le champ `"vali` (validation)
- Perte de données dans InfluxDB/Grafana

### Cause principale
La taille du buffer `StaticJsonDocument` sur Arduino est insuffisante pour contenir le message JSON complet avec toutes les métadonnées UCUM.

## 🔧 Solutions par ordre de préférence

### Solution 1 : Augmentation des buffers (RECOMMANDÉE)

Les buffers ont été augmentés dans le code principal :
- `sendMeasurementUCUM()` : 350 → **512 bytes**
- `sendKeepalive()` : 500 → **1024 bytes**

```cpp
// Dans iot-sensors-ucum.ino
StaticJsonDocument<512> doc;  // Au lieu de 350
StaticJsonDocument<1024> doc; // Au lieu de 500
```

### Solution 2 : Format compact (SI PROBLÈME PERSISTE)

Si la solution 1 ne suffit pas, utiliser le format compact :

```cpp
// Inclure le fichier d'optimisation
#include "message_optimization.h"

// Dans le setup(), tester les tailles
void setup() {
  // ... code existant ...
  testMessageSizes(); // Affiche les tailles des messages
}

// Remplacer les appels de fonction
void readAndSendIfChanged() {
  // ... lecture des capteurs ...
  
  // Remplacer sendMeasurementUCUM par sendMeasurementUCUMCompact
  if (abs(temperature - lastTemperature) >= tempConfig.threshold) {
    sendMeasurementUCUMCompact("temperature", temperature, tempConfig);
    lastTemperature = temperature;
  }
  // ... idem pour autres capteurs
}

void loop() {
  // ... code existant ...
  
  // Remplacer sendKeepalive par sendKeepaliveCompact
  if (currentTime - lastKeepalive >= KEEPALIVE_INTERVAL) {
    sendKeepaliveCompact();
    lastKeepalive = currentTime;
  }
}
```

### Solution 3 : Configuration Telegraf dual-format

Si vous utilisez le format compact, remplacer la configuration Telegraf :

```bash
# Sauvegarder l'ancienne config
mv telegraf/telegraf.conf telegraf/telegraf-original.conf

# Utiliser la nouvelle config dual-format
mv telegraf/telegraf-dual-format.conf telegraf/telegraf.conf

# Redémarrer Telegraf
docker-compose restart telegraf
```

## 📊 Comparaison des formats

### Format normal (UCUM complet)
```json
{
  "device_id": "mkr1010_AA1D11EE",
  "sensor_type": "illuminance", 
  "value": 45.80645,
  "timestamp": 1755016534,
  "location": "unknown",
  "measurement_type": "sensor_reading",
  "ucum": {
    "code": "lx",
    "display": "lx", 
    "common_name": "Illuminance",
    "quantity_type": "illuminance"
  },
  "validation": {
    "min_value": 0.0,
    "max_value": 100000.0,
    "in_range": true
  }
}
```
**Taille : ~380 caractères**

### Format compact
```json
{
  "id": "mkr1010_AA1D11EE",
  "type": "illuminance",
  "val": 45.80645,
  "ts": 1755016534,
  "loc": "unknown",
  "unit": "lx",
  "sym": "lx",
  "ok": true
}
```
**Taille : ~120 caractères**

## 🧪 Tests et validation

### Test des tailles de messages

Ajoutez dans le `setup()` Arduino :

```cpp
void setup() {
  // ... code existant ...
  
  if (DEBUG_SERIAL) {
    testMessageSizes(); // Fonction dans message_optimization.h
  }
}
```

### Monitoring MQTT en temps réel

```bash
# Surveiller tous les messages
mosquitto_sub -h localhost -p 1883 -u mqtt_user -P mqtt_password -t "sensors/+/+" -v

# Surveiller uniquement un device
mosquitto_sub -h localhost -p 1883 -u mqtt_user -P mqtt_password -t "sensors/mkr1010_AA1D11EE/+" -v
```

### Vérification dans InfluxDB

```bash
# Interface web InfluxDB
open http://localhost:8086

# Query Flux pour vérifier les données
from(bucket: "sensor-data")
  |> range(start: -10m)
  |> filter(fn: (r) => r.device_id == "mkr1010_AA1D11EE")
  |> count()
```

## ⚙️ Optimisations avancées

### Réduction sélective des champs

Pour garder UCUM mais réduire la taille :

```cpp
// Supprimer validation du message normal
// JsonObject validation = doc.createNestedObject("validation"); // COMMENTER
// validation["min_value"] = config.min_value;                   // COMMENTER  
// validation["max_value"] = config.max_value;                   // COMMENTER
// validation["in_range"] = ...;                                 // COMMENTER

// Réduire les noms de champs UCUM
ucum["c"] = config.ucum_code;        // "code" -> "c"
ucum["d"] = config.ucum_display;     // "display" -> "d"  
ucum["n"] = config.common_name;      // "common_name" -> "n"
ucum["q"] = config.quantity_type;    // "quantity_type" -> "q"
```

### Envoi sélectif des métadonnées

```cpp
// Envoyer métadonnées UCUM complètes seulement au premier message
static bool first_message = true;
if (first_message) {
  // Format complet avec UCUM
  first_message = false;
} else {
  // Format minimal sans métadonnées
}
```

## 🔄 Migration step-by-step

1. **Augmenter buffers** (déjà fait)
2. **Tester** avec monitoring MQTT
3. **Si toujours tronqué** → Implémenter format compact
4. **Modifier Telegraf** → Config dual-format
5. **Valider** données dans Grafana

## 📈 Impact sur Grafana

Les dashboards Grafana continueront de fonctionner car :
- Telegraf normalise les formats
- Les tags UCUM sont préservés  
- Les requêtes Flux restent identiques
- Seuls les noms de champs internes changent

## 🔍 Debug avancé

### Mémoire Arduino

```cpp
void printMemoryUsage() {
  Serial.print("Mémoire libre: ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" bytes");
}
```

### Buffer overflow detection

```cpp
StaticJsonDocument<512> doc;
DeserializationError error = deserializeJson(doc, jsonString);
if (error) {
  Serial.print("JSON error: ");
  Serial.println(error.c_str());
}
```

Cette approche garantit la compatibilité UCUM tout en résolvant les problèmes de troncature.
