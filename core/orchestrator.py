"""Orchestrateur principal gérant la récursivité et le routage des tool calls."""
import json
from typing import Dict, Any, List, Optional
from core.base import GraphManager
from core.factory import AgentFactory
from tools.filesystem import MCPFilesystem


class Orchestrator:
    """Orchestrateur gérant la boucle de réflexion et la récursivité."""
    
    def __init__(self, client, workspace_dir: str = "./workspace"):
        self.client = client
        self.workspace_dir = workspace_dir
        self.graph_manager = GraphManager()
        self.factory = AgentFactory(graph_manager=self.graph_manager)
        self.filesystem = MCPFilesystem(base_path=workspace_dir)
        self.token_budget = 100000  # Budget par défaut
        self.tokens_used = 0
        self.max_depth = 3
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Retourne le schéma JSON de tous les outils disponibles."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "delegate_task",
                    "description": "Délègue une tâche à un agent spécialisé. Utilisez cet outil quand la tâche nécessite une expertise spécifique ou peut être décomposée.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "agent_name": {
                                "type": "string",
                                "description": "Nom unique pour identifier l'agent créé"
                            },
                            "role": {
                                "type": "string",
                                "description": "Rôle/spécialité de l'agent (ex: 'Analyste Technique', 'Rédacteur', 'Développeur')"
                            },
                            "instructions": {
                                "type": "string",
                                "description": "Instructions détaillées pour l'agent délégué"
                            },
                            "system_prompt": {
                                "type": "string",
                                "description": "Prompt système optionnel pour définir le contexte de l'agent"
                            }
                        },
                        "required": ["agent_name", "role", "instructions"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Lit le contenu d'un fichier depuis le workspace. Utilisez cet outil pour analyser des documents, logs, ou fichiers sources.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à lire (relatif au workspace)"
                            }
                        },
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Écrit du contenu dans un fichier du workspace. Utilisez cet outil pour créer des rapports, documents Markdown, ou fichiers de sortie.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Nom du fichier à créer/écraser"
                            },
                            "content": {
                                "type": "string",
                                "description": "Contenu à écrire dans le fichier"
                            }
                        },
                        "required": ["filename", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "Liste les fichiers et répertoires dans le workspace. Utilisez cet outil pour explorer l'arborescence du projet.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Chemin relatif à explorer (vide pour la racine)",
                                "default": ""
                            }
                        },
                        "required": []
                    }
                }
            }
        ]
    
    async def process_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        manager_agent,
        depth: int = 0
    ) -> Any:
        """Traite un appel d'outil et route vers la fonction appropriée."""
        
        # Vérifier le budget de tokens
        if self.tokens_used >= self.token_budget:
            raise RuntimeError(f"Budget de tokens dépassé: {self.tokens_used}/{self.token_budget}")
        
        # Vérifier la profondeur
        if depth > self.max_depth:
            raise ValueError(f"Profondeur maximale atteinte: {depth}")
        
        if tool_name == "delegate_task":
            return await self._handle_delegation(arguments, manager_agent, depth)
        elif tool_name == "read_file":
            return self.filesystem.read_file(arguments["filename"])
        elif tool_name == "write_file":
            return self.filesystem.write_file(arguments["filename"], arguments["content"])
        elif tool_name == "list_files":
            path = arguments.get("path", "")
            return self.filesystem.list_files(path)
        else:
            raise ValueError(f"Outil inconnu: {tool_name}")
    
    async def _handle_delegation(
        self,
        arguments: Dict[str, Any],
        parent_agent,
        depth: int
    ) -> str:
        """Gère la délégation de tâche à un Worker."""
        agent_name = arguments["agent_name"]
        role = arguments["role"]
        instructions = arguments["instructions"]
        system_prompt = arguments.get("system_prompt")
        
        # Créer le worker
        worker = self.factory.create_worker(
            agent_name=agent_name,
            role=role,
            system_prompt=system_prompt,
            parent_agent=parent_agent.name,
            depth=depth + 1
        )
        
        # Mettre à jour le graphe
        parent_agent.update_graph("Délégation", agent_name, {"role": role})
        
        # Exécuter la tâche
        result = await worker.process(instructions)
        
        return result
    
    async def execute_with_llm(
        self,
        manager_agent,
        query: str,
        depth: int = 0
    ) -> str:
        """Exécute une requête en utilisant le LLM pour générer des tool calls."""
        
        # Construire les messages
        messages = [
            {
                "role": "system",
                "content": manager_agent.get_system_prompt()
            }
        ]
        
        # Ajouter l'historique récent
        for entry in manager_agent.history[-5:]:
            if "query" in entry:
                messages.append({"role": "user", "content": entry["query"]})
            if "response" in entry:
                messages.append({"role": "assistant", "content": entry["response"]})
        
        # Ajouter la requête actuelle
        messages.append({"role": "user", "content": query})
        
        # Appeler le LLM avec tool calling
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # ou autre modèle
                messages=messages,
                tools=self.get_tools_schema(),
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Traiter les tool calls
            if message.tool_calls:
                results = []
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    result = await self.process_tool_call(
                        tool_name,
                        arguments,
                        manager_agent,
                        depth
                    )
                    results.append(result)
                
                # Si plusieurs tool calls, combiner les résultats
                combined_result = "\n".join(str(r) for r in results)
                
                # Optionnel: faire un appel de suivi pour synthétiser
                return combined_result
            else:
                # Réponse directe du LLM
                return message.content
            
        except Exception as e:
            return f"Erreur lors de l'appel LLM: {str(e)}"
    
    def save_graph(self, filepath: Optional[str] = None):
        """Sauvegarde le graphe de session."""
        if not filepath:
            filepath = f"{self.workspace_dir}/graph.json"
        return self.graph_manager.save_graph(filepath)
    
    def get_graph(self) -> Dict:
        """Retourne le graphe actuel."""
        return self.graph_manager.get_graph()
