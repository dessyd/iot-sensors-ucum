# Version 1.8 - Profils de fréquence prédéfinis

## 🎯 Nouvelle fonctionnalité : Configuration ultra-simple via profils

### **Problème résolu :**
- Configuration manuelle des intervalles complexe pour les utilisateurs
- Besoin de connaître les bonnes valeurs pour différents cas d'usage
- Risque d'erreurs dans les calculs d'intervalles

### **Solution implémentée :**

#### **1. Configuration en une seule ligne**
```cpp
// Super simple : Juste une valeur !
#define MEASUREMENT_FREQUENCY MEDIUM
```

**Valeurs possibles :**
- **`HIGH`** : Monitoring temps réel
- **`MEDIUM`** : Configuration équilibrée (par défaut)
- **`LOW`** : Économie d'énergie

## 📊 Profils de fréquence disponibles

### **🔥 HIGH - Temps réel**
```cpp
#define MEASUREMENT_FREQUENCY HIGH
```
- **Mesures** : Toutes les 10 secondes
- **Keepalive** : Toutes les 1 minute (6 × mesure)
- **Usage** : Monitoring critique, laboratoire, démo
- **Détection offline** : 2 minutes

### **⚖️ MEDIUM - Équilibré (par défaut)**
```cpp
#define MEASUREMENT_FREQUENCY MEDIUM
```
- **Mesures** : Toutes les 30 secondes
- **Keepalive** : Toutes les 5 minutes (10 × mesure)
- **Usage** : Monitoring standard, bureau, maison
- **Détection offline** : 10 minutes

### **🔋 LOW - Économe en énergie**
```cpp
#define MEASUREMENT_FREQUENCY LOW
```
- **Mesures** : Toutes les 1 minute
- **Keepalive** : Toutes les 15 minutes (15 × mesure)
- **Usage** : Monitoring longue durée, extérieur, autonomie
- **Détection offline** : 30 minutes

## 🛡️ Robustesse et fallback

### **Gestion automatique des erreurs :**
```cpp
// Toutes ces configurations donnent MEDIUM :
#define MEASUREMENT_FREQUENCY MEDIUM     // ✅ Standard
#define MEASUREMENT_FREQUENCY INVALID    // ✅ Fallback → MEDIUM
// Non défini                            // ✅ Fallback → MEDIUM
```

### **Comportement de fallback :**
- **Si `MEASUREMENT_FREQUENCY` non défini** → MEDIUM
- **Si valeur invalide** (ni LOW, ni MEDIUM, ni HIGH) → MEDIUM
- **Logs de vérification** : Affichage du profil sélectionné

## 📱 Nouveaux logs de démarrage

### **Exemple avec profil MEDIUM :**
```text
=== Arduino IoT Sensors - Standard UCUM ===
Version: 1.8 (Frequency Profiles)
=== Configuration fréquence ===
Fréquence: MEDIUM (équilibré)
Mesure: 30s
Keepalive: 300s (10x mesure)
=== Corrections de calibration ===
Température: -2.5 °C
```

### **Exemple avec profil HIGH :**
```text
=== Configuration fréquence ===
Fréquence: HIGH (temps réel)
Mesure: 10s
Keepalive: 60s (6x mesure)
```

### **Exemple avec profil LOW :**
```text
=== Configuration fréquence ===
Fréquence: LOW (économe en énergie)
Mesure: 60s
Keepalive: 900s (15x mesure)
```

## 🔧 Guide de sélection du profil

### **Choisir HIGH quand :**
- ✅ Monitoring critique (serveur, processus industriel)
- ✅ Démonstration temps réel
- ✅ Debugging et développement
- ✅ Laboratoire et expérimentation
- ❌ Alimentation limitée

### **Choisir MEDIUM quand :**
- ✅ Monitoring domestique ou bureau
- ✅ Applications standard IoT
- ✅ Bon compromis performance/énergie
- ✅ Configuration par défaut recommandée
- ✅ La plupart des cas d'usage

### **Choisir LOW quand :**
- ✅ Autonomie importante (batterie, solaire)
- ✅ Monitoring longue durée (environnemental)
- ✅ Réseau limité ou coûteux
- ✅ Capteurs extérieurs isolés
- ❌ Besoin de réactivité rapide

## ⚙️ Implémentation technique

### **Système de preprocesseur intelligent :**
```cpp
// Définitions des constantes
#define LOW    1    // Économe en énergie
#define MEDIUM 2    // Équilibré (défaut)
#define HIGH   3    // Temps réel

// Logique conditionnelle automatique
#if defined(MEASUREMENT_FREQUENCY) && (MEASUREMENT_FREQUENCY == HIGH)
  #define MEASUREMENT_INTERVAL 10000      // 10 secondes
  #define KEEPALIVE_MULTIPLIER 6          // 6 × 10s = 1 minute
#elif defined(MEASUREMENT_FREQUENCY) && (MEASUREMENT_FREQUENCY == LOW)
  #define MEASUREMENT_INTERVAL 60000      // 60 secondes
  #define KEEPALIVE_MULTIPLIER 15         // 15 × 1min = 15 minutes
#else
  // MEDIUM par défaut (fallback)
  #define MEASUREMENT_INTERVAL 30000      // 30 secondes
  #define KEEPALIVE_MULTIPLIER 10         // 10 × 30s = 5 minutes
#endif
```

### **Avantages de cette approche :**
- ✅ **Calcul à la compilation** : Aucun impact performance
- ✅ **Fallback robuste** : Toujours une config valide
- ✅ **Extensible** : Facile d'ajouter ULTRA_HIGH, ULTRA_LOW, etc.
- ✅ **Préprocesseur** : Optimisation maximale du code

## 🔄 Migration depuis v1.7

### **Migration automatique :**
1. **Aucune action requise** si vous gardez la config par défaut
2. **Vérification** : Les logs montrent "MEDIUM (équilibré)"
3. **Personnalisation** : Changer simplement `MEASUREMENT_FREQUENCY`

### **Exemples de migration :**

#### **Si vous aviez v1.7 :**
```cpp
// v1.7 - Configuration manuelle
#define MEASUREMENT_INTERVAL 10000
#define KEEPALIVE_MULTIPLIER 6
```

#### **Équivalent v1.8 :**
```cpp
// v1.8 - Configuration simplifiée
#define MEASUREMENT_FREQUENCY HIGH    // Même résultat !
```

## 🚀 Cas d'usage typiques

### **Déploiement domestique :**
```cpp
#define MEASUREMENT_FREQUENCY MEDIUM    // Parfait pour la maison
```

### **Monitoring serveur :**
```cpp
#define MEASUREMENT_FREQUENCY HIGH     // Réactivité maximale
```

### **Station météo autonome :**
```cpp
#define MEASUREMENT_FREQUENCY LOW      // Économie batterie
```

### **Prototype/développement :**
```cpp
#define MEASUREMENT_FREQUENCY HIGH     // Feedback rapide
```

## 🏆 Avantages de la v1.8

- ✅ **Ultra-simple** : Une seule ligne de configuration
- ✅ **Intuitif** : LOW/MEDIUM/HIGH compréhensible par tous
- ✅ **Robuste** : Fallback automatique vers MEDIUM
- ✅ **Optimisé** : Profils pré-calculés et testés
- ✅ **Évolutif** : Facile d'ajouter de nouveaux profils
- ✅ **Compatible** : Fonctionne avec toute l'infrastructure

**Configuration en 3 mots = Simplicité maximale !** 🎯

---

**Version 1.8 - Dominique Dessy - Août 2025**
