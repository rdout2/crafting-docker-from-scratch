#!/usr/bin/env python3
"""
Gestionnaire de cgroups pour mini-docker
Interagit avec le système de fichiers virtuel /sys/fs/cgroup pour contrôler les ressources
"""

import os
import shutil
from typing import Optional


class CgroupManager:
    """Gère les cgroups pour limiter les ressources des conteneurs"""
    
    def __init__(self):
        self.cgroup_root = "/sys/fs/cgroup"
        self.mini_docker_group = "mini-docker"
        self._ensure_mini_docker_group()
    
    def _ensure_mini_docker_group(self):
        """S'assure que le groupe mini-docker existe"""
        mini_docker_path = os.path.join(self.cgroup_root, self.mini_docker_group)
        if not os.path.exists(mini_docker_path):
            os.makedirs(mini_docker_path, exist_ok=True)
            print(f"📁 Groupe cgroup créé: {mini_docker_path}")
    
    def create_cgroup(self, container_id: str) -> str:
        """Crée un nouveau cgroup pour le conteneur"""
        cgroup_path = os.path.join(
            self.cgroup_root, 
            self.mini_docker_group, 
            container_id
        )
        
        # Création du répertoire du cgroup
        os.makedirs(cgroup_path, exist_ok=True)
        
        print(f"📦 Cgroup créé: {cgroup_path}")
        return cgroup_path
    
    def set_memory_limit(self, container_id: str, memory_bytes: int):
        """Définit la limite de mémoire pour le conteneur"""
        cgroup_path = self._get_cgroup_path(container_id)
        
        # Écriture de la limite de mémoire
        memory_limit_file = os.path.join(cgroup_path, "memory.limit_in_bytes")
        try:
            with open(memory_limit_file, 'w') as f:
                f.write(str(memory_bytes))
            print(f"💾 Limite de mémoire définie: {memory_bytes} bytes")
        except PermissionError:
            print("⚠️  Permissions insuffisantes pour définir la limite de mémoire")
        except Exception as e:
            print(f"❌ Erreur lors de la définition de la limite de mémoire: {e}")
    
    def set_cpu_limit(self, container_id: str, cpu_cores: float):
        """Définit la limite de CPU pour le conteneur"""
        cgroup_path = self._get_cgroup_path(container_id)
        
        # Conversion en millisecondes (CPU quota = cores * 100000)
        cpu_quota = int(cpu_cores * 100000)
        
        try:
            # Définition du quota CPU
            cpu_quota_file = os.path.join(cgroup_path, "cpu.cfs_quota_us")
            with open(cpu_quota_file, 'w') as f:
                f.write(str(cpu_quota))
            
            # Définition de la période CPU (100ms par défaut)
            cpu_period_file = os.path.join(cgroup_path, "cpu.cfs_period_us")
            with open(cpu_period_file, 'w') as f:
                f.write("100000")  # 100ms
            
            print(f"⚡ Limite de CPU définie: {cpu_cores} cœurs")
            
        except PermissionError:
            print("⚠️  Permissions insuffisantes pour définir la limite de CPU")
        except Exception as e:
            print(f"❌ Erreur lors de la définition de la limite de CPU: {e}")
    
    def add_process_to_cgroup(self, container_id: str, pid: int):
        """Ajoute un processus au cgroup"""
        cgroup_path = self._get_cgroup_path(container_id)
        
        # Ajout du PID au cgroup
        cgroup_procs_file = os.path.join(cgroup_path, "cgroup.procs")
        
        try:
            with open(cgroup_procs_file, 'w') as f:
                f.write(str(pid))
            print(f"🔗 Processus {pid} ajouté au cgroup")
        except PermissionError:
            print("⚠️  Permissions insuffisantes pour ajouter le processus au cgroup")
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout du processus au cgroup: {e}")
    
    def get_memory_usage(self, container_id: str) -> Optional[int]:
        """Récupère l'utilisation mémoire actuelle du conteneur"""
        cgroup_path = self._get_cgroup_path(container_id)
        memory_usage_file = os.path.join(cgroup_path, "memory.usage_in_bytes")
        
        try:
            with open(memory_usage_file, 'r') as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return None
    
    def get_cpu_usage(self, container_id: str) -> Optional[dict]:
        """Récupère l'utilisation CPU actuelle du conteneur"""
        cgroup_path = self._get_cgroup_path(container_id)
        
        try:
            # Lecture du fichier cpuacct.stat
            cpuacct_stat_file = os.path.join(cgroup_path, "cpuacct.stat")
            if os.path.exists(cpuacct_stat_file):
                with open(cpuacct_stat_file, 'r') as f:
                    lines = f.readlines()
                    cpu_data = {}
                    for line in lines:
                        key, value = line.strip().split()
                        cpu_data[key] = int(value)
                    return cpu_data
        except Exception:
            pass
        
        return None
    
    def cleanup(self, container_id: str):
        """Nettoie le cgroup du conteneur"""
        cgroup_path = self._get_cgroup_path(container_id)
        
        try:
            # Suppression de tous les processus du cgroup
            cgroup_procs_file = os.path.join(cgroup_path, "cgroup.procs")
            if os.path.exists(cgroup_procs_file):
                with open(cgroup_procs_file, 'r') as f:
                    pids = f.read().strip().split('\n')
                    for pid in pids:
                        if pid.strip():
                            try:
                                os.kill(int(pid), 9)  # SIGKILL
                            except (ProcessLookupError, ValueError):
                                pass
            
            # Suppression du répertoire du cgroup
            if os.path.exists(cgroup_path):
                shutil.rmtree(cgroup_path)
                print(f"🧹 Cgroup nettoyé: {container_id}")
                
        except PermissionError:
            print("⚠️  Permissions insuffisantes pour nettoyer le cgroup")
        except Exception as e:
            print(f"❌ Erreur lors du nettoyage du cgroup: {e}")
    
    def _get_cgroup_path(self, container_id: str) -> str:
        """Retourne le chemin complet vers le cgroup du conteneur"""
        return os.path.join(
            self.cgroup_root,
            self.mini_docker_group,
            container_id
        )
    
    def list_containers(self):
        """Liste tous les conteneurs actifs"""
        mini_docker_path = os.path.join(self.cgroup_root, self.mini_docker_group)
        
        if not os.path.exists(mini_docker_path):
            return []
        
        containers = []
        for item in os.listdir(mini_docker_path):
            container_path = os.path.join(mini_docker_path, item)
            if os.path.isdir(container_path):
                containers.append(item)
        
        return containers
