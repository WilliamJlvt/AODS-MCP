from typing import Optional
from datetime import datetime
from core.base import BaseAgent, GraphManager
from tools.filesystem import MCPFilesystem


class WorkerAgent(BaseAgent):
    """Agent Worker spécialisé pour l'exécution de tâches spécifiques."""
    
    def __init__(
        self,
        name: str,
        role: str,
        graph_manager: Optional[GraphManager] = None,
        system_prompt: Optional[str] = None
    ):
        super().__init__(name, role, graph_manager)
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.filesystem = MCPFilesystem()
    
    def _default_system_prompt(self) -> str:
        """Retourne le prompt système par défaut pour un Worker."""
        return f"""Tu es un agent Worker spécialisé dans le rôle: {self.role}.

Tu as reçu une mission spécifique à accomplir. Utilise tes capacités pour:
- Analyser les informations fournies
- Traiter les données nécessaires
- Produire un résultat clair et structuré

Si tu as besoin d'informations supplémentaires ou si les instructions sont floues,
demande des clarifications dans ta réponse."""
    
    def get_system_prompt(self) -> str:
        """Retourne le prompt système de ce Worker."""
        return self.system_prompt
    
    async def process(self, task: str) -> str:
        """Traite une tâche assignée."""
        self.log_action("Exécution de la tâche", task)
        
        # Enregistrer la tâche dans l'historique
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "task": task
        })
        
        # Pour l'instant, le Worker fait un traitement simple
        # Dans une implémentation complète, il pourrait aussi utiliser le LLM
        # ou avoir accès à des outils spécifiques
        
        result = f"""Résultat du travail de {self.role} ({self.name}):

Mission: {task}

Traitement effectué:
- Analyse de la demande
- Exécution des opérations requises
- Génération du résultat

Résultat: [Tâche '{task}' traitée avec succès par {self.name}]
"""
        
        self.log_action("Tâche terminée", f"Résultat généré")
        return result
    
    async def execute(self, task: str) -> str:
        """Alias pour compatibilité avec l'ancienne interface."""
        return await self.process(task)
    
    def log_action(self, action: str, details: str = None):
        """Override pour un formatage spécifique aux Workers."""
        indent = "  " * (self.depth + 1)
        print(f"{indent}└─> [{self.name} - {self.role}] {action}: {details}")
        
        # Appeler aussi la méthode parent pour le logging complet
        super().log_action(action, details)