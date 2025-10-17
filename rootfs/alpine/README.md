# Alpine Linux Rootfs

This folder contains the Alpine Linux root filesystem for mini-docker.

## Installation

To install Alpine Linux in this folder, you can:

1. **Download an existing Alpine image:**
   ```bash
   # Download a minimal Alpine image
   wget http://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-minirootfs-3.18.4-x86_64.tar.gz
   
   # Extract into the rootfs/alpine folder
   tar -xzf alpine-minirootfs-3.18.4-x86_64.tar.gz -C /Users/rouchadahmat/qbs/test/mini-docker/rootfs/alpine
   ```

2. **Use Docker to create the rootfs:**
   ```bash
   # Create a temporary Alpine container
   docker run --name alpine-temp alpine:latest sh -c "echo 'Alpine Linux ready'"
   
   # Copy the filesystem
   docker cp alpine-temp:/ /Users/rouchadahmat/qbs/test/mini-docker/rootfs/alpine
   
   # Clean up
   docker rm alpine-temp
   ```

3. **Use debootstrap for a full installation:**
   ```bash
   # Install a minimal distribution
   sudo debootstrap --variant=minbase alpine /Users/rouchadahmat/qbs/test/mini-docker/rootfs/alpine
   ```

## Expected structure

The folder should contain the typical structure of a Linux system:
```
alpine/
├── bin/           # System binaries
├── etc/           # Configuration
├── lib/           # Libraries
├── proc/          # proc filesystem
├── sys/           # sys filesystem
├── tmp/           # Temporary directory
├── usr/           # User programs
└── var/           # Variable data
```

## Notes

- Ensure the rootfs contains the necessary binaries (sh, ls, etc.)
- The system must be compatible with your machine's architecture
- Permissions must be correctly set for chroot
