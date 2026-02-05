from typing import Optional
from datetime import datetime
from core.base import BaseAgent, GraphManager
from core.orchestrator import Orchestrator


class ManagerAgent(BaseAgent):
    """Agent Manager responsable de la délégation et de l'orchestration."""
    
    def __init__(
        self,
        name: str,
        client,
        graph_manager: Optional[GraphManager] = None,
        orchestrator: Optional[Orchestrator] = None
    ):
        super().__init__(name, role="Manager", graph_manager=graph_manager)
        self.client = client
        self.orchestrator = orchestrator
        
        # Si pas d'orchestrateur fourni, en créer un
        if not self.orchestrator:
            workspace_dir = "./workspace"
            self.orchestrator = Orchestrator(client, workspace_dir)
            if graph_manager:
                self.orchestrator.graph_manager = graph_manager
    
    def get_system_prompt(self) -> str:
        """Retourne le prompt système pour le Manager."""
        return """Tu es un agent Manager intelligent capable de décomposer des tâches complexes 
en sous-tâches et de déléguer à des agents spécialisés. 

Tu as accès aux outils suivants:
- delegate_task: Pour déléguer une tâche à un agent spécialisé
- read_file: Pour lire des fichiers du workspace
- write_file: Pour écrire des fichiers dans le workspace
- list_files: Pour explorer l'arborescence du workspace

Quand une tâche est trop complexe ou nécessite une expertise spécifique, utilise delegate_task 
pour créer un agent Worker spécialisé. Sinon, utilise directement les outils de fichiers 
pour accomplir la tâche.

Après avoir reçu les résultats d'un agent délégué, compile les informations et génère 
un rapport final si nécessaire."""
    
    async def process(self, query: str) -> str:
        """Traite une requête utilisateur."""
        self.log_action("Instruction reçue", query)
        
        # Enregistrer la requête dans l'historique
        timestamp = datetime.now().isoformat()
        self.history.append({
            "timestamp": timestamp,
            "agent": self.name,
            "query": query
        })
        
        # Utiliser l'orchestrateur pour exécuter avec le LLM
        try:
            result = await self.orchestrator.execute_with_llm(
                manager_agent=self,
                query=query,
                depth=0
            )
            
            # Enregistrer la réponse
            self.history.append({
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
                "response": result
            })
            
            self.log_action("Tâche terminée", f"Résultat: {result[:100]}...")
            return result
            
        except Exception as e:
            error_msg = f"Erreur lors du traitement: {str(e)}"
            self.log_action("Erreur", error_msg)
            return error_msg
    
    async def execute(self, task: str) -> str:
        """Alias pour compatibilité avec l'ancienne interface."""
        return await self.process(task)