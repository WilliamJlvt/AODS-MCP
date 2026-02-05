"""
Exemple 6: Revue de code automatisée

Ce cas d'usage montre une revue de code multi-facettes où plusieurs
agents analysent différents aspects du code.
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
    """Exemple de revue de code."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    workspace_dir = "./workspace/examples/code_review"
    os.makedirs(workspace_dir, exist_ok=True)
    
    # Code à revoir
    code_to_review = """def calculate_total(items):
    total = 0
    for i in range(len(items)):
        total += items[i].price * items[i].quantity
    return total

def process_user_data(user_data):
    # TODO: Add validation
    username = user_data['username']
    email = user_data['email']
    
    if username == None or email == None:
        return False
    
    # Hardcoded password - BAD!
    if user_data['password'] == 'admin123':
        return True
    
    return False

def fetch_data(url):
    import requests
    response = requests.get(url)
    return response.json()

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add(self, item):
        self.data.append(item)
    
    def process(self):
        result = []
        for i in range(len(self.data)):
            result.append(self.data[i] * 2)
        return result
"""
    
    with open(f"{workspace_dir}/code.py", "w", encoding="utf-8") as f:
        f.write(code_to_review)
    
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
                                    "agent_name": "Reveur_Code",
                                    "role": "Expert en Revue de Code",
                                    "instructions": "Analyse code.py et effectue une revue complète: style, complexité, bugs potentiels, bonnes pratiques. Génère un rapport détaillé.",
                                    "system_prompt": "Tu es un expert en revue de code. Tu identifies les problèmes de style, complexité, bugs et violations des bonnes pratiques."
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
    print("🔍 EXEMPLE 6: Revue de Code Automatisée")
    print("=" * 70)
    
    graph_manager = GraphManager()
    orchestrator = Orchestrator(client, workspace_dir)
    orchestrator.graph_manager = graph_manager
    
    manager = ManagerAgent("Manager_Review", client, graph_manager, orchestrator)
    
    print(f"\n📁 Workspace: {workspace_dir}")
    print(f"💻 Code à revoir: code.py\n")
    
    query = """Effectue une revue de code complète de code.py.
    Analyse:
    1. Style et conventions (PEP 8)
    2. Complexité cyclomatique
    3. Bugs potentiels
    4. Violations des bonnes pratiques
    5. Code smells
    
    Pour chaque problème identifié, fournis:
    - Ligne de code
    - Type de problème
    - Sévérité
    - Suggestion de correction
    
    Génère le rapport dans CODE_REVIEW_REPORT.md"""
    
    print("💬 Requête:")
    print(f"   {query}\n")
    print("-" * 70)
    print("🔄 Revue en cours...\n")
    
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
