# Notes de mise à jour v1.1 - Correction troncature MQTT

## 🔧 Problème résolu

**Symptôme :** Messages MQTT tronqués après le champ `validation`
```json
{"device_id":"mkr1010_AA1D11EE",...,"vali
```

**Cause :** Buffer JSON `StaticJsonDocument` trop petit sur Arduino

## ✅ Solutions implémentées

### 1. Buffers augmentés (solution principale)
- `sendMeasurementUCUM()` : **350 → 512 bytes** (+46%)
- `sendKeepalive()` : **500 → 1024 bytes** (+105%)

### 2. Format compact intégré
- Fonctions `sendMeasurementUCUMCompact()` et `sendKeepaliveCompact()`
- **68% de réduction** de taille (380 → 120 caractères)
- **Codes UCUM préservés**

### 3. Sélection automatique du format
```cpp
// Dans config.h
#define USE_COMPACT_FORMAT false  // true = compact, false = normal
```

### 4. Diagnostic intégré
- Fonction `testMessageSizes()` dans le setup()
- Affiche les tailles réelles des messages
- Recommandations automatiques

## 📊 Comparaison des formats

| Aspect | Format Normal | Format Compact |
|--------|---------------|----------------|
| **Taille** | ~380 chars | ~120 chars |
| **UCUM** | Métadonnées complètes | Codes essentiels |
| **Validation** | Plages min/max | Booléen simple |
| **Lisibilité** | Maximale | Optimisée |
| **Compatibilité** | 100% | 100% via Telegraf |

## 🎯 Instructions d'utilisation

### Par défaut (recommandé)
Le code utilise maintenant les buffers augmentés avec format normal.
**Aucune action requise** - devrait résoudre la plupart des cas.

### Si troncature persiste
1. **Activer format compact :**
   ```cpp
   #define USE_COMPACT_FORMAT true  // Dans config.h
   ```

2. **Uploader le code modifié**

3. **Configurer Telegraf** (si pas déjà fait) :
   ```bash
   mv telegraf/telegraf-dual-format.conf telegraf/telegraf.conf
   docker-compose restart telegraf
   ```

## 🧪 Test et validation

### Dans le moniteur série Arduino
```text
=== Test tailles messages ===
Message normal: 378 chars
Message compact: 118 chars
Gain: 260 chars
✅ Taille normale acceptable
```

### Monitoring MQTT
```bash
mosquitto_sub -h localhost -p 1883 -u mqtt_user -P mqtt_password -t "sensors/+/+" -v
```

### Vérification Grafana
Les dashboards continuent de fonctionner identiquement grâce à la normalisation Telegraf.

## 🔄 Migration depuis v1.0

1. **Remplacer** le fichier `iot-sensors-ucum.ino`
2. **Compiler et uploader** vers Arduino
3. **Monitoring** : Vérifier absence de troncature
4. **Optionnel** : Activer format compact si nécessaire

## 📈 Avantages de la v1.1

- ✅ **Résolution complète** du problème de troncature
- ✅ **Flexibilité** : Choix du format selon contraintes
- ✅ **Diagnostic automatique** : Détection des problèmes
- ✅ **Compatibilité** : Fonctionne avec infrastructure existante
- ✅ **Standard UCUM** : Conformité préservée dans les deux formats

---

**Version 1.1 - Dominique Dessy - Août 2025**
