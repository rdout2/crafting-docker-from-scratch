#!/usr/bin/env python3
"""
Mini-Docker - A simple container in Python
Main entry point with argparse to handle commands
"""

import argparse
import sys
import os

# Add the project directory to sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cmd.run import run_command


def main():
    """Main entry point of mini-docker"""
    parser = argparse.ArgumentParser(
        description="Mini-Docker - A simple container in Python",
        prog="mini-docker"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Execute a command in a container')
    run_parser.add_argument('--memory', '-m', type=str, 
                          help='Memory limit (e.g., 100M, 1G)')
    run_parser.add_argument('--cpus', '-c', type=float,
                          help='CPU limit (number of cores)')
    run_parser.add_argument('--rootfs', type=str, default='./rootfs/alpine',
                          help='Path to the rootfs (default: ./rootfs/alpine)')
    run_parser.add_argument('--hostname', type=str,
                          help='Container hostname')
    run_parser.add_argument('--network', type=str, default='none',
                          help='Network configuration (none, host, bridge)')
    run_parser.add_argument('image', help='Image or command to execute')
    run_parser.add_argument('args', nargs='*', help='Arguments for the command')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        run_command(args)
    elif args.command == 'version':
        print("Mini-Docker v1.0.0")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
