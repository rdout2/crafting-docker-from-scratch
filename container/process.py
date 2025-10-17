#!/usr/bin/env python3
"""
Process and namespace management for mini-docker
Uses os.fork() and os.unshare() to create isolation
"""

import os
import sys
import signal
import subprocess
from typing import Optional, List


class ContainerProcess:
    """Manage execution of a process in an isolated container"""
    
    def __init__(self, rootfs: str, hostname: Optional[str] = None, 
                 cgroup_manager=None, container_id: Optional[str] = None):
        self.rootfs = rootfs
        self.hostname = hostname
        self.cgroup_manager = cgroup_manager
        self.container_id = container_id
        self.child_pid = None
    
    def run(self, command: str, args: List[str] = None):
        """Execute the command inside the isolated container"""
        if args is None:
            args = []
        
        # Création du processus enfant avec fork
        self.child_pid = os.fork()
        
        if self.child_pid == 0:
            # Child process - set up isolation
            self._setup_container()
            self._execute_command(command, args)
        else:
            # Parent process - manage the container
            self._manage_container()
    
    def _setup_container(self):
        """Configure container isolation in the child process"""
        try:
            # Create new namespaces
            self._create_namespaces()
            
            # Change root (chroot)
            self._setup_rootfs()
            
            # Configure hostname
            if self.hostname:
                self._set_hostname()
            
            # Apply cgroup limits
            if self.cgroup_manager and self.container_id:
                self.cgroup_manager.add_process_to_cgroup(
                    self.container_id, os.getpid()
                )
            
            print("✅ Container configured successfully")
            
        except Exception as e:
            print(f"❌ Error while configuring the container: {e}")
            sys.exit(1)
    
    def _create_namespaces(self):
        """Create new namespaces for isolation"""
        # Flags for namespaces (Linux)
        namespace_flags = 0
        
        # PID namespace for process isolation
        namespace_flags |= os.CLONE_NEWPID
        
        # UTS namespace for hostname isolation
        namespace_flags |= os.CLONE_NEWUTS
        
        # NET namespace for network isolation (if needed)
        # namespace_flags |= os.CLONE_NEWNET
        
        # MNT namespace for mount isolation
        namespace_flags |= os.CLONE_NEWNS
        
        # Create the new namespaces
        os.unshare(namespace_flags)
        print("🔒 Namespaces created successfully")
    
    def _setup_rootfs(self):
        """Configure the root filesystem (chroot)"""
        # Change to the new rootfs
        os.chroot(self.rootfs)
        
        # Change working directory to the new root
        os.chdir('/')
        
        print(f"📁 Rootfs configured: {self.rootfs}")
    
    def _set_hostname(self):
        """Configure the container hostname"""
        try:
            # Write the new hostname
            with open('/proc/sys/kernel/hostname', 'w') as f:
                f.write(self.hostname)
            print(f"🏷️  Hostname configured: {self.hostname}")
        except PermissionError:
            print("⚠️  Unable to change hostname (permissions)")
    
    def _execute_command(self, command: str, args: List[str]):
        """Execute the command inside the container"""
        try:
            # Construction de la commande complète
            full_command = [command] + args
            
            print(f"▶️  Executing: {' '.join(full_command)}")
            
            # Exécution de la commande
            os.execvp(command, full_command)
            
        except FileNotFoundError:
            print(f"❌ Command not found: {command}")
            sys.exit(127)  # Code d'erreur standard pour "command not found"
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            sys.exit(1)
    
    def _manage_container(self):
        """Manage the container from the parent process"""
        try:
            # Wait for the child process to finish
            pid, status = os.waitpid(self.child_pid, 0)
            
            # Display exit code
            exit_code = os.WEXITSTATUS(status)
            if exit_code == 0:
                print("✅ Container finished successfully")
            else:
                print(f"❌ Container exited with error code: {exit_code}")
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping container...")
            self.cleanup()
        except Exception as e:
            print(f"❌ Error while managing the container: {e}")
            self.cleanup()
    
    def cleanup(self):
        """Clean up container resources"""
        if self.child_pid:
            try:
                # Send SIGTERM to the child process
                os.kill(self.child_pid, signal.SIGTERM)
                
                # Wait for the process to finish
                os.waitpid(self.child_pid, 0)
                
            except ProcessLookupError:
                # The process is already finished
                pass
        
        # Clean up cgroup
        if self.cgroup_manager and self.container_id:
            self.cgroup_manager.cleanup(self.container_id)
        
        print("🧹 Resources cleaned up")
