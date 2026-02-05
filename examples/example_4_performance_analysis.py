"""
Exemple 4: Analyse de performance

Ce cas d'usage montre comment analyser les métriques de performance
et identifier les goulots d'étranglement.
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
    """Exemple d'analyse de performance."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    workspace_dir = "./workspace/examples/performance"
    os.makedirs(workspace_dir, exist_ok=True)
    
    # Métriques de performance
    metrics = """Timestamp,Endpoint,ResponseTime,CPU,Memory,Requests
2024-02-05 10:00:00,/api/users,120,45,2.1,150
2024-02-05 10:01:00,/api/users,135,52,2.3,180
2024-02-05 10:02:00,/api/products,450,78,3.2,90
2024-02-05 10:03:00,/api/users,110,48,2.2,165
2024-02-05 10:04:00,/api/products,520,85,3.5,95
2024-02-05 10:05:00,/api/orders,890,92,4.1,45
2024-02-05 10:06:00,/api/users,125,50,2.4,170
2024-02-05 10:07:00,/api/products,480,80,3.3,88
2024-02-05 10:08:00,/api/orders,920,95,4.3,42
2024-02-05 10:09:00,/api/users,115,46,2.1,160
2024-02-05 10:10:00,/api/products,510,82,3.4,92
2024-02-05 10:11:00,/api/orders,950,98,4.5,40
"""
    
    with open(f"{workspace_dir}/metrics.csv", "w", encoding="utf-8") as f:
        f.write(metrics)
    
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
                                    "agent_name": "Analyste_Performance",
                                    "role": "Expert en Analyse de Performance",
                                    "instructions": "Analyse metrics.csv et identifie les goulots d'étranglement. Calcule les moyennes, maximums, et génère des recommandations d'optimisation.",
                                    "system_prompt": "Tu es un expert en performance applicative. Tu analyses les métriques et identifies les problèmes de performance."
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
    print("⚡ EXEMPLE 4: Analyse de Performance")
    print("=" * 70)
    
    graph_manager = GraphManager()
    orchestrator = Orchestrator(client, workspace_dir)
    orchestrator.graph_manager = graph_manager
    
    manager = ManagerAgent("Manager_Performance", client, graph_manager, orchestrator)
    
    print(f"\n📁 Workspace: {workspace_dir}")
    print(f"📊 Métriques: metrics.csv\n")
    
    query = """Analyse le fichier metrics.csv et:
    1. Identifie les endpoints les plus lents
    2. Calcule les statistiques (moyenne, max, min) pour chaque endpoint
    3. Identifie les goulots d'étranglement
    4. Génère des recommandations d'optimisation
    
    Sauvegarde l'analyse dans PERFORMANCE_REPORT.md"""
    
    print("💬 Requête:")
    print(f"   {query}\n")
    print("-" * 70)
    print("🔄 Analyse en cours...\n")
    
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
