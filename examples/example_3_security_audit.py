"""
Exemple 3: Audit de sécurité de code

Ce cas d'usage illustre un audit de sécurité multi-agents où le Manager
coordonne plusieurs agents spécialisés pour analyser différents aspects.
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
    """Exemple d'audit de sécurité."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    workspace_dir = "./workspace/examples/security_audit"
    os.makedirs(workspace_dir, exist_ok=True)
    
    # Code avec des problèmes de sécurité potentiels
    vulnerable_code = """import os
import subprocess
import pickle
from flask import Flask, request

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute_command():
    # VULN: Injection de commande
    command = request.form.get('cmd')
    result = subprocess.run(command, shell=True, capture_output=True)
    return result.stdout

@app.route('/load', methods=['POST'])
def load_data():
    # VULN: Désérialisation non sécurisée
    data = request.form.get('data')
    obj = pickle.loads(data)
    return str(obj)

@app.route('/read', methods=['GET'])
def read_file():
    # VULN: Path traversal
    filename = request.args.get('file')
    with open(filename, 'r') as f:
        return f.read()

def authenticate(password):
    # VULN: Comparaison de strings non sécurisée
    if password == "admin123":
        return True
    return False
"""
    
    with open(f"{workspace_dir}/app.py", "w", encoding="utf-8") as f:
        f.write(vulnerable_code)
    
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
                                    "agent_name": "Auditeur_Securite",
                                    "role": "Expert en Sécurité Applicative",
                                    "instructions": "Analyse app.py et identifie toutes les vulnérabilités de sécurité (injection, path traversal, désérialisation, etc.). Génère un rapport détaillé avec niveau de criticité pour chaque vulnérabilité.",
                                    "system_prompt": "Tu es un expert en sécurité applicative. Tu identifies les vulnérabilités OWASP Top 10 et autres failles de sécurité."
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
    print("🔒 EXEMPLE 3: Audit de Sécurité de Code")
    print("=" * 70)
    
    graph_manager = GraphManager()
    orchestrator = Orchestrator(client, workspace_dir)
    orchestrator.graph_manager = graph_manager
    
    manager = ManagerAgent("Manager_Securite", client, graph_manager, orchestrator)
    
    print(f"\n📁 Workspace: {workspace_dir}")
    print(f"💻 Code à auditer: app.py\n")
    
    query = """Effectue un audit de sécurité complet du fichier app.py.
    Identifie toutes les vulnérabilités potentielles (injection, path traversal,
    désérialisation non sécurisée, etc.) et génère un rapport d'audit avec:
    - Liste des vulnérabilités trouvées
    - Niveau de criticité (Critique, Haute, Moyenne, Faible)
    - Ligne de code concernée
    - Recommandations de correction
    
    Sauvegarde dans SECURITY_AUDIT_REPORT.md"""
    
    print("💬 Requête:")
    print(f"   {query}\n")
    print("-" * 70)
    print("🔄 Audit en cours...\n")
    
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
