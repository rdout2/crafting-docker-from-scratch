#!/usr/bin/env python3
"""
Cgroup manager for mini-docker
Interacts with the virtual filesystem /sys/fs/cgroup to control resources
"""

import os
import shutil
from typing import Optional


class CgroupManager:
    """Manage cgroups to limit container resources"""
    
    def __init__(self):
        self.cgroup_root = "/sys/fs/cgroup"
        self.mini_docker_group = "mini-docker"
        self._ensure_mini_docker_group()
    
    def _ensure_mini_docker_group(self):
        """Ensure the mini-docker cgroup exists"""
        mini_docker_path = os.path.join(self.cgroup_root, self.mini_docker_group)
        if not os.path.exists(mini_docker_path):
            os.makedirs(mini_docker_path, exist_ok=True)
            print(f"📁 Cgroup group created: {mini_docker_path}")
    
    def create_cgroup(self, container_id: str) -> str:
        """Create a new cgroup for the container"""
        cgroup_path = os.path.join(
            self.cgroup_root, 
            self.mini_docker_group, 
            container_id
        )
        
        # Create the cgroup directory
        os.makedirs(cgroup_path, exist_ok=True)
        
        print(f"📦 Cgroup created: {cgroup_path}")
        return cgroup_path
    
    def set_memory_limit(self, container_id: str, memory_bytes: int):
        """Set the memory limit for the container"""
        cgroup_path = self._get_cgroup_path(container_id)
        
        # Write the memory limit
        memory_limit_file = os.path.join(cgroup_path, "memory.limit_in_bytes")
        try:
            with open(memory_limit_file, 'w') as f:
                f.write(str(memory_bytes))
            print(f"💾 Memory limit set: {memory_bytes} bytes")
        except PermissionError:
            print("⚠️  Insufficient permissions to set memory limit")
        except Exception as e:
            print(f"❌ Error while setting memory limit: {e}")
    
    def set_cpu_limit(self, container_id: str, cpu_cores: float):
        """Set the CPU limit for the container"""
        cgroup_path = self._get_cgroup_path(container_id)
        
        # Convert to microseconds (CPU quota = cores * 100000)
        cpu_quota = int(cpu_cores * 100000)
        
        try:
            # Set CPU quota
            cpu_quota_file = os.path.join(cgroup_path, "cpu.cfs_quota_us")
            with open(cpu_quota_file, 'w') as f:
                f.write(str(cpu_quota))
            
            # Set CPU period (100ms default)
            cpu_period_file = os.path.join(cgroup_path, "cpu.cfs_period_us")
            with open(cpu_period_file, 'w') as f:
                f.write("100000")  # 100ms
            
            print(f"⚡ CPU limit set: {cpu_cores} cores")
            
        except PermissionError:
            print("⚠️  Insufficient permissions to set CPU limit")
        except Exception as e:
            print(f"❌ Error while setting CPU limit: {e}")
    
    def add_process_to_cgroup(self, container_id: str, pid: int):
        """Add a process to the cgroup"""
        cgroup_path = self._get_cgroup_path(container_id)
        
        # Add the PID to the cgroup
        cgroup_procs_file = os.path.join(cgroup_path, "cgroup.procs")
        
        try:
            with open(cgroup_procs_file, 'w') as f:
                f.write(str(pid))
            print(f"🔗 Process {pid} added to cgroup")
        except PermissionError:
            print("⚠️  Insufficient permissions to add process to cgroup")
        except Exception as e:
            print(f"❌ Error while adding process to cgroup: {e}")
    
    def get_memory_usage(self, container_id: str) -> Optional[int]:
        """Get current memory usage of the container"""
        cgroup_path = self._get_cgroup_path(container_id)
        memory_usage_file = os.path.join(cgroup_path, "memory.usage_in_bytes")
        
        try:
            with open(memory_usage_file, 'r') as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return None
    
    def get_cpu_usage(self, container_id: str) -> Optional[dict]:
        """Get current CPU usage of the container"""
        cgroup_path = self._get_cgroup_path(container_id)
        
        try:
            # Read cpuacct.stat file
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
        """Clean up the container's cgroup"""
        cgroup_path = self._get_cgroup_path(container_id)
        
        try:
            # Remove all processes from the cgroup
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
            
            # Remove the cgroup directory
            if os.path.exists(cgroup_path):
                shutil.rmtree(cgroup_path)
                print(f"🧹 Cgroup cleaned: {container_id}")
                
        except PermissionError:
            print("⚠️  Insufficient permissions to clean the cgroup")
        except Exception as e:
            print(f"❌ Error while cleaning the cgroup: {e}")
    
    def _get_cgroup_path(self, container_id: str) -> str:
        """Return the full path to the container's cgroup"""
        return os.path.join(
            self.cgroup_root,
            self.mini_docker_group,
            container_id
        )
    
    def list_containers(self):
        """List all active containers"""
        mini_docker_path = os.path.join(self.cgroup_root, self.mini_docker_group)
        
        if not os.path.exists(mini_docker_path):
            return []
        
        containers = []
        for item in os.listdir(mini_docker_path):
            container_path = os.path.join(mini_docker_path, item)
            if os.path.isdir(container_path):
                containers.append(item)
        
        return containers
