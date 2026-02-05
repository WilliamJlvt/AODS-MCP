# **SYNERGOS-MCP** (Autonomous Orchestration & Delegation System)

## Définition Technique

SYNERGOS-MCP est une implémentation logicielle en Python conçue pour transformer un modèle de langage en un système d'exploitation d'agents autonome. Le système repose sur le standard **Model Context Protocol (MCP)** pour l'interfaçage avec les ressources locales et utilise le schéma de **Tool Calling OpenAI** pour la gestion de la logique de branchement et de délégation récursive.

**Statut du projet :** Prototype de système multi-agents avec délégation intelligente.

## 🚀 Installation

### Prérequis

- Python 3.10 ou supérieur
- Clé API OpenAI (optionnelle pour les tests avec mock)

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Configuration

Créez un fichier `.env` à la racine du projet :

```env
# Clé API OpenAI (requis pour utiliser le LLM)
OPENAI_API_KEY=your_openai_api_key_here

# Répertoire de travail (optionnel, défaut: ./workspace)
WORKSPACE_DIR=./workspace
```

## 📖 Utilisation

### Exécution du système

```bash
python main.py
```

Le système vous demandera une requête ou utilisera un exemple par défaut.

### Visualisation du graphe

Pour visualiser le graphe de session au format texte :

```bash
python visualize.py
```

Pour générer une visualisation HTML interactive :

```bash
python visualize.py --html
```

Le fichier HTML sera généré dans `./workspace/graph.html` et peut être ouvert dans votre navigateur.

## Architecture et Composants

### Couche Core (Abstraction)

* **`core/base.py`** : Classes de base abstraites (ABC) pour l'unification des interfaces
  - `BaseAgent` : Interface de base pour tous les agents
  - `GraphManager` : Gestionnaire centralisé du graphe de session
  - `Tool` : Interface abstraite pour les outils

* **`core/factory.py`** : Factory pour la création dynamique d'agents
  - `AgentFactory` : Crée des agents Manager et Worker à la volée

* **`core/orchestrator.py`** : Orchestrateur principal
  - Gère la récursivité et le routage des tool calls
  - Intègre avec OpenAI pour la génération de tool calls
  - Gère le budget de tokens et la profondeur de délégation

### Couche Agents

* **`agents/manager.py`** : Agent Manager
  - Analyse les requêtes utilisateur
  - Décompose les tâches complexes
  - Délègue aux agents spécialisés
  - Compile les résultats

* **`agents/worker.py`** : Agents Worker
  - Exécutent des tâches spécialisées
  - Peuvent avoir des prompts système personnalisés
  - Retournent des résultats structurés

### Couche Tools (MCP)

* **`tools/filesystem.py`** : Gestionnaire de fichiers sécurisé
  - `read_file` : Lecture de fichiers depuis le workspace
  - `write_file` : Écriture de fichiers dans le workspace
  - `list_files` : Exploration de l'arborescence
  - Validation des chemins pour sécurité (sandbox)

## Fonctionnalités Principales

* **Délégation Récursive** : Le Manager peut créer des agents Worker spécialisés pour des tâches complexes
* **Normalisation OpenAI** : Utilise le format standard OpenAI Tool Calling
* **Tracking Grapheur** : Génère un graphe JSON de toutes les actions et délégations
* **Sandbox I/O** : Accès restreint au système de fichiers via validation des chemins
* **Sécurité** : 
  - Limite de profondeur de délégation (max 3 niveaux)
  - Validation des chemins de fichiers
  - Budget de tokens configurable
* **Visualisation** : Scripts pour visualiser le graphe de session (texte et HTML interactif)

## Structure de l'Arborescence

```text
AODS-MCP/
├── main.py                 # Point d'entrée principal
├── visualize.py            # Script de visualisation du graphe
├── requirements.txt        # Dépendances Python
├── README.md              # Documentation
├── doc.md                 # Document de conception technique
├── core/
│   ├── __init__.py
│   ├── base.py            # Interfaces abstraites et GraphManager
│   ├── factory.py         # Factory pour création d'agents
│   └── orchestrator.py    # Orchestrateur principal
├── agents/
│   ├── __init__.py
│   ├── manager.py         # Agent Manager
│   └── worker.py          # Agents Worker
└── tools/
    ├── __init__.py
    └── filesystem.py      # Gestionnaire de fichiers MCP
```

## Protocole d'Exécution

1. **Initialisation** : Création du Manager et de l'Orchestrateur
2. **Réception de requête** : L'utilisateur soumet une tâche
3. **Analyse** : Le Manager utilise le LLM pour analyser la tâche
4. **Décision** : Le LLM génère des tool calls (délégation, lecture, écriture, etc.)
5. **Exécution** : L'orchestrateur route les tool calls vers les fonctions appropriées
6. **Délégation** : Si nécessaire, création d'agents Worker spécialisés
7. **Agrégation** : Compilation des résultats de tous les agents
8. **Rapport** : Génération du résultat final et sauvegarde du graphe

## 📊 Visualisation

Le système génère automatiquement :
- `workspace/graph.json` : Graphe de session au format JSON
- `workspace/session.log` : Log de toutes les actions
- `workspace/graph.html` : Visualisation HTML interactive (si généré)

## 🔒 Sécurité

Le système inclut plusieurs garde-fous :
- **Limite de profondeur** : Maximum 3 niveaux de délégation
- **Validation des chemins** : Empêche l'accès hors du workspace
- **Budget de tokens** : Limite configurable pour éviter les coûts excessifs

## 📝 Notes

Ce projet est un prototype de "Mainframe Agentique" - un système capable d'auto-organisation via la délégation intelligente. Il suit les standards OpenAI et MCP pour assurer la compatibilité avec les futurs modèles de langage.

Pour plus de détails sur la conception, consultez `doc.md`.

## 🎯 Exemples d'utilisation

Le dossier `examples/` contient 6 cas d'usage concrets démontrant les capacités du système :

1. **Analyse de logs système** - Délégation pour analyser des logs et générer des rapports
2. **Génération de documentation** - Création automatique de documentation technique
3. **Audit de sécurité** - Détection de vulnérabilités dans le code
4. **Analyse de performance** - Identification de goulots d'étranglement
5. **Migration de code** - Assistance à la migration entre versions
6. **Revue de code automatisée** - Analyse multi-facettes du code

Consultez `examples/README.md` pour plus de détails sur chaque exemple.

**Exécuter un exemple :**
```bash
python examples/example_1_log_analysis.py
```
