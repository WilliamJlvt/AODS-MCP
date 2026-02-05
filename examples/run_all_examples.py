"""
Script pour exécuter tous les exemples d'un coup.

Usage:
    python examples/run_all_examples.py
    python examples/run_all_examples.py --skip 1,3  # Skip examples 1 and 3
"""
import asyncio
import sys
import argparse
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importer tous les exemples
from examples import example_1_log_analysis
from examples import example_2_documentation
from examples import example_3_security_audit
from examples import example_4_performance_analysis
from examples import example_5_code_migration
from examples import example_6_code_review


EXAMPLES = [
    ("1", "Analyse de logs", example_1_log_analysis.main),
    ("2", "Génération de documentation", example_2_documentation.main),
    ("3", "Audit de sécurité", example_3_security_audit.main),
    ("4", "Analyse de performance", example_4_performance_analysis.main),
    ("5", "Migration de code", example_5_code_migration.main),
    ("6", "Revue de code", example_6_code_review.main),
]


async def run_all(skip_list=None):
    """Exécute tous les exemples."""
    if skip_list is None:
        skip_list = []
    
    print("=" * 70)
    print("🚀 EXÉCUTION DE TOUS LES EXEMPLES")
    print("=" * 70)
    print(f"📋 {len(EXAMPLES)} exemples disponibles")
    if skip_list:
        print(f"⏭️  Exemples ignorés: {', '.join(skip_list)}\n")
    else:
        print()
    
    results = []
    
    for num, name, main_func in EXAMPLES:
        if num in skip_list:
            print(f"⏭️  Exemple {num} ignoré: {name}")
            continue
        
        print("\n" + "=" * 70)
        print(f"▶️  EXEMPLE {num}: {name}")
        print("=" * 70)
        
        try:
            await main_func()
            results.append((num, name, "✅ Succès"))
        except Exception as e:
            results.append((num, name, f"❌ Erreur: {str(e)}"))
            print(f"\n❌ Erreur dans l'exemple {num}: {str(e)}")
        
        print("\n" + "-" * 70)
        print("Pause de 2 secondes avant le prochain exemple...")
        await asyncio.sleep(2)
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    for num, name, status in results:
        print(f"  {num}. {name}: {status}")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exécute tous les exemples")
    parser.add_argument(
        "--skip",
        type=str,
        help="Liste des numéros d'exemples à ignorer (ex: 1,3,5)",
        default=""
    )
    
    args = parser.parse_args()
    
    skip_list = []
    if args.skip:
        skip_list = [s.strip() for s in args.skip.split(",")]
    
    asyncio.run(run_all(skip_list))
