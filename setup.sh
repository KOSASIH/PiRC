#!/bin/bash
# PiRC Complete Setup

echo "🚀 PiRC Super Setup Starting..."

# Clone submodules
git submodule update --init --recursive

# Build PiRC-OS
echo "Building PiRC-OS..."
chmod +x pirc-os/build.sh
./pirc-os/build.sh

# Build Docker images
docker build -f Dockerfile.pirc-os -t pirc/os:latest .
docker build -f Dockerfile.pirc-vision -t pirc/vision:latest ./vision/
docker build -f Dockerfile.pirc-nav -t pirc/navigation:latest ./navigation/

# Create installer
chmod +x pirc-os/installer/pirc-os-install.sh

echo "✅ PiRC-OS READY!"
echo "Flash with: sudo ./pirc-os/installer/pirc-os-install.sh /dev/sdX"
echo "Files created:"
echo "  - pirc-os.iso (Bootable USB)"
echo "  - Docker images: pirc/os, pirc/vision, pirc/nav"
