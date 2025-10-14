#!/usr/bin/env python3
"""
Gestion des processus et namespaces pour mini-docker
Utilise os.fork() et os.unshare() pour créer l'isolation
"""

import os
import sys
import signal
import subprocess
from typing import Optional, List


class ContainerProcess:
    """Gère l'exécution d'un processus dans un conteneur isolé"""
    
    def __init__(self, rootfs: str, hostname: Optional[str] = None, 
                 cgroup_manager=None, container_id: Optional[str] = None):
        self.rootfs = rootfs
        self.hostname = hostname
        self.cgroup_manager = cgroup_manager
        self.container_id = container_id
        self.child_pid = None
    
    def run(self, command: str, args: List[str] = None):
        """Exécute la commande dans le conteneur isolé"""
        if args is None:
            args = []
        
        # Création du processus enfant avec fork
        self.child_pid = os.fork()
        
        if self.child_pid == 0:
            # Processus enfant - configuration de l'isolation
            self._setup_container()
            self._execute_command(command, args)
        else:
            # Processus parent - gestion du conteneur
            self._manage_container()
    
    def _setup_container(self):
        """Configure l'isolation du conteneur dans le processus enfant"""
        try:
            # Création des nouveaux namespaces
            self._create_namespaces()
            
            # Changement de racine (chroot)
            self._setup_rootfs()
            
            # Configuration du hostname
            if self.hostname:
                self._set_hostname()
            
            # Application des limites de cgroups
            if self.cgroup_manager and self.container_id:
                self.cgroup_manager.add_process_to_cgroup(
                    self.container_id, os.getpid()
                )
            
            print("✅ Conteneur configuré avec succès")
            
        except Exception as e:
            print(f"❌ Erreur lors de la configuration du conteneur: {e}")
            sys.exit(1)
    
    def _create_namespaces(self):
        """Crée les nouveaux namespaces pour l'isolation"""
        # Flags pour les namespaces (Linux)
        namespace_flags = 0
        
        # Namespace PID pour l'isolation des processus
        namespace_flags |= os.CLONE_NEWPID
        
        # Namespace UTS pour l'isolation du hostname
        namespace_flags |= os.CLONE_NEWUTS
        
        # Namespace NET pour l'isolation réseau (si nécessaire)
        # namespace_flags |= os.CLONE_NEWNET
        
        # Namespace MNT pour l'isolation des points de montage
        namespace_flags |= os.CLONE_NEWNS
        
        # Création des nouveaux namespaces
        os.unshare(namespace_flags)
        print("🔒 Namespaces créés avec succès")
    
    def _setup_rootfs(self):
        """Configure le système de fichiers racine (chroot)"""
        # Changement vers le nouveau rootfs
        os.chroot(self.rootfs)
        
        # Changement du répertoire de travail vers la nouvelle racine
        os.chdir('/')
        
        print(f"📁 Rootfs configuré: {self.rootfs}")
    
    def _set_hostname(self):
        """Configure le hostname du conteneur"""
        try:
            # Écriture du nouveau hostname
            with open('/proc/sys/kernel/hostname', 'w') as f:
                f.write(self.hostname)
            print(f"🏷️  Hostname configuré: {self.hostname}")
        except PermissionError:
            print("⚠️  Impossible de changer le hostname (permissions)")
    
    def _execute_command(self, command: str, args: List[str]):
        """Exécute la commande dans le conteneur"""
        try:
            # Construction de la commande complète
            full_command = [command] + args
            
            print(f"▶️  Exécution: {' '.join(full_command)}")
            
            # Exécution de la commande
            os.execvp(command, full_command)
            
        except FileNotFoundError:
            print(f"❌ Commande non trouvée: {command}")
            sys.exit(127)  # Code d'erreur standard pour "command not found"
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution: {e}")
            sys.exit(1)
    
    def _manage_container(self):
        """Gère le conteneur depuis le processus parent"""
        try:
            # Attente de la fin du processus enfant
            pid, status = os.waitpid(self.child_pid, 0)
            
            # Affichage du code de sortie
            exit_code = os.WEXITSTATUS(status)
            if exit_code == 0:
                print("✅ Conteneur terminé avec succès")
            else:
                print(f"❌ Conteneur terminé avec le code d'erreur: {exit_code}")
            
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du conteneur...")
            self.cleanup()
        except Exception as e:
            print(f"❌ Erreur lors de la gestion du conteneur: {e}")
            self.cleanup()
    
    def cleanup(self):
        """Nettoie les ressources du conteneur"""
        if self.child_pid:
            try:
                # Envoi du signal SIGTERM au processus enfant
                os.kill(self.child_pid, signal.SIGTERM)
                
                # Attente de la fin du processus
                os.waitpid(self.child_pid, 0)
                
            except ProcessLookupError:
                # Le processus est déjà terminé
                pass
        
        # Nettoyage des cgroups
        if self.cgroup_manager and self.container_id:
            self.cgroup_manager.cleanup(self.container_id)
        
        print("🧹 Ressources nettoyées")
