# Mini-Docker

Un conteneur simple implémenté en Python utilisant les namespaces Linux et les cgroups.

> **Inspiré par le cours "Complete Intro to Containers" de [Brian Holt](https://containers-v2.holt.courses)**  
> Ce projet implémente manuellement les concepts fondamentaux de la conteneurisation présentés dans ce cours exceptionnel.

## 🏗️ Architecture

```
mini-docker/
├── main.py                 # Point d'entrée avec argparse
├── cmd/
│   └── run.py             # Commande run
├── container/
│   └── process.py         # Gestion des processus et namespaces
├── cgroups/
│   └── manager.py         # Gestion des cgroups
└── rootfs/
    └── alpine/            # Système de fichiers racine
```

## 🚀 Installation et Configuration

### 1. Prérequis

- Linux (namespaces et cgroups requis)
- Python 3.6+
- Permissions root (pour les namespaces et cgroups)

### 2. Configuration du Rootfs

```bash
# Télécharger Alpine Linux minimal
wget http://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-minirootfs-3.18.4-x86_64.tar.gz

# Extraire dans le dossier rootfs/alpine
tar -xzf alpine-minirootfs-3.18.4-x86_64.tar.gz -C ./rootfs/alpine
```

### 3. Permissions

```bash
# Rendre le script exécutable
chmod +x main.py

# Exécuter avec sudo (requis pour les namespaces)
sudo python3 main.py
```

## 📖 Utilisation

### Commandes de base

```bash
# Afficher l'aide
sudo python3 main.py --help

# Exécuter une commande simple
sudo python3 main.py run /bin/sh

# Avec limite de mémoire
sudo python3 main.py run --memory 100M /bin/sh

# Avec limite de CPU
sudo python3 main.py run --cpus 0.5 /bin/sh

# Avec hostname personnalisé
sudo python3 main.py run --hostname mon-conteneur /bin/sh

# Commande complexe
sudo python3 main.py run --memory 200M --cpus 1.0 --hostname test /bin/ls -la
```

### Exemples d'utilisation

```bash
# Exploration du système de fichiers
sudo python3 main.py run /bin/ls -la /

# Test de la limite de mémoire
sudo python3 main.py run --memory 50M /bin/sh -c "echo 'Test mémoire limitée'"

# Test de la limite de CPU
sudo python3 main.py run --cpus 0.5 /bin/sh -c "while true; do echo 'CPU limit'; done"

# Hostname personnalisé
sudo python3 main.py run --hostname mon-conteneur /bin/hostname
```

## 🔧 Fonctionnalités

### Namespaces
- **PID Namespace** : Isolation des processus
- **UTS Namespace** : Isolation du hostname
- **Mount Namespace** : Isolation du système de fichiers
- **Network Namespace** : (optionnel) Isolation réseau

### Cgroups
- **Limite de mémoire** : Contrôle de l'utilisation RAM
- **Limite de CPU** : Contrôle de l'utilisation CPU
- **Monitoring** : Suivi des ressources utilisées

### Chroot
- **Isolation du système de fichiers** : Utilisation d'un rootfs Alpine Linux
- **Sécurité** : Limitation de l'accès aux fichiers système

## 🛠️ Développement

### Structure du code

- `main.py` : Point d'entrée avec argparse pour les commandes
- `cmd/run.py` : Logique de la commande run
- `container/process.py` : Gestion des processus et namespaces avec `os.fork()` et `os.unshare()`
- `cgroups/manager.py` : Interaction avec `/sys/fs/cgroup` pour les limites de ressources

### Modules Python utilisés

- `os` : Fork, unshare, chroot, chdir
- `sys` : Gestion des arguments et sorties
- `signal` : Gestion des signaux pour la propreté
- `subprocess` : Exécution de commandes
- `argparse` : Interface en ligne de commande

## ⚠️ Limitations

- Nécessite Linux et les privilèges root
- Namespaces non disponibles sur macOS/Windows
- Rootfs doit être configuré manuellement
- Pas de gestion réseau avancée
- Pas de gestion des volumes persistants

## 🔍 Dépannage

### Erreurs communes

```bash
# Permission denied
sudo python3 main.py run /bin/sh

# Namespace non supporté
# Vérifier que le kernel supporte les namespaces
cat /proc/self/status | grep NStgid

# Rootfs manquant
# S'assurer que ./rootfs/alpine existe et contient un système Linux
ls -la ./rootfs/alpine/bin/
```

### Debug

```bash
# Vérifier les cgroups
ls -la /sys/fs/cgroup/mini-docker/

# Vérifier les processus
ps aux | grep python
```
