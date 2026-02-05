"""
Exemple 2: Génération de documentation technique

Ce cas d'usage montre comment le Manager coordonne plusieurs agents
pour générer de la documentation complète à partir du code source.
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
    """Exemple de génération de documentation."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    workspace_dir = "./workspace/examples/documentation"
    os.makedirs(workspace_dir, exist_ok=True)
    
    # Créer un exemple de code source
    code_example = """class UserManager:
    \"\"\"Gestionnaire d'utilisateurs.\"\"\"
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.cache = {}
    
    def create_user(self, username: str, email: str) -> dict:
        \"\"\"
        Crée un nouvel utilisateur.
        
        Args:
            username: Nom d'utilisateur unique
            email: Adresse email valide
        
        Returns:
            dict: Informations de l'utilisateur créé
        
        Raises:
            ValueError: Si l'utilisateur existe déjà
        \"\"\"
        if self.user_exists(username):
            raise ValueError(f"User {username} already exists")
        
        user = {
            "id": self._generate_id(),
            "username": username,
            "email": email,
            "created_at": datetime.now()
        }
        
        self.db.save(user)
        self.cache[username] = user
        return user
    
    def get_user(self, username: str) -> dict:
        \"\"\"Récupère un utilisateur par son nom.\"\"\"
        if username in self.cache:
            return self.cache[username]
        
        user = self.db.find_by_username(username)
        if user:
            self.cache[username] = user
        return user
    
    def _generate_id(self) -> str:
        return str(uuid.uuid4())
"""
    
    with open(f"{workspace_dir}/user_manager.py", "w", encoding="utf-8") as f:
        f.write(code_example)
    
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
                                    "agent_name": "Documenteur_API",
                                    "role": "Générateur de Documentation API",
                                    "instructions": "Analyse user_manager.py et génère une documentation API complète au format Markdown avec tous les paramètres, retours et exceptions.",
                                    "system_prompt": "Tu es un expert en documentation technique. Tu génères des docs claires et complètes."
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
    print("📚 EXEMPLE 2: Génération de Documentation Technique")
    print("=" * 70)
    
    graph_manager = GraphManager()
    orchestrator = Orchestrator(client, workspace_dir)
    orchestrator.graph_manager = graph_manager
    
    manager = ManagerAgent("Manager_Docs", client, graph_manager, orchestrator)
    
    print(f"\n📁 Workspace: {workspace_dir}")
    print(f"💻 Code source: user_manager.py\n")
    
    query = """Analyse le fichier user_manager.py et génère une documentation 
    API complète incluant:
    - Description de chaque méthode
    - Paramètres avec types
    - Valeurs de retour
    - Exceptions possibles
    - Exemples d'utilisation
    
    Sauvegarde le résultat dans API_DOCUMENTATION.md"""
    
    print("💬 Requête:")
    print(f"   {query}\n")
    print("-" * 70)
    print("🔄 Traitement...\n")
    
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
