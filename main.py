#!/usr/bin/env python3
"""
Mini-Docker - Un conteneur simple en Python
Point d'entrée principal avec argparse pour gérer les commandes
"""

import argparse
import sys
import os

# Ajouter le répertoire du projet au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cmd.run import run_command


def main():
    """Point d'entrée principal du mini-docker"""
    parser = argparse.ArgumentParser(
        description="Mini-Docker - Un conteneur simple en Python",
        prog="mini-docker"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande run
    run_parser = subparsers.add_parser('run', help='Exécuter une commande dans un conteneur')
    run_parser.add_argument('--memory', '-m', type=str, 
                          help='Limite de mémoire (ex: 100M, 1G)')
    run_parser.add_argument('--cpus', '-c', type=float,
                          help='Limite de CPU (nombre de cœurs)')
    run_parser.add_argument('--rootfs', type=str, default='./rootfs/alpine',
                          help='Chemin vers le rootfs (défaut: ./rootfs/alpine)')
    run_parser.add_argument('--hostname', type=str,
                          help='Nom d\'hôte du conteneur')
    run_parser.add_argument('--network', type=str, default='none',
                          help='Configuration réseau (none, host, bridge)')
    run_parser.add_argument('image', help='Image ou commande à exécuter')
    run_parser.add_argument('args', nargs='*', help='Arguments pour la commande')
    
    # Commande version
    version_parser = subparsers.add_parser('version', help='Afficher la version')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        run_command(args)
    elif args.command == 'version':
        print("Mini-Docker v1.0.0")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
