from typing import Optional
from datetime import datetime
from core.base import BaseAgent, GraphManager
from tools.filesystem import MCPFilesystem


class WorkerAgent(BaseAgent):
    """Agent Worker spécialisé pour l'exécution de tâches spécifiques."""
    
    def __init__(
        self,
        name: str,
        role: str,
        graph_manager: Optional[GraphManager] = None,
        system_prompt: Optional[str] = None,
        workspace_dir: Optional[str] = None
    ):
        super().__init__(name, role, graph_manager)
        self.system_prompt = system_prompt or self._default_system_prompt()
        # Utiliser le workspace_dir si fourni, sinon utiliser le défaut
        self.filesystem = MCPFilesystem(base_path=workspace_dir or "./workspace")
    
    def _default_system_prompt(self) -> str:
        """Retourne le prompt système par défaut pour un Worker."""
        return f"""Tu es un agent Worker spécialisé dans le rôle: {self.role}.

Tu as reçu une mission spécifique à accomplir. Utilise tes capacités pour:
- Analyser les informations fournies
- Traiter les données nécessaires
- Produire un résultat clair et structuré

Si tu as besoin d'informations supplémentaires ou si les instructions sont floues,
demande des clarifications dans ta réponse."""
    
    def get_system_prompt(self) -> str:
        """Retourne le prompt système de ce Worker."""
        return self.system_prompt
    
    async def process(self, task: str) -> str:
        """Traite une tâche assignée."""
        self.log_action("Exécution de la tâche", task)
        
        # Enregistrer la tâche dans l'historique
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "task": task
        })
        
        # Analyser la tâche pour extraire les actions de fichiers
        # Détecter les fichiers à lire ou écrire dans la tâche
        import re
        
        # Chercher des références à des fichiers (amélioré pour capturer mieux)
        # Patterns pour fichiers à lire
        read_patterns = [
            r'(?:lire|read|analyse|analyze|lit|reads).*?([a-zA-Z0-9_\-\.]+\.(?:log|txt|md|py|json|csv))',
            r'fichier\s+([a-zA-Z0-9_\-\.]+\.(?:log|txt|md|py|json|csv))',
            r'file\s+([a-zA-Z0-9_\-\.]+\.(?:log|txt|md|py|json|csv))',
        ]
        
        # Patterns pour fichiers à écrire
        write_patterns = [
            r'(?:écrire|write|génère|generate|crée|create|sauvegarde|save).*?([a-zA-Z0-9_\-\.]+\.(?:log|txt|md|py|json|csv))',
            r'dans\s+([a-zA-Z0-9_\-\.]+\.(?:log|txt|md|py|json|csv))',
            r'in\s+([a-zA-Z0-9_\-\.]+\.(?:log|txt|md|py|json|csv))',
        ]
        
        files_to_read = []
        files_to_write = []
        
        for pattern in read_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            files_to_read.extend(matches)
        
        for pattern in write_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            files_to_write.extend(matches)
        
        # Dédupliquer
        files_to_read = list(set(files_to_read))
        files_to_write = list(set(files_to_write))
        
        result_parts = []
        result_parts.append(f"Résultat du travail de {self.role} ({self.name}):\n")
        result_parts.append(f"Mission: {task}\n\n")
        
        # Lire les fichiers demandés
        if files_to_read:
            result_parts.append("📖 Fichiers lus:\n")
            for filename in files_to_read:
                content = self.filesystem.read_file(filename)
                if not content.startswith("Erreur"):
                    result_parts.append(f"- {filename}: {len(content)} caractères\n")
                    # Analyser le contenu selon le type de fichier
                    if filename.endswith('.log'):
                        # Analyse basique des logs
                        errors = content.count('ERROR')
                        warnings = content.count('WARNING')
                        info = content.count('INFO')
                        result_parts.append(f"  → Statistiques: {errors} erreurs, {warnings} warnings, {info} infos\n")
                else:
                    result_parts.append(f"- {filename}: {content}\n")
        
        # Traitement spécifique selon le rôle
        if "log" in task.lower() or "analyste" in self.role.lower():
            # Analyse de logs
            if files_to_read:
                for filename in files_to_read:
                    if filename.endswith('.log'):
                        content = self.filesystem.read_file(filename)
                        if not content.startswith("Erreur"):
                            # Générer un rapport d'analyse
                            report = self._analyze_logs(content, filename)
                            result_parts.append(f"\n📊 Analyse de {filename}:\n{report}\n")
                            
                            # Si un fichier de sortie est demandé, l'écrire
                            if files_to_write:
                                for outfile in files_to_write:
                                    self.filesystem.write_file(outfile, report)
                                    result_parts.append(f"✅ Rapport sauvegardé dans {outfile}\n")
        
        # Si aucun fichier spécifique n'est mentionné, faire un traitement générique
        if not files_to_read and not files_to_write:
            result_parts.append("Traitement effectué:\n")
            result_parts.append("- Analyse de la demande\n")
            result_parts.append("- Exécution des opérations requises\n")
            result_parts.append("- Génération du résultat\n")
        
        result = "".join(result_parts)
        
        self.log_action("Tâche terminée", f"Résultat généré")
        return result
    
    def _analyze_logs(self, log_content: str, filename: str) -> str:
        """Analyse le contenu d'un fichier de log et génère un rapport."""
        lines = log_content.split('\n')
        
        errors = []
        warnings = []
        info_count = 0
        
        for line in lines:
            if 'ERROR' in line:
                errors.append(line.strip())
            elif 'WARNING' in line:
                warnings.append(line.strip())
            elif 'INFO' in line:
                info_count += 1
        
        # Générer le rapport Markdown
        report = f"""# Rapport d'Analyse de Logs: {filename}

## 📊 Statistiques Générales

- **Total de lignes**: {len(lines)}
- **Erreurs (ERROR)**: {len(errors)}
- **Avertissements (WARNING)**: {len(warnings)}
- **Informations (INFO)**: {info_count}

## ❌ Erreurs Détectées

"""
        if errors:
            for i, error in enumerate(errors[:10], 1):  # Limiter à 10 erreurs
                report += f"{i}. {error}\n"
            if len(errors) > 10:
                report += f"\n... et {len(errors) - 10} autres erreurs\n"
        else:
            report += "Aucune erreur détectée.\n"
        
        report += "\n## ⚠️ Avertissements\n\n"
        if warnings:
            for i, warning in enumerate(warnings[:10], 1):
                report += f"{i}. {warning}\n"
            if len(warnings) > 10:
                report += f"\n... et {len(warnings) - 10} autres avertissements\n"
        else:
            report += "Aucun avertissement détecté.\n"
        
        # Analyse des patterns
        report += "\n## 🔍 Analyse des Patterns\n\n"
        
        # Compter les types d'erreurs
        error_types = {}
        for error in errors:
            # Extraire le type d'erreur (après "ERROR:")
            if 'ERROR:' in error:
                error_type = error.split('ERROR:')[1].strip().split(':')[0]
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        if error_types:
            report += "### Types d'erreurs les plus fréquents:\n\n"
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                report += f"- **{error_type}**: {count} occurrence(s)\n"
        
        report += "\n## 💡 Recommandations\n\n"
        if len(errors) > 5:
            report += "- ⚠️ Nombre élevé d'erreurs détecté. Investigation recommandée.\n"
        if len(warnings) > 10:
            report += "- ⚠️ Nombre élevé d'avertissements. Revue de la configuration recommandée.\n"
        if not errors and not warnings:
            report += "- ✅ Aucun problème détecté. Le système fonctionne normalement.\n"
        
        return report
    
    async def execute(self, task: str) -> str:
        """Alias pour compatibilité avec l'ancienne interface."""
        return await self.process(task)
    
    def log_action(self, action: str, details: str = None):
        """Override pour un formatage spécifique aux Workers."""
        indent = "  " * (self.depth + 1)
        print(f"{indent}└─> [{self.name} - {self.role}] {action}: {details}")
        
        # Appeler aussi la méthode parent pour le logging complet
        super().log_action(action, details)