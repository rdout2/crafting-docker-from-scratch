# Rootfs Alpine Linux

Ce dossier contient le système de fichiers racine Alpine Linux pour mini-docker.

## Installation

Pour installer Alpine Linux dans ce dossier, vous pouvez :

1. **Télécharger une image Alpine existante :**
   ```bash
   # Télécharger une image Alpine minimale
   wget http://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-minirootfs-3.18.4-x86_64.tar.gz
   
   # Extraire dans le dossier rootfs/alpine
   tar -xzf alpine-minirootfs-3.18.4-x86_64.tar.gz -C /Users/rouchadahmat/qbs/test/mini-docker/rootfs/alpine
   ```

2. **Utiliser Docker pour créer le rootfs :**
   ```bash
   # Créer un conteneur Alpine temporaire
   docker run --name alpine-temp alpine:latest sh -c "echo 'Alpine Linux ready'"
   
   # Copier le système de fichiers
   docker cp alpine-temp:/ /Users/rouchadahmat/qbs/test/mini-docker/rootfs/alpine
   
   # Nettoyer
   docker rm alpine-temp
   ```

3. **Utiliser debootstrap pour une installation complète :**
   ```bash
   # Installation d'une distribution minimale
   sudo debootstrap --variant=minbase alpine /Users/rouchadahmat/qbs/test/mini-docker/rootfs/alpine
   ```

## Structure attendue

Le dossier doit contenir la structure typique d'un système Linux :
```
alpine/
├── bin/           # Binaires système
├── etc/           # Configuration
├── lib/           # Bibliothèques
├── proc/          # Système de fichiers proc
├── sys/           # Système de fichiers sys
├── tmp/           # Dossier temporaire
├── usr/           # Programmes utilisateur
└── var/           # Données variables
```

## Notes

- Assurez-vous que le rootfs contient les binaires nécessaires (sh, ls, etc.)
- Le système doit être compatible avec l'architecture de votre machine
- Les permissions doivent être correctement définies pour le chroot
