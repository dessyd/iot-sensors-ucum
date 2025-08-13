# Version 1.6 - Calibration des capteurs

## 🎯 Nouvelle fonctionnalité : Calibration des capteurs

### **Problème résolu :**
- Capteurs avec biais systématique (ex: température +2.5°C trop élevée)
- Besoin de correction sans modification hardware
- Calibration centralisée et configurable

### **Solution implémentée :**

#### **1. Configuration dans config.h**
```cpp
// Corrections de calibration des capteurs (valeurs à soustraire aux lectures)
#define TEMPERATURE_OFFSET 2.5    // °C - Correction température (valeur à soustraire)
#define HUMIDITY_OFFSET 0.0       // %RH - Correction humidité  
#define PRESSURE_OFFSET 0.0       // hPa - Correction pression
#define ILLUMINANCE_OFFSET 0.0    // lx - Correction luminosité
```

#### **2. Application automatique dans le code**
```cpp
// Avant (lecture brute)
float temperature = ENV.readTemperature();

// Après (lecture corrigée)
float temperature = ENV.readTemperature() - TEMPERATURE_OFFSET;
```

## 🔧 Configuration de la calibration

### **Comment déterminer les offsets :**

#### **1. Méthode de référence**
1. **Placer l'Arduino** à côté d'un thermomètre de référence
2. **Attendre stabilisation** (15-20 minutes)
3. **Relever les valeurs** :
   - Référence : 22.0°C
   - Arduino : 24.5°C
   - **Offset = 24.5 - 22.0 = 2.5°C**

#### **2. Exemple de configuration**
```cpp
// Capteur lit 2.5°C trop élevé
#define TEMPERATURE_OFFSET 2.5

// Capteur lit 1.2% trop bas → offset négatif
#define HUMIDITY_OFFSET -1.2

// Capteur précis
#define PRESSURE_OFFSET 0.0
#define ILLUMINANCE_OFFSET 0.0
```

### **Valeurs positives vs négatives :**
- **OFFSET positif** : Capteur lit trop **élevé** → soustraction
- **OFFSET négatif** : Capteur lit trop **bas** → addition (soustraction d'une valeur négative)

## 📊 Application dans tout le système

### **Fonctions corrigées :**
1. **`readAndSendIfChanged()`** : Mesures individuelles
2. **`sendKeepalive()`** : Status complet  
3. **`sendKeepaliveCompact()`** : Status compact

### **Cohérence garantie :**
- ✅ Toutes les mesures utilisent les mêmes corrections
- ✅ Valeurs identiques dans mesures et keepalive
- ✅ Pas de divergence entre différents messages

## 🧪 Test et validation

### **Messages de démarrage :**
```text
=== Arduino IoT Sensors - Standard UCUM ===
Version: 1.6 (Sensor Calibration)
=== Corrections de calibration ===
Température: -2.5 °C
Humidité: -0.0 %RH
Pression: -0.0 hPa
Luminosité: -0.0 lx
```

### **Vérification des corrections :**
```cpp
// Test simple dans le code
float rawTemp = ENV.readTemperature();
float correctedTemp = rawTemp - TEMPERATURE_OFFSET;

Serial.println("Température brute: " + String(rawTemp) + "°C");
Serial.println("Température corrigée: " + String(correctedTemp) + "°C");
```

## ⚙️ Cas d'usage avancés

### **Calibration multi-points (à implémenter si nécessaire) :**
```cpp
// Pour corrections non-linéaires (exemple avancé)
float correctTemperature(float raw) {
  // Correction linéaire simple (actuelle)
  return raw - TEMPERATURE_OFFSET;
  
  // Correction polynomial (exemple avancé)
  // return raw + (A * raw * raw) + (B * raw) + C;
}
```

### **Calibration temporelle (compensation dérive) :**
```cpp
// Drift compensation basé sur l'uptime (exemple)
float tempDrift = (millis() / 1000 / 3600) * 0.001; // 0.001°C/heure
float correctedTemp = rawTemp - TEMPERATURE_OFFSET - tempDrift;
```

## 🔄 Migration et utilisation

### **Étapes de calibration :**

1. **Installer v1.6** avec offsets à 0.0
2. **Mesurer les biais** par rapport à références
3. **Configurer les offsets** dans config.h
4. **Recompiler et uploader**
5. **Vérifier** les corrections dans les logs

### **Exemple pratique :**
```cpp
// Situation : Capteur Arduino lit 24.8°C, thermomètre référence lit 22.3°C
// Calcul : 24.8 - 22.3 = 2.5°C d'erreur
#define TEMPERATURE_OFFSET 2.5

// Résultat : Arduino affichera maintenant 22.3°C ✅
```

## 🏆 Avantages de la v1.6

- ✅ **Précision améliorée** des mesures
- ✅ **Configuration centralisée** dans config.h  
- ✅ **Application automatique** dans tout le code
- ✅ **Cohérence** entre tous les messages MQTT
- ✅ **Traçabilité** des corrections dans les logs
- ✅ **Flexibilité** : Corrections par capteur

**Note :** Cette approche corrige les biais systématiques. Pour des capteurs défaillants ou avec bruit important, remplacement hardware recommandé.

---

**Version 1.6 - Dominique Dessy - Août 2025**
