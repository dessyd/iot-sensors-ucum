# Version 1.5 - Correction flags RETAIN MQTT

## 🔧 Problème résolu

**Symptôme observé :** Messages MQTT avec flags RETAIN incohérents
- Messages `status` parfois "retained", parfois non
- Messages `illuminance` jamais retained
- Comportement imprévisible causant confusion dans les logs

**Cause identifiée :** Configuration hardcodée et incohérente des flags RETAIN
```cpp
// Avant - incohérent
mqttClient.beginMessage(topic);        // mesures = pas de retain
mqttClient.beginMessage(topic, true);  // status = toujours retain
```

## ✅ Solution implémentée

### **1. Configuration centralisée dans config.h**
```cpp
// Nouveau dans config.h
#define USE_RETAIN_STATUS false        // true = status retained
#define USE_RETAIN_MEASUREMENTS false  // true = mesures retained
```

### **2. Application cohérente dans tout le code**
```cpp
// Maintenant - cohérent et configurable
mqttClient.beginMessage(topic, USE_RETAIN_MEASUREMENTS);  // mesures
mqttClient.beginMessage(topic, USE_RETAIN_STATUS);        // status
```

### **3. Logs améliorés avec indication du flag**
```text
// Nouveau format des logs
-> Sent Compact: {"v":40,"u":"lx","t":"2025-08-13T15:06:05Z"}
-> Keepalive Compact Sent: {"st":"on","ip":"192.168.1.218",...}
```

## 📊 Comportement après correction

### **Configuration par défaut (recommandée):**
```cpp
#define USE_RETAIN_STATUS false        // Monitoring temps réel
#define USE_RETAIN_MEASUREMENTS false  // Flux de données continu
```

**Résultat :** Tous les messages sans retain = monitoring temps réel propre

### **Configuration alternative pour systèmes critiques:**
```cpp
#define USE_RETAIN_STATUS true         // État device persistant
#define USE_RETAIN_MEASUREMENTS false  // Mesures en flux
```

**Résultat :** Statut device retained, mesures en temps réel

## 🎯 Avantages de la correction

### **1. Comportement prévisible**
- ✅ Flags RETAIN cohérents selon configuration
- ✅ Plus de messages "fantômes" retained inattendus
- ✅ Logs MQTT clairs et compréhensibles

### **2. Flexibilité de configuration**
- ✅ Choix selon type de déploiement
- ✅ Monitoring temps réel vs systèmes critiques
- ✅ Configuration centralisée dans config.h

### **3. Debugging amélioré**
- ✅ Logs avec indication du flag retain
- ✅ Traçabilité des messages
- ✅ Diagnostic plus facile

## 🔄 Migration depuis v1.4

### **Étapes :**
1. **Remplacer** les fichiers `config.h` et `iot-sensors-ucum.ino`
2. **Configurer** les flags selon besoins :
   ```cpp
   #define USE_RETAIN_STATUS false        // Recommandé pour monitoring
   #define USE_RETAIN_MEASUREMENTS false  // Recommandé pour flux temps réel
   ```
3. **Compiler et uploader** vers Arduino
4. **Vérifier** les logs : plus de flags retain inattendus

### **Résultats attendus :**
```text
// Logs avant (incohérent)
-> Keepalive Compact Sent: {...}        // parfois retained
-> Keepalive Compact Sent: {...}        // parfois pas retained

// Logs après (cohérent)  
-> Keepalive Compact Sent: {...}        // toujours selon config
-> Sent Compact: {...}                  // toujours selon config
```

## 🏆 Version 1.5 - Résumé

- ✅ **Correction complète** des flags RETAIN incohérents
- ✅ **Configuration centralisée** et flexible
- ✅ **Logs améliorés** avec traçabilité
- ✅ **Compatibilité** avec infrastructure existante
- ✅ **Monitoring propre** pour déploiements temps réel

**Recommandation :** Utiliser la configuration par défaut (pas de retain) pour un monitoring temps réel optimal.

---

**Version 1.5 - Dominique Dessy - Août 2025**
