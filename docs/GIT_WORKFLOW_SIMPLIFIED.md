# Git Workflow - IoT Sensors UCUM (Simplifié)

## 🌳 Structure des branches

### Branche unique

- **`main`** : Branche unique de production et développement
  - Contient toutes les versions releases stables
  - Développement direct sur main
  - Tags de version (v2.2.3, v2.2.2, etc.)

### Workflow simplifié

```text
main (production + développement)
  │
  ├── commit direct
  ├── tag version  
  └── push origin
```

## 🔄 Processus de développement

### 1. Développement quotidien

```bash
git checkout main
git pull origin main
# Développement...
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin main
```

### 2. Release avec tag

```bash
# Après développement et test
git tag -a v2.2.4 -m "Version 2.2.4: Description"
git push origin --tags
```

## 📋 Configuration actuelle

### Branche configurée

- ✅ `main` → `origin/main` (tracking configuré)

### Remote

```text
origin: https://github.com/dessyd/iot-sensors-ucum.git
```

## 🛠️ Commandes utiles

### Vérification état

```bash
# Branche actuelle
git branch --show-current

# État repository
git status

# Historique
git log --oneline --graph
```

### Synchronisation

```bash
# Mettre à jour branche courante
git pull

# Pousser les changements
git push origin main

# Pousser les tags
git push origin --tags
```

### Création branche feature (si nécessaire)

```bash
# Nouvelle fonctionnalité complexe depuis main
git checkout main
git checkout -b feature/nouvelle-fonctionnalite
git push -u origin feature/nouvelle-fonctionnalite
# Après développement: merge via PR vers main
```

## 🎯 Bonnes pratiques

### Messages de commit

- **feat:** nouvelle fonctionnalité
- **fix:** correction de bug
- **docs:** documentation
- **style:** formatage
- **refactor:** refactoring code
- **test:** ajout tests
- **chore:** tâches maintenance

### Exemple complet

```bash
# Développement sur main
git checkout main
git pull origin main

# Modification fichiers...
git add .
git commit -m "feat: intégration capteur PM2.5 Feinstaub

- Ajout support capteur SDS011
- Configuration Telegraf pour PM2.5
- Dashboard Grafana particules fines
- Tests validation données"

git push origin main

# Tag version
git tag -a v2.3.0 -m "Version 2.3.0: Support capteurs Feinstaub"
git push origin --tags
```

## 📊 Historique des modifications

### Évolution du workflow

1. **v2.2.0-v2.2.2** : Workflow avec dev-feinstaub + main
2. **v2.2.3+** : Workflow simplifié avec main uniquement

### Raison de la simplification

- **Synchronisation parfaite** : Plus besoin de branche séparée
- **Développement linéaire** : Workflow plus simple et direct
- **Moins de complexité** : Gestion facilitée pour un développeur unique

---

**Documentation Git Workflow v2.2.3** - Version simplifiée  
Projet IoT Sensors UCUM - Dominique Dessy - Août 2025
