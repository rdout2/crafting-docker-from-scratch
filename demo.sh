#!/bin/bash

# Demo script for mini-docker
# Make sure you have configured the Alpine rootfs before running

echo "🐳 Mini-Docker Demo"
echo "================================"

# Prerequisite checks
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run with sudo"
    exit 1
fi

if [ ! -d "./rootfs/alpine/bin" ]; then
    echo "❌ Alpine rootfs not configured. Please follow the README instructions."
    exit 1
fi

echo "✅ Prerequisites verified"

# Test 1: Simple command
echo ""
echo "🧪 Test 1: Simple command (ls)"
python3 main.py run /bin/ls -la /

# Test 2: Custom hostname
echo ""
echo "🧪 Test 2: Custom hostname"
python3 main.py run --hostname mon-conteneur /bin/hostname

# Test 3: Memory limit
echo ""
echo "🧪 Test 3: Memory limit (100M)"
python3 main.py run --memory 100M /bin/sh -c "echo 'Test with memory limit'"

# Test 4: CPU limit
echo ""
echo "🧪 Test 4: CPU limit (0.5 cores)"
python3 main.py run --cpus 0.5 /bin/sh -c "echo 'Test with CPU limit'"

# Test 5: Combined limits
echo ""
echo "🧪 Test 5: Memory + CPU + hostname"
python3 main.py run --memory 200M --cpus 1.0 --hostname test-container /bin/sh -c "echo 'Full test' && /bin/hostname"

echo ""
echo "✅ Demo finished"
echo ""
echo "💡 For more examples, see README.md"
