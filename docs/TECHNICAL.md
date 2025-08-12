# Documentation technique - IoT Sensors UCUM

## Architecture détaillée

### Flux de données

1. **Arduino MKR1010** lit les capteurs ENV shield
2. **Formatage UCUM** : Application des codes standards
3. **Transmission MQTT** : Envoi vers broker local/distant
4. **Telegraf** : Collecte, enrichissement et conversion
5. **InfluxDB** : Stockage time-series avec tags UCUM
6. **Grafana** : Visualisation et alerting

### Codes UCUM implémentés

| Code | Nom complet | Symbole | Conversion SI |
|------|-------------|---------|---------------|
| `Cel` | degree Celsius | °C | +273.15 → K |
| `%` | percent | % | /100 → 1 |
| `hPa` | hectopascal | hPa | ×100 → Pa |
| `lx` | lux | lx | = lx (SI) |

### Configuration réseau

- **MQTT Port** : 1883 (non-TLS), 8883 (TLS)
- **Grafana Port** : 3000
- **InfluxDB Port** : 8086
- **WebSocket MQTT** : 9001

### Intervalles de mesure

- **Measurement** : 30 secondes (envoi si changement)
- **Keepalive** : 5 minutes (envoi systématique)
- **Offline timeout** : 10 minutes (2 × keepalive)

## Procédures de déploiement

### Environnement de développement

```bash
# Clone et setup
git clone <repo> iot-sensors-ucum
cd iot-sensors-ucum
./scripts/deploy.sh
```

### Environnement de production

1. **Sécurisation** : TLS, certificats, firewall
2. **Monitoring** : Logs centralisés, métriques
3. **Backup** : Stratégie de sauvegarde InfluxDB
4. **Scaling** : Load balancer, cluster InfluxDB

### Ajout de nouveaux sites

1. Configuration Arduino identique
2. Modification `SECRET_DEVICE_LOCATION`
3. ID unique automatique via ECCX08
4. Dashboards Grafana adaptés automatiquement

## Maintenance et monitoring

### Surveillance système

- **Disk usage** : InfluxDB data retention
- **Network** : MQTT connections, latency
- **Performance** : Query response time Grafana
- **Security** : Failed authentication attempts

### Scripts utiles

```bash
# Status des services
docker-compose ps

# Monitoring en temps réel
docker-compose logs -f

# Backup InfluxDB
./scripts/backup-influxdb.sh

# Test connectivité Arduino
./scripts/test-mqtt-connectivity.sh
```

### Alertes à configurer

- Service Docker down
- Disk space > 85%
- MQTT broker unreachable
- InfluxDB write errors
- Device offline > 10 min

## Sécurité

### Niveau développement

- Authentification MQTT basique
- Tokens InfluxDB non-rotatifs
- HTTP non-chiffré

### Niveau production

- **TLS partout** : MQTT, HTTP, InfluxDB
- **Certificats PKI** : Authentification devices
- **RBAC** : Rôles et permissions Grafana
- **Network segmentation** : VLANs IoT séparés
- **Log monitoring** : SIEM intégration

## Performance

### Métriques cibles

- **Latency** : < 5s Arduino → Grafana
- **Throughput** : 1000 messages/sec MQTT
- **Storage** : 1GB/mois par device
- **Availability** : 99.9% uptime

### Optimisations

- **InfluxDB** : Downsampling, retention policies
- **Telegraf** : Batch processing, buffering
- **MQTT** : QoS 1, retain messages
- **Grafana** : Query caching, variables

## Extensions possibles

### Nouveaux capteurs

- **CO2** : Code UCUM `[ppm]`
- **PM2.5** : Code UCUM `mg/m3`
- **Bruit** : Code UCUM `dB`
- **UV** : Code UCUM personnalisé

### Intégrations

- **Cloud** : AWS IoT, Azure IoT Hub
- **Mobile** : App React Native
- **API** : REST endpoints pour tiers
- **ML** : Anomaly detection InfluxDB

### Sources additionnelles

- **SNMP** : Équipements réseau
- **ModBus** : Automates industriels
- **OPC-UA** : Systèmes SCADA
- **APIs** : Services météo, capteurs IP
