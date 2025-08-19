# Configuration Telegraf - Guide Détaillé

**Version 2.2.0** - Guide complet de configuration Telegraf pour IoT Sensors UCUM

## 📊 Vue d'ensemble

Telegraf sert de collecteur de données central dans l'architecture IoT Sensors, transformant les messages MQTT des capteurs Arduino et les données Feinstaub en format unifié pour InfluxDB.

### Architecture des données

```text
Arduino MKR1010      Capteur Feinstaub
     |                      |
     v                      v
   MQTT                InfluxDB v1
     |                      |
     v                      v
      Telegraf (unificateur)
            |
            v
       InfluxDB v2
            |
            v
        Grafana
```

## ⚙️ Configuration principale

### Agent global

```toml
[agent]
  interval = "10s"              # Collecte toutes les 10 secondes
  round_interval = true         # Arrondi des timestamps
  metric_batch_size = 1000      # Taille batch pour performance
  metric_buffer_limit = 10000   # Buffer mémoire
  collection_jitter = "0s"      # Pas de jitter pour IoT
  flush_interval = "10s"        # Envoi immédiat vers InfluxDB
  flush_jitter = "0s"           # Flush déterministe
  precision = ""                # Précision nanoseconde par défaut
  hostname = ""                 # Pas de hostname dans les tags
  omit_hostname = false         # Garder hostname pour debug
  debug = true                  # Mode debug activé
```

### Optimisations performance

- **Interval 10s** : Synchronisé avec fréquence Arduino MEDIUM
- **Buffer 10000** : Gestion pics de charge temporaires
- **Flush 10s** : Latence minimale vers InfluxDB
- **Debug activé** : Traçabilité complète des transformations

## 📡 Collecte MQTT - Arduino MKR1010

### Input MQTT Consumer

```toml
[[inputs.mqtt_consumer]]
  servers = ["tcp://192.168.1.15:1883"]
  topics = ["sensors/+/temperature", "sensors/+/humidity", "sensors/+/pressure", "sensors/+/illuminance"]
  data_format = "json"
  
  # Configuration format Arduino v2.0
  json_string_fields = ["u", "t"]
  
  # Extraction automatique tags depuis topic
  [[inputs.mqtt_consumer.topic_parsing]]
    topic = "sensors/+/+"
    tags = "sensors/device_id/sensor_type"
```

### Topics collectés

| Topic Pattern | Capteur | Format attendu |
|---------------|---------|----------------|
| `sensors/+/temperature` | Température | `{"v": 23.5, "u": "Cel", "t": "2025-08-19T10:30:00Z"}` |
| `sensors/+/humidity` | Humidité | `{"v": 65.2, "u": "%", "t": "2025-08-19T10:30:00Z"}` |
| `sensors/+/pressure` | Pression | `{"v": 1013.25, "u": "hPa", "t": "2025-08-19T10:30:00Z"}` |
| `sensors/+/illuminance` | Luminosité | `{"v": 350.0, "u": "lx", "t": "2025-08-19T10:30:00Z"}` |

### Topics ignorés

- `sensors/+/status` : Messages de statut Arduino
- `sensors/+/LWT` : Last Will Testament
- Tous autres patterns non listés

## 📊 Collecte InfluxDB v1 - Capteur Feinstaub

### Input InfluxDB Listener

```toml
[[inputs.influxdb_listener]]
  service_address = ":8086"     # Port d'écoute local
  write_timeout = "5s"          # Timeout écriture
  read_timeout = "5s"           # Timeout lecture
  data_format = "influx"        # Format InfluxDB line protocol
```

### Format Feinstaub

```text
feinstaub,node=esp8266-12345678 temperature=22.3,humidity=58.1,SDS_P1=15.2,SDS_P2=8.7 1692456000000000000
```

## 🔄 Processors - Transformation des données

### 1. Renommage des champs Arduino

```toml
[[processors.rename]]
  namepass = ["mqtt_consumer"]
  [[processors.rename.replace]]
    field = "v"                 # Valeur Arduino
    dest = "value"              # Champ standardisé
  [[processors.rename.replace]]
    field = "u"                 # Unité UCUM Arduino
    dest = "ucum_code"          # Code UCUM standardisé
  [[processors.rename.replace]]
    field = "t"                 # Timestamp Arduino
    dest = "sensor_timestamp"   # Timestamp capteur
```

**Résultat transformation :**

```text
Avant : {"v": 23.5, "u": "Cel", "t": "2025-08-19T10:30:00Z"}
Après : {"value": 23.5, "ucum_code": "Cel", "sensor_timestamp": "2025-08-19T10:30:00Z"}
```

### 2. Enrichissement métadonnées UCUM

```toml
[[processors.enum]]
  namepass = ["mqtt_consumer"]
  [[processors.enum.mapping]]
    field = "ucum_code"
    dest = "si_base_unit"
    [processors.enum.mapping.value_mappings]
      "Cel" = "K"              # Celsius → Kelvin (SI)
      "[degF]" = "K"           # Fahrenheit → Kelvin (SI)
      "K" = "K"                # Kelvin (déjà SI)
      "hPa" = "Pa"             # hectoPascal → Pascal (SI)
      "kPa" = "Pa"             # kiloPascal → Pascal (SI)
      "bar" = "Pa"             # bar → Pascal (SI)
      "lx" = "lx"              # lux (déjà SI)
      "%" = "1"                # pourcentage → sans dimension
```

**Mapping UCUM vers SI :**

| Code UCUM | Unité complète | Unité SI | Conversion |
|-----------|----------------|----------|------------|
| `Cel` | degré Celsius | K (Kelvin) | K = °C + 273.15 |
| `%` | pourcentage | 1 (sans dimension) | Ratio 0-1 |
| `hPa` | hectopascal | Pa (Pascal) | Pa = hPa × 100 |
| `lx` | lux | lx (déjà SI) | Aucune |

### 3. Transformation Feinstaub vers format unifié

```toml
[[processors.starlark]]
  namepass = ["feinstaub"]
  source = '''
def apply(metric):
    new_metrics = []
    node_id = metric.tags.get("node", "unknown_feinstaub")
    
    # Conversion timestamp pour compatibilité Arduino
    timestamp_str = str(metric.time).replace("T", " ").replace("Z", "")
    
    # Température feinstaub → mqtt_consumer
    if "temperature" in metric.fields:
        temp_metric = Metric("mqtt_consumer")
        # Tags unifiés
        temp_metric.tags["device_id"] = node_id
        temp_metric.tags["sensor_type"] = "temperature"
        temp_metric.tags["sensors"] = "sensors"
        temp_metric.tags["topic"] = "sensors/" + node_id + "/temperature"
        # Champs unifiés
        temp_metric.fields["value"] = metric.fields["temperature"]
        temp_metric.fields["ucum_code"] = "Cel"
        temp_metric.fields["si_base_unit"] = "K"
        temp_metric.fields["sensor_timestamp"] = timestamp_str
        temp_metric.time = metric.time
        new_metrics.append(temp_metric)
    
    # Humidité, PM10, PM2.5...
    # [Code similaire pour autres capteurs]
    
    return new_metrics
'''
```

**Transformation Feinstaub :**

| Mesure Feinstaub | Measurement | sensor_type | ucum_code |
|------------------|-------------|-------------|-----------|
| `temperature` | `mqtt_consumer` | `temperature` | `Cel` |
| `humidity` | `mqtt_consumer` | `humidity` | `%` |
| `SDS_P1` | `mqtt_consumer` | `pm10` | `ug/m3` |
| `SDS_P2` | `mqtt_consumer` | `pm25` | `ug/m3` |

## 💾 Sortie InfluxDB v2

### Configuration output

```toml
[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "MyInitialAdminToken0=="
  organization = "iot-sensors"
  bucket = "sensor-data"
  
  timeout = "5s"
  user_agent = "telegraf-iot-sensors-v2-unified-fixed"
```

### Structure des données unifiées

```text
mqtt_consumer,device_id=arduino001,sensor_type=temperature,sensors=sensors,topic=sensors/arduino001/temperature value=23.5,ucum_code="Cel",si_base_unit="K",sensor_timestamp="2025-08-19 10:30:00" 1692456000000000000
```

**Tags standardisés :**
- `device_id` : Identifiant unique capteur
- `sensor_type` : Type de mesure (temperature, humidity, pressure, illuminance, pm10, pm25)
- `sensors` : Catégorie fixe "sensors"
- `topic` : Topic MQTT reconstruit

**Fields standardisés :**
- `value` : Valeur numérique de la mesure
- `ucum_code` : Code UCUM original
- `si_base_unit` : Unité SI équivalente
- `sensor_timestamp` : Timestamp du capteur (string)

## 🔧 Monitoring et debug

### Logs Telegraf

```bash
# Logs en temps réel
docker-compose logs -f telegraf

# Filtrage par erreur
docker-compose logs telegraf | grep ERROR

# Debug transformations
docker-compose logs telegraf | grep "processors.rename"
```

### Métriques internes

```bash
# État interne Telegraf
curl -s http://localhost:9009/metrics | grep telegraf_

# Nombre de métriques par input
curl -s http://localhost:9009/metrics | grep "inputs.*metrics_gathered"

# Nombre de métriques par output
curl -s http://localhost:9009/metrics | grep "outputs.*metrics_written"
```

### Test de configuration

```bash
# Validation syntaxe configuration
docker exec telegraf telegraf --config /etc/telegraf/telegraf.conf --test

# Test processors uniquement
docker exec telegraf telegraf --config /etc/telegraf/telegraf.conf --test --input-filter mqtt_consumer
```

## 🚨 Résolution de problèmes

### Erreurs courantes

#### 1. Échec connexion MQTT

```text
ERROR connecting to [tcp://192.168.1.15:1883]: dial tcp 192.168.1.15:1883: connect: connection refused
```

**Solutions :**
- Vérifier l'adresse IP du broker MQTT
- Tester connectivité : `telnet 192.168.1.15 1883`
- Vérifier firewall et ports ouverts

#### 2. Erreur parsing JSON

```text
ERROR json: cannot unmarshal string into Go value of type float64
```

**Solutions :**
- Vérifier `json_string_fields = ["u", "t"]`
- Valider format JSON Arduino
- Tester avec `mosquitto_sub -v -t "sensors/#"`

#### 3. Processor Starlark défaillant

```text
ERROR applying processor starlark: failed to run script
```

**Solutions :**
- Vérifier syntaxe Python du script
- Ajouter gestion d'erreurs dans le script
- Tester avec des données réelles

### Performance et optimisation

#### Métriques de performance

```bash
# Latence transformation
docker-compose logs telegraf | grep "processing time"

# Throughput
docker-compose logs telegraf | grep "metrics/sec"

# Buffer utilization
curl -s http://localhost:9009/metrics | grep buffer
```

#### Optimisations recommandées

1. **Buffer sizing** selon volume de données
2. **Batch size** adapté à la latence réseau
3. **Flush interval** équilibré entre latence et charge
4. **Processeur order** : rename → enum → starlark

## 📈 Requêtes InfluxDB optimisées

### Requête température par device

```flux
from(bucket: "sensor-data")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["sensor_type"] == "temperature")
  |> filter(fn: (r) => r["device_id"] == "arduino001")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
```

### Requête multi-capteurs

```flux
from(bucket: "sensor-data")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["sensor_type"] =~ /^(temperature|humidity|pressure)$/)
  |> pivot(rowKey:["_time"], columnKey: ["sensor_type"], valueColumn: "_value")
```

### Dernières valeurs par capteur

```flux
from(bucket: "sensor-data")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "value")
  |> group(columns: ["device_id", "sensor_type"])
  |> last()
```

## 🔧 Configuration avancée

### Variables d'environnement

```bash
# Dans .env
MQTT_SERVER=tcp://192.168.1.15:1883
INFLUXDB_TOKEN=MyInitialAdminToken0==
INFLUXDB_ORG=iot-sensors
INFLUXDB_BUCKET=sensor-data
TELEGRAF_DEBUG=true
```

### Utilisation dans telegraf.conf

```toml
[[inputs.mqtt_consumer]]
  servers = ["${MQTT_SERVER}"]
  
[[outputs.influxdb_v2]]
  token = "${INFLUXDB_TOKEN}"
  organization = "${INFLUXDB_ORG}"
  bucket = "${INFLUXDB_BUCKET}"
```

### Scaling horizontal

```toml
# Répartition par device_id
[[inputs.mqtt_consumer]]
  topics = ["sensors/arduino001/+", "sensors/arduino002/+"]
  
[[inputs.mqtt_consumer]]  
  topics = ["sensors/arduino003/+", "sensors/arduino004/+"]
```

## 🎯 Bonnes pratiques

### Configuration

1. **Toujours utiliser** `namepass` dans les processors
2. **Ordonner** les processors : rename → enum → starlark
3. **Tester** chaque processor indépendamment
4. **Monitorer** les métriques internes Telegraf

### Performance

1. **Ajuster** batch_size selon volume de données
2. **Équilibrer** flush_interval vs latence
3. **Utiliser** json_string_fields pour optimiser parsing
4. **Éviter** processors trop complexes

### Sécurité

1. **Isoler** tokens dans variables d'environnement
2. **Utiliser** authentification MQTT si nécessaire
3. **Limiter** accès aux ports Telegraf
4. **Chiffrer** communications MQTT/TLS

---

**Configuration Telegraf v2.2.0** - Documentation complète  
Projet IoT Sensors UCUM - Dominique Dessy - Août 2025
