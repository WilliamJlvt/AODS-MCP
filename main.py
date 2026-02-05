import asyncio
import os
from dotenv import load_dotenv
from openai import OpenAI
from agents.manager import ManagerAgent
from core.base import GraphManager
from core.orchestrator import Orchestrator

# Charger les variables d'environnement
load_dotenv()


async def main():
    """Point d'entrée principal du système SYNERGOS-MCP."""
    
    # Configuration
    api_key = os.getenv("OPENAI_API_KEY")
    workspace_dir = os.getenv("WORKSPACE_DIR", "./workspace")
    
    if not api_key:
        print("⚠️  Attention: OPENAI_API_KEY non définie. Utilisation d'un client mock.")
        print("💡 Pour utiliser le vrai LLM, créez un fichier .env avec votre OPENAI_API_KEY\n")
        # Pour les tests sans API key, on peut utiliser un mock
        class MockClient:
            class chat:
                class completions:
                    @staticmethod
                    def create(*args, **kwargs):
                        # Retourner une réponse mockée qui simule une délégation
                        class MockToolCall:
                            class MockFunction:
                                name = "delegate_task"
                                arguments = '{"agent_name": "Worker_Mock", "role": "Test Worker", "instructions": "Tâche de test mockée"}'
                            
                            function = MockFunction()
                        
                        class MockMessage:
                            content = None
                            tool_calls = [MockToolCall()]
                        
                        class MockChoice:
                            message = MockMessage()
                        
                        class MockResponse:
                            choices = [MockChoice()]
                        
                        return MockResponse()
        
        client = MockClient()
    else:
        client = OpenAI(api_key=api_key)
    
    # Initialisation du système
    print("=" * 60)
    print("🚀 SYNERGOS-MCP - Système Multi-Agents")
    print("=" * 60)
    
    # Créer le gestionnaire de graphe
    graph_manager = GraphManager()
    
    # Créer l'orchestrateur
    orchestrator = Orchestrator(client, workspace_dir)
    orchestrator.graph_manager = graph_manager
    
    # Initialisation de l'agent Manager
    manager = ManagerAgent("Manager_Principal", client, graph_manager, orchestrator)
    
    print(f"\n📁 Workspace: {workspace_dir}")
    print(f"📊 Session ID: {graph_manager.session_id}\n")
    
    # Exemple de requête
    print("-" * 60)
    print("💬 Requête utilisateur:")
    mission = input("Entrez votre requête (ou appuyez sur Entrée pour l'exemple): ").strip()
    
    if not mission:
        mission = "Analyse les fichiers du workspace et crée un rapport récapitulatif."
        print(f"Utilisation de l'exemple: {mission}")
    
    print("-" * 60)
    print("\n🔄 Traitement en cours...\n")
    
    try:
        # Exécution
        result = await manager.process(mission)
        
        # Sauvegarder le graphe
        graph_path = orchestrator.save_graph()
        
        print("\n" + "=" * 60)
        print("✅ Résultat final:")
        print("=" * 60)
        print(result)
        print("\n" + "=" * 60)
        print(f"📊 Graphe sauvegardé: {graph_path}")
        print(f"📝 Log de session: {workspace_dir}/session.log")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Sauvegarder le graphe même en cas d'erreur
        try:
            orchestrator.save_graph()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
