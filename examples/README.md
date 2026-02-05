# Exemples d'utilisation de SYNERGOS-MCP

Ce dossier contient des exemples concrets d'utilisation du système SYNERGOS-MCP pour différents cas d'usage.

## 📋 Cas d'usage disponibles

### 1. Analyse de logs système
**Fichier:** `example_1_log_analysis.py`

Démontre comment le Manager délègue l'analyse de logs à un agent spécialisé qui :
- Lit les fichiers de log
- Identifie les erreurs et warnings
- Génère un rapport structuré

**Commande:**
```bash
python examples/example_1_log_analysis.py
```

### 2. Génération de documentation technique
**Fichier:** `example_2_documentation.py`

Montre la délégation pour créer de la documentation :
- Analyse du code source
- Génération de documentation API
- Création de guides utilisateur

**Commande:**
```bash
python examples/example_2_documentation.py
```

### 3. Audit de sécurité de code
**Fichier:** `example_3_security_audit.py`

Illustre un audit de sécurité multi-agents :
- Agent analyseur de dépendances
- Agent détecteur de vulnérabilités
- Agent générateur de rapport

**Commande:**
```bash
python examples/example_3_security_audit.py
```

### 4. Analyse de performance
**Fichier:** `example_4_performance_analysis.py`

Démontre l'analyse de performance avec délégation :
- Analyse des métriques
- Identification des goulots d'étranglement
- Recommandations d'optimisation

**Commande:**
```bash
python examples/example_4_performance_analysis.py
```

### 5. Migration de code
**Fichier:** `example_5_code_migration.py`

Exemple de migration assistée :
- Analyse du code legacy
- Planification de la migration
- Génération du code migré

**Commande:**
```bash
python examples/example_5_code_migration.py
```

### 6. Revue de code automatisée
**Fichier:** `example_6_code_review.py`

Montre une revue de code multi-facettes :
- Agent vérificateur de style
- Agent analyseur de complexité
- Agent détecteur de bugs potentiels

**Commande:**
```bash
python examples/example_6_code_review.py
```

## 🚀 Utilisation

Tous les exemples peuvent être exécutés indépendamment. Ils créent leurs propres données de test dans le workspace et génèrent des rapports.

**Prérequis:**
- Avoir configuré `.env` avec `OPENAI_API_KEY` (ou utiliser le mode mock)
- Avoir installé les dépendances : `pip install -r requirements.txt`

## 📊 Visualisation

Après chaque exécution, vous pouvez visualiser le graphe de délégation :
```bash
python visualize.py --html
```

Ouvrez ensuite `workspace/graph.html` dans votre navigateur.
