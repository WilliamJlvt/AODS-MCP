from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime


class GraphManager:
    """Gestionnaire centralisé du graphe de session."""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.graph_data = {
            "session_id": self.session_id,
            "nodes": [],
            "edges": []
        }
        self.node_counter = 0
        
    def add_node(self, node_id: str, label: str, node_type: str = "agent", metadata: Optional[Dict] = None):
        """Ajoute un nœud au graphe."""
        node = {
            "id": node_id,
            "label": label,
            "type": node_type,
            "metadata": metadata or {}
        }
        self.graph_data["nodes"].append(node)
        return node_id
    
    def add_edge(self, source: str, target: str, label: str = "", metadata: Optional[Dict] = None):
        """Ajoute une arête au graphe."""
        edge = {
            "source": source,
            "target": target,
            "label": label,
            "metadata": metadata or {}
        }
        self.graph_data["edges"].append(edge)
        return edge
    
    def save_graph(self, filepath: str = "./workspace/graph.json"):
        """Sauvegarde le graphe dans un fichier JSON."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.graph_data, f, indent=2, ensure_ascii=False)
        return filepath
    
    def get_graph(self) -> Dict:
        """Retourne le graphe actuel."""
        return self.graph_data


class Tool(ABC):
    """Interface abstraite pour les outils disponibles aux agents."""
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Retourne le schéma JSON de l'outil (format OpenAI)."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Exécute l'outil avec les paramètres fournis."""
        pass


class BaseAgent(ABC):
    """Classe de base abstraite pour tous les agents."""
    
    def __init__(self, name: str, role: str, graph_manager: Optional[GraphManager] = None):
        self.name = name
        self.role = role
        self.history: List[Dict[str, Any]] = []
        self.graph_manager = graph_manager
        self.depth = 0  # Profondeur de délégation
        
        # Enregistrer le nœud dans le graphe
        if self.graph_manager:
            self.graph_manager.add_node(
                self.name,
                f"{self.name} ({self.role})",
                node_type="agent",
                metadata={"role": self.role}
            )
    
    @abstractmethod
    async def process(self, query: str) -> str:
        """Méthode principale pour traiter une requête."""
        pass
    
    def log_action(self, action: str, details: Any = None):
        """Enregistre une action pour la télémétrie et le graphe."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "action": action,
            "details": str(details) if details else None
        }
        self.history.append(log_entry)
        print(f"[{self.name}] {action}: {details}")
        
        # Sauvegarder dans session.log
        self._write_session_log(log_entry)
    
    def _write_session_log(self, log_entry: Dict):
        """Écrit dans le fichier de log de session."""
        log_file = "./workspace/session.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def get_tools(self) -> List[Tool]:
        """Retourne la liste des outils disponibles pour cet agent."""
        return []
    
    def update_graph(self, action: str, target: Optional[str] = None, metadata: Optional[Dict] = None):
        """Met à jour le graphe avec une action."""
        if self.graph_manager:
            if target:
                self.graph_manager.add_edge(
                    self.name,
                    target,
                    label=action,
                    metadata=metadata or {}
                )
    
    def set_depth(self, depth: int):
        """Définit la profondeur de délégation."""
        self.depth = depth
        if depth > 3:
            raise ValueError(f"Profondeur de délégation dépassée: {depth} (max: 3)")
