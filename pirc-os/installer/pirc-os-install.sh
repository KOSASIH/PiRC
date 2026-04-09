#!/bin/bash
# PiRC-OS USB Installer

TARGET_DEVICE=$1
PIRC_ISO="pirc-os.iso"

if [ -z "$TARGET_DEVICE" ]; then
    echo "Usage: sudo ./pirc-os-install.sh /dev/sdX"
    exit 1
fi

echo "🔥 Flashing PiRC-OS to $TARGET_DEVICE..."

# Validate device
if [ ! -b "$TARGET_DEVICE" ]; then
    echo "❌ Device not found!"
    exit 1
fi

# Write ISO
sudo dd if=$PIRC_ISO of=$TARGET_DEVICE bs=4M status=progress oflag=sync

echo "✅ PiRC-OS flashed! Insert into RPi and boot."
echo "Default login: pi / pirc2024"
