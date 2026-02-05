"""
Exemple 1: Analyse de logs système

Ce cas d'usage démontre comment le Manager délègue l'analyse de logs
à un agent spécialisé qui identifie les erreurs et génère un rapport.
"""
import asyncio
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from openai import OpenAI
from agents.manager import ManagerAgent
from core.base import GraphManager
from core.orchestrator import Orchestrator

load_dotenv()


async def main():
    """Exemple d'analyse de logs avec délégation."""
    
    # Configuration
    api_key = os.getenv("OPENAI_API_KEY")
    workspace_dir = "./workspace/examples/log_analysis"
    
    # Créer le répertoire de travail
    os.makedirs(workspace_dir, exist_ok=True)
    
    # Créer des fichiers de log d'exemple
    log_content = """2024-02-05 10:15:23 INFO: Application démarrée
2024-02-05 10:15:24 INFO: Connexion à la base de données réussie
2024-02-05 10:16:45 WARNING: Cache presque plein (85%)
2024-02-05 10:17:12 ERROR: Échec de connexion à l'API externe: timeout
2024-02-05 10:17:13 INFO: Tentative de reconnexion...
2024-02-05 10:17:45 ERROR: Échec de connexion à l'API externe: timeout
2024-02-05 10:18:20 WARNING: Utilisation mémoire élevée: 2.3GB
2024-02-05 10:19:05 INFO: Reconnexion réussie
2024-02-05 10:20:15 ERROR: Erreur de validation: champ 'email' invalide
2024-02-05 10:21:30 INFO: Traitement de 150 requêtes
2024-02-05 10:22:45 WARNING: Latence élevée détectée: 450ms
2024-02-05 10:23:10 ERROR: Erreur de validation: champ 'email' invalide
"""
    
    with open(f"{workspace_dir}/app.log", "w", encoding="utf-8") as f:
        f.write(log_content)
    
    # Initialiser le client
    import json
    if not api_key:
        print("⚠️  Mode mock activé (pas de clé API)")
        class MockClient:
            class chat:
                class completions:
                    @staticmethod
                    def create(*args, **kwargs):
                        # Créer le tool_call pour déléguer
                        print("[MOCK] Génération d'un tool_call pour déléguer la tâche")
                        
                        class MockFunction:
                            def __init__(self):
                                self.name = "delegate_task"
                                self.arguments = json.dumps({
                                    "agent_name": "Analyste_Logs",
                                    "role": "Analyste de Logs Système",
                                    "instructions": "Analyse le fichier app.log, identifie toutes les erreurs et warnings, calcule des statistiques (nombre d'erreurs par type, fréquence) et génère un rapport détaillé dans rapport_analyse_logs.md",
                                    "system_prompt": "Tu es un expert en analyse de logs système. Tu identifies les patterns d'erreurs, calcule les statistiques et génère des rapports clairs en Markdown."
                                })
                                print(f"[MOCK] Tool function créée: {self.name}")
                        
                        class MockToolCall:
                            def __init__(self):
                                self.function = MockFunction()
                                self.id = "call_mock_123"
                                self.type = "function"
                                print(f"[MOCK] ToolCall créé: id={self.id}, type={self.type}")
                        
                        tool_call = MockToolCall()
                        
                        class MockMessage:
                            def __init__(self):
                                self.content = None
                                self.tool_calls = [tool_call]  # Utiliser l'instance créée
                                self.role = "assistant"
                                print(f"[MOCK] Message créé avec {len(self.tool_calls)} tool_call(s)")
                        
                        message = MockMessage()
                        
                        class MockChoice:
                            def __init__(self):
                                self.message = message
                                self.finish_reason = "tool_calls"
                                print(f"[MOCK] Choice créé avec finish_reason: {self.finish_reason}")
                        
                        choice = MockChoice()
                        
                        class MockResponse:
                            def __init__(self):
                                self.choices = [choice]
                                print(f"[MOCK] Response créée avec {len(self.choices)} choice(s)")
                        
                        response = MockResponse()
                        print("[MOCK] Mock response généré avec succès")
                        return response
        
        client = MockClient()
    else:
        client = OpenAI(api_key=api_key)
    
    # Initialiser le système
    print("=" * 70)
    print("📊 EXEMPLE 1: Analyse de Logs Système")
    print("=" * 70)
    
    graph_manager = GraphManager()
    orchestrator = Orchestrator(client, workspace_dir)
    orchestrator.graph_manager = graph_manager
    
    manager = ManagerAgent("Manager_Logs", client, graph_manager, orchestrator)
    
    print(f"\n📁 Workspace: {workspace_dir}")
    print(f"📝 Fichier de log créé: app.log\n")
    
    # Requête
    query = """Analyse le fichier app.log dans le workspace. 
    Identifie toutes les erreurs et warnings, calcule des statistiques 
    (nombre d'erreurs par type, fréquence, etc.) et génère un rapport 
    détaillé dans un fichier rapport_analyse_logs.md"""
    
    print("💬 Requête:")
    print(f"   {query}\n")
    print("-" * 70)
    print("🔄 Traitement en cours...\n")
    
    try:
        result = await manager.process(query)
        
        print("\n" + "=" * 70)
        print("✅ Résultat:")
        print("=" * 70)
        print(result)
        
        # Sauvegarder le graphe
        graph_path = orchestrator.save_graph(f"{workspace_dir}/graph.json")
        print(f"\n📊 Graphe sauvegardé: {graph_path}")
        
        # Vérifier si le rapport a été créé
        report_path = f"{workspace_dir}/rapport_analyse_logs.md"
        if os.path.exists(report_path):
            print(f"📄 Rapport généré: {report_path}")
            with open(report_path, "r", encoding="utf-8") as f:
                print("\n📋 Contenu du rapport:")
                print("-" * 70)
                print(f.read()[:500] + "..." if len(f.read()) > 500 else f.read())
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
