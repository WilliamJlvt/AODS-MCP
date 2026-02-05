"""Factory pour la création dynamique d'agents."""
from typing import Optional, Dict, Any
from agents.worker import WorkerAgent
from agents.manager import ManagerAgent
from core.base import GraphManager


class AgentFactory:
    """Factory pour créer des agents à la volée."""
    
    def __init__(self, graph_manager: Optional[GraphManager] = None):
        self.graph_manager = graph_manager
        self.agent_registry: Dict[str, Any] = {}
        self.agent_counter = 0
    
    def create_worker(
        self,
        agent_name: Optional[str] = None,
        role: str = "Worker",
        system_prompt: Optional[str] = None,
        parent_agent: Optional[str] = None,
        depth: int = 0
    ) -> WorkerAgent:
        """Crée un agent Worker avec un contexte spécifique."""
        if not agent_name:
            self.agent_counter += 1
            agent_name = f"Worker_{self.agent_counter}"
        
        # Vérifier la profondeur
        if depth > 3:
            raise ValueError(f"Profondeur de délégation maximale atteinte: {depth}")
        
        worker = WorkerAgent(
            name=agent_name,
            role=role,
            graph_manager=self.graph_manager,
            system_prompt=system_prompt
        )
        worker.set_depth(depth)
        
        # Enregistrer dans le registre
        self.agent_registry[agent_name] = worker
        
        # Ajouter une arête si parent spécifié
        if parent_agent and self.graph_manager:
            self.graph_manager.add_edge(
                parent_agent,
                agent_name,
                label="Délégation",
                metadata={"role": role, "depth": depth}
            )
        
        return worker
    
    def create_manager(
        self,
        name: str,
        client,
        graph_manager: Optional[GraphManager] = None
    ) -> ManagerAgent:
        """Crée un agent Manager."""
        manager = ManagerAgent(
            name=name,
            client=client,
            graph_manager=graph_manager or self.graph_manager
        )
        self.agent_registry[name] = manager
        return manager
    
    def get_agent(self, agent_name: str):
        """Récupère un agent depuis le registre."""
        return self.agent_registry.get(agent_name)
    
    def list_agents(self) -> list:
        """Liste tous les agents créés."""
        return list(self.agent_registry.keys())
