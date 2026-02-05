"""
Exemple 5: Migration de code

Ce cas d'usage montre comment le système peut aider à migrer
du code d'une version/technologie à une autre.
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from openai import OpenAI
from agents.manager import ManagerAgent
from core.base import GraphManager
from core.orchestrator import Orchestrator

load_dotenv()


async def main():
    """Exemple de migration de code."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    workspace_dir = "./workspace/examples/migration"
    os.makedirs(workspace_dir, exist_ok=True)
    
    # Code Python 2 à migrer vers Python 3
    legacy_code = """# Code Python 2.7
def process_data(data):
    print "Processing:", data
    result = []
    for item in data:
        if item.has_key('value'):
            result.append(item['value'])
    return result

class DataHandler:
    def __init__(self, name):
        self.name = name
    
    def handle(self, data):
        print "Handling with", self.name
        return process_data(data)
"""
    
    with open(f"{workspace_dir}/legacy.py", "w", encoding="utf-8") as f:
        f.write(legacy_code)
    
    # Client
    if not api_key:
        print("⚠️  Mode mock activé")
        import json
        class MockClient:
            class chat:
                class completions:
                    @staticmethod
                    def create(*args, **kwargs):
                        class MockToolCall:
                            class MockFunction:
                                name = "delegate_task"
                                arguments = json.dumps({
                                    "agent_name": "Migrateur_Code",
                                    "role": "Expert en Migration de Code",
                                    "instructions": "Analyse legacy.py (Python 2.7) et génère une version migrée vers Python 3 avec toutes les corrections nécessaires (print statements, has_key, etc.).",
                                    "system_prompt": "Tu es un expert en migration de code Python. Tu migres du Python 2 vers Python 3 en respectant les meilleures pratiques."
                                })
                            
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
    
    print("=" * 70)
    print("🔄 EXEMPLE 5: Migration de Code")
    print("=" * 70)
    
    graph_manager = GraphManager()
    orchestrator = Orchestrator(client, workspace_dir)
    orchestrator.graph_manager = graph_manager
    
    manager = ManagerAgent("Manager_Migration", client, graph_manager, orchestrator)
    
    print(f"\n📁 Workspace: {workspace_dir}")
    print(f"💻 Code legacy: legacy.py (Python 2.7)\n")
    
    query = """Analyse legacy.py et migre le code de Python 2.7 vers Python 3.
    Corrige tous les problèmes de compatibilité:
    - print statements -> print()
    - has_key() -> in operator
    - Gestion des bytes/strings
    - Autres incompatibilités
    
    Génère le code migré dans migrated.py et un rapport de migration
    dans MIGRATION_REPORT.md"""
    
    print("💬 Requête:")
    print(f"   {query}\n")
    print("-" * 70)
    print("🔄 Migration en cours...\n")
    
    try:
        result = await manager.process(query)
        
        print("\n" + "=" * 70)
        print("✅ Résultat:")
        print("=" * 70)
        print(result)
        
        orchestrator.save_graph(f"{workspace_dir}/graph.json")
        print(f"\n📊 Graphe sauvegardé")
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
