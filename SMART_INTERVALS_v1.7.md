# Version 1.7 - Intervalles intelligents

## 🎯 Amélioration : Configuration intelligente des intervalles

### **Problème résolu :**
- Configuration manuelle des intervalles source d'erreurs
- Risque d'incohérence entre MEASUREMENT_INTERVAL et KEEPALIVE_INTERVAL
- Difficulté à maintenir la relation Int2 > n × Int1

### **Solution implémentée :**

#### **1. Configuration basée sur un multiplicateur**
```cpp
// Avant v1.7 (configuration manuelle)
#define MEASUREMENT_INTERVAL 30000    // 30 secondes
#define KEEPALIVE_INTERVAL 300000     // 5 minutes (à calculer manuellement)

// Après v1.7 (configuration intelligente)
#define MEASUREMENT_INTERVAL 30000      // 30 secondes (Int1)
#define KEEPALIVE_MULTIPLIER 10          // Keepalive = MEASUREMENT × MULTIPLIER
#define KEEPALIVE_INTERVAL (MEASUREMENT_INTERVAL * KEEPALIVE_MULTIPLIER)  // Auto: 5 minutes
```

#### **2. Avantages de cette approche :**
- ✅ **Cohérence garantie** : KEEPALIVE toujours multiple de MEASUREMENT
- ✅ **Configuration simple** : Un seul paramètre à ajuster
- ✅ **Calcul automatique** : Plus d'erreurs de multiplication
- ✅ **Lisibilité** : Relation claire entre les intervalles

## 🔧 Configuration des intervalles

### **Exemples de configurations courantes :**

#### **1. Monitoring haute fréquence**
```cpp
#define MEASUREMENT_INTERVAL 10000      // 10 secondes
#define KEEPALIVE_MULTIPLIER 6          // 6 × 10s = 1 minute
// Résultat: Mesure toutes les 10s, Keepalive toutes les 1min
```

#### **2. Configuration équilibrée (par défaut)**
```cpp
#define MEASUREMENT_INTERVAL 30000      // 30 secondes  
#define KEEPALIVE_MULTIPLIER 10         // 10 × 30s = 5 minutes
// Résultat: Mesure toutes les 30s, Keepalive toutes les 5min
```

#### **3. Monitoring économe en énergie**
```cpp
#define MEASUREMENT_INTERVAL 60000      // 1 minute
#define KEEPALIVE_MULTIPLIER 10         // 10 × 1min = 10 minutes  
// Résultat: Mesure toutes les 1min, Keepalive toutes les 10min
```

#### **4. Monitoring longue durée**
```cpp
#define MEASUREMENT_INTERVAL 300000     // 5 minutes
#define KEEPALIVE_MULTIPLIER 6          // 6 × 5min = 30 minutes
// Résultat: Mesure toutes les 5min, Keepalive toutes les 30min
```

## 📊 Logs de vérification

### **Nouveaux logs au démarrage :**
```text
=== Arduino IoT Sensors - Standard UCUM ===
Version: 1.7 (Smart Intervals)
=== Configuration intervalles ===
Mesure: 30s
Keepalive: 300s (10x mesure)
=== Corrections de calibration ===
Température: -2.5 °C
Humidité: -0.0 %RH
Pression: -0.0 hPa
Luminosité: -0.0 lx
```

### **Vérification de cohérence :**
- **Mesure** : Fréquence des lectures individuelles
- **Keepalive** : Fréquence des status complets
- **Multiplicateur** : Relation claire affichée

## ⚙️ Considérations de design

### **Choix du multiplicateur :**

#### **KEEPALIVE_MULTIPLIER recommandés :**
- **6-12** : Pour monitoring temps réel
- **10-20** : Pour applications standard  
- **20-60** : Pour systèmes économes en énergie

#### **Limites pratiques :**
```cpp
// Multiplicateur trop faible (non recommandé)
#define KEEPALIVE_MULTIPLIER 2    // Keepalive trop fréquent vs mesures

// Multiplicateur optimal
#define KEEPALIVE_MULTIPLIER 10   // Bon équilibre

// Multiplicateur élevé (économie d'énergie)
#define KEEPALIVE_MULTIPLIER 60   // 1 keepalive pour 60 mesures
```

### **Impact sur le monitoring :**

#### **Détection offline :**
```text
Timeout de détection = 2 × KEEPALIVE_INTERVAL

Exemples:
- KEEPALIVE 1min → Offline après 2min
- KEEPALIVE 5min → Offline après 10min  
- KEEPALIVE 10min → Offline après 20min
```

## 🔄 Migration depuis v1.6

### **Étapes automatiques :**
1. **Aucune action requise** si vous gardez les valeurs par défaut
2. **Vérification** : Les logs montrent les intervalles calculés
3. **Ajustement** : Modifier seulement `KEEPALIVE_MULTIPLIER` si besoin

### **Exemples de migration :**

#### **Si vous aviez :**
```cpp
// v1.6
#define MEASUREMENT_INTERVAL 30000
#define KEEPALIVE_INTERVAL 600000     // 10 minutes
```

#### **Équivalent v1.7 :**
```cpp
// v1.7  
#define MEASUREMENT_INTERVAL 30000    // Inchangé
#define KEEPALIVE_MULTIPLIER 20       // 20 × 30s = 600s = 10min
```

## 🏆 Avantages de la v1.7

- ✅ **Configuration simplifiée** : Un paramètre au lieu de deux
- ✅ **Cohérence garantie** : Pas d'erreurs de calcul manuel
- ✅ **Flexibilité** : Changement rapide des intervalles
- ✅ **Traçabilité** : Logs montrent la relation entre intervalles
- ✅ **Compatibilité** : Fonctionne avec toute l'infrastructure existante

### **Cas d'usage optimaux :**

| Type de monitoring | MEASUREMENT_INTERVAL | KEEPALIVE_MULTIPLIER | Résultat |
|-------------------|---------------------|---------------------|----------|
| **Temps réel** | 10s | 6 | Mesure: 10s, Status: 1min |
| **Standard** | 30s | 10 | Mesure: 30s, Status: 5min |
| **Économe** | 60s | 15 | Mesure: 1min, Status: 15min |
| **Longue durée** | 300s | 12 | Mesure: 5min, Status: 1h |

**Configuration intelligente = Monitoring robuste !** 📊

---

**Version 1.7 - Dominique Dessy - Août 2025**
