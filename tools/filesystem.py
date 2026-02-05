import os
from typing import List, Dict, Any
from pathlib import Path


class MCPFilesystem:
    """Gestionnaire de fichiers sécurisé simulant un serveur MCP."""
    
    def __init__(self, base_path: str = "./workspace"):
        self.base_path = os.path.abspath(base_path)
        os.makedirs(self.base_path, exist_ok=True)
    
    def _validate_path(self, filepath: str) -> str:
        """Valide et sécurise un chemin pour empêcher les sorties du workspace."""
        # Résoudre le chemin relatif
        if os.path.isabs(filepath):
            # Si c'est un chemin absolu, vérifier qu'il est dans base_path
            resolved = os.path.abspath(filepath)
        else:
            # Chemin relatif
            resolved = os.path.abspath(os.path.join(self.base_path, filepath))
        
        # Vérifier que le chemin résolu est bien dans base_path
        if not resolved.startswith(self.base_path):
            raise ValueError(
                f"Accès refusé: tentative d'accès hors du workspace "
                f"({filepath} -> {resolved})"
            )
        
        return resolved
    
    def read_file(self, filename: str) -> str:
        """
        Lit le contenu d'un fichier depuis le workspace.
        
        Args:
            filename: Nom du fichier (relatif au workspace)
            
        Returns:
            Contenu du fichier ou message d'erreur
        """
        try:
            filepath = self._validate_path(filename)
            
            if not os.path.exists(filepath):
                return f"Erreur: Fichier '{filename}' introuvable dans le workspace."
            
            if not os.path.isfile(filepath):
                return f"Erreur: '{filename}' n'est pas un fichier."
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            return content
            
        except ValueError as e:
            return f"Erreur de sécurité: {str(e)}"
        except Exception as e:
            return f"Erreur lors de la lecture: {str(e)}"
    
    def write_file(self, filename: str, content: str) -> str:
        """
        Écrit du contenu dans un fichier du workspace.
        
        Args:
            filename: Nom du fichier (relatif au workspace)
            content: Contenu à écrire
            
        Returns:
            Message de confirmation ou d'erreur
        """
        try:
            filepath = self._validate_path(filename)
            
            # Créer les répertoires parents si nécessaire
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            return f"Fichier '{filename}' écrit avec succès ({len(content)} caractères)."
            
        except ValueError as e:
            return f"Erreur de sécurité: {str(e)}"
        except Exception as e:
            return f"Erreur lors de l'écriture: {str(e)}"
    
    def list_files(self, path: str = "") -> str:
        """
        Liste les fichiers et répertoires dans le workspace.
        
        Args:
            path: Chemin relatif à explorer (vide pour la racine)
            
        Returns:
            Liste formatée des fichiers et répertoires
        """
        try:
            dirpath = self._validate_path(path)
            
            if not os.path.exists(dirpath):
                return f"Erreur: Chemin '{path}' introuvable."
            
            if not os.path.isdir(dirpath):
                return f"Erreur: '{path}' n'est pas un répertoire."
            
            items = []
            for item in sorted(os.listdir(dirpath)):
                item_path = os.path.join(dirpath, item)
                rel_path = os.path.relpath(item_path, self.base_path)
                
                if os.path.isdir(item_path):
                    items.append(f"[DIR]  {rel_path}/")
                else:
                    size = os.path.getsize(item_path)
                    items.append(f"[FILE] {rel_path} ({size} bytes)")
            
            if not items:
                return f"Le répertoire '{path}' est vide."
            
            return "\n".join(items)
            
        except ValueError as e:
            return f"Erreur de sécurité: {str(e)}"
        except Exception as e:
            return f"Erreur lors de la liste: {str(e)}"
    
    def write_report(self, filename: str, content: str) -> str:
        """Alias pour compatibilité avec l'ancienne interface."""
        return self.write_file(filename, content)

