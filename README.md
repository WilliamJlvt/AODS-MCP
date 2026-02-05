
# **AODS-MCP** (Autonomous Orchestration & Delegation System)

## Définition Technique

AODS-MCP est une implémentation logicielle en Python conçue pour l'orchestration de systèmes multi-agents. Le système repose sur le standard **Model Context Protocol (MCP)** pour l'interfaçage avec les ressources locales et utilise le schéma de **Tool Calling OpenAI** pour la gestion de la logique de branchement et de délégation récursive.

**Statut du projet :** Test environnemental pour développements personnels.

## Architecture et Composants

* **Abstraction (core/base.py) :** Utilisation de classes de base abstraites (ABC) pour l'unification des interfaces `execute` et `log_action`.
* **Orchestration (agents/manager.py) :** Hub décisionnel gérant le cycle de vie des sous-agents et le routage des métadonnées vers le moteur d'exécution.
* **Exécution (agents/worker.py) :** Instances d'agents spécialisés sans état (stateless) pour le traitement de tâches isolées.
* **I/O Resource (tools/filesystem.py) :** Couche d'abstraction filesystem simulant un serveur de ressources MCP pour la persistance des données et la gestion des rapports.

## Fonctionnalités Principales

* **Délégation Récursive :** Capacité du système à générer des instances d'agents enfants en fonction de la complexité de l'input utilisateur.
* **Normalisation OpenAI :** Interopérabilité avec les modèles supportant le JSON Schema pour la définition des outils de délégation.
* **Tracking Grapheur :** Structuration des logs en format nœuds/arêtes pour reconstruction de l'arbre de décision.
* **Sandbox I/O :** Accès restreint au système de fichiers via un path-prefix dédié.

## Structure de l'Arborescence

```text
AODS-MCP/
├── main.py                 # Initialisation du runtime
├── core/
│   └── base.py             # Interfaces abstraites
├── agents/
│   ├── manager.py          # Orchestrateur central
│   └── worker.py           # Agents d'exécution
└── tools/
    └── filesystem.py       # Couche d'accès aux ressources

```

## Protocole d'Exécution

1. Injection de la requête dans l'orchestrateur.
2. Analyse de dépendances et génération des tool_calls de délégation.
3. Instanciation dynamique des agents requis via la classe `WorkerAgent`.
4. Agrégation des sorties et commit des fichiers via le module filesystem.
5. Export du log de session pour visualisation du graphe.
