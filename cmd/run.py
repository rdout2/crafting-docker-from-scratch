#!/usr/bin/env python3
"""
Run command for mini-docker
Manages container execution with namespace and cgroup isolation
"""

import os
import sys
import signal
import time
from container.process import ContainerProcess
from cgroups.manager import CgroupManager


def parse_memory_limit(memory_str):
    """Parse a memory limit string (e.g., '100M', '1G') into bytes"""
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
    """Configure signal handlers for clean shutdown"""
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, stopping container...")
        container_process.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def run_command(args):
    """Execute the run command with the given parameters"""
    print(f"🚀 Starting container with command: {args.image}")
    
    # Validate parameters
    if not os.path.exists(args.rootfs):
        print(f"❌ Error: Rootfs '{args.rootfs}' does not exist")
        sys.exit(1)
    
    # Parse resource limits
    memory_limit = parse_memory_limit(args.memory)
    
    try:
        # Create the cgroup manager
        cgroup_manager = None
        if memory_limit or args.cpus:
            cgroup_manager = CgroupManager()
            container_id = f"mini-docker-{int(time.time())}"
            cgroup_manager.create_cgroup(container_id)
            
            if memory_limit:
                print(f"📊 Memory limit: {args.memory}")
                cgroup_manager.set_memory_limit(container_id, memory_limit)
            
            if args.cpus:
                print(f"⚡ CPU limit: {args.cpus} cores")
                cgroup_manager.set_cpu_limit(container_id, args.cpus)
        
        # Create and configure the container process
        container = ContainerProcess(
            rootfs=args.rootfs,
            hostname=args.hostname,
            cgroup_manager=cgroup_manager,
            container_id=container_id if cgroup_manager else None
        )
        
        # Configure signal handlers
        setup_signal_handlers(container)
        
        # Run the container
        print("🔒 Creating namespaces and isolation...")
        container.run(args.image, args.args)
        
    except PermissionError:
        print("❌ Error: Insufficient permissions. Run with sudo.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error while running the container: {e}")
        if cgroup_manager and 'container_id' in locals():
            cgroup_manager.cleanup(container_id)
        sys.exit(1)
