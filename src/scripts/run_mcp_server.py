#!/usr/bin/env python3
"""
Script de lancement pour le serveur MCP IoT Sensors
"""

import sys
import os

# Définir les chemins
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # Remonter vers racine
venv_python = os.path.join(project_root, '.venv', 'bin', 'python')
src_path = os.path.dirname(current_dir)  # Répertoire src

# Si nous ne sommes pas dans le bon environnement Python, relancer avec le bon
if not sys.executable.endswith('.venv/bin/python'):
    if os.path.exists(venv_python):
        # Relancer avec l'environnement virtuel en utilisant os.execv
        os.execv(venv_python, [venv_python] + sys.argv)
    else:
        print(f"Erreur: Environnement virtuel non trouvé à {venv_python}", file=sys.stderr)
        print("Lancez: source .venv/bin/activate", file=sys.stderr)
        sys.exit(1)

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, src_path)

# Importer et lancer le serveur
try:
    from iot_sensors_mcp.server import main
    import asyncio
    
    if __name__ == '__main__':
        asyncio.run(main())
        
except ImportError as e:
    print(f"Erreur d'import: {e}", file=sys.stderr)
    print(f"PYTHONPATH: {sys.path}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Erreur: {e}", file=sys.stderr)
    sys.exit(1)
