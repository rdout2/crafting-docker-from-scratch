#!/usr/bin/env python3
"""
Commande run pour mini-docker
Gère l'exécution des conteneurs avec isolation des namespaces et cgroups
"""

import os
import sys
import signal
import time
from container.process import ContainerProcess
from cgroups.manager import CgroupManager


def parse_memory_limit(memory_str):
    """Parse une chaîne de limite de mémoire (ex: '100M', '1G') en bytes"""
    if not memory_str:
        return None
    
    memory_str = memory_str.upper()
    if memory_str.endswith('K'):
        return int(memory_str[:-1]) * 1024
    elif memory_str.endswith('M'):
        return int(memory_str[:-1]) * 1024 * 1024
    elif memory_str.endswith('G'):
        return int(memory_str[:-1]) * 1024 * 1024 * 1024
    else:
        # Assume bytes
        return int(memory_str)


def setup_signal_handlers(container_process):
    """Configure les gestionnaires de signaux pour la propreté"""
    def signal_handler(signum, frame):
        print(f"\nReçu le signal {signum}, arrêt du conteneur...")
        container_process.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def run_command(args):
    """Exécute la commande run avec les paramètres donnés"""
    print(f"🚀 Démarrage du conteneur avec la commande: {args.image}")
    
    # Validation des paramètres
    if not os.path.exists(args.rootfs):
        print(f"❌ Erreur: Le rootfs '{args.rootfs}' n'existe pas")
        sys.exit(1)
    
    # Parse des limites de ressources
    memory_limit = parse_memory_limit(args.memory)
    
    try:
        # Création du gestionnaire de cgroups
        cgroup_manager = None
        if memory_limit or args.cpus:
            cgroup_manager = CgroupManager()
            container_id = f"mini-docker-{int(time.time())}"
            cgroup_manager.create_cgroup(container_id)
            
            if memory_limit:
                print(f"📊 Limite de mémoire: {args.memory}")
                cgroup_manager.set_memory_limit(container_id, memory_limit)
            
            if args.cpus:
                print(f"⚡ Limite de CPU: {args.cpus} cœurs")
                cgroup_manager.set_cpu_limit(container_id, args.cpus)
        
        # Création et configuration du processus conteneur
        container = ContainerProcess(
            rootfs=args.rootfs,
            hostname=args.hostname,
            cgroup_manager=cgroup_manager,
            container_id=container_id if cgroup_manager else None
        )
        
        # Configuration des gestionnaires de signaux
        setup_signal_handlers(container)
        
        # Exécution du conteneur
        print("🔒 Création des namespaces et isolation...")
        container.run(args.image, args.args)
        
    except PermissionError:
        print("❌ Erreur: Permissions insuffisantes. Exécutez avec sudo.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du conteneur: {e}")
        if cgroup_manager and 'container_id' in locals():
            cgroup_manager.cleanup(container_id)
        sys.exit(1)
