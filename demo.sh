#!/bin/bash

# Script de démonstration pour mini-docker
# Assurez-vous d'avoir configuré le rootfs Alpine avant d'exécuter

echo "🐳 Démonstration de Mini-Docker"
echo "================================"

# Vérification des prérequis
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script doit être exécuté avec sudo"
    exit 1
fi

if [ ! -d "./rootfs/alpine/bin" ]; then
    echo "❌ Rootfs Alpine non configuré. Veuillez suivre les instructions du README."
    exit 1
fi

echo "✅ Prérequis vérifiés"

# Test 1: Commande simple
echo ""
echo "🧪 Test 1: Commande simple (ls)"
python3 main.py run /bin/ls -la /

# Test 2: Hostname personnalisé
echo ""
echo "🧪 Test 2: Hostname personnalisé"
python3 main.py run --hostname mon-conteneur /bin/hostname

# Test 3: Limite de mémoire
echo ""
echo "🧪 Test 3: Limite de mémoire (100M)"
python3 main.py run --memory 100M /bin/sh -c "echo 'Test avec limite mémoire'"

# Test 4: Limite de CPU
echo ""
echo "🧪 Test 4: Limite de CPU (0.5 cœurs)"
python3 main.py run --cpus 0.5 /bin/sh -c "echo 'Test avec limite CPU'"

# Test 5: Combinaison de limites
echo ""
echo "🧪 Test 5: Combinaison mémoire + CPU + hostname"
python3 main.py run --memory 200M --cpus 1.0 --hostname test-conteneur /bin/sh -c "echo 'Test complet' && /bin/hostname"

echo ""
echo "✅ Démonstration terminée"
echo ""
echo "💡 Pour plus d'exemples, consultez le README.md"
