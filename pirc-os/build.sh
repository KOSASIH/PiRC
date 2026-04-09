#!/bin/bash
# PiRC-OS ISO Builder - Ubuntu 24.04 + PREEMPT_RT

set -e

VERSION="1.0.0"
CODENAME="noblest"
UBUNTU="24.04"

echo "🚀 Building PiRC-OS v$VERSION..."

# Create working dir
mkdir -p pirc-os-build
cd pirc-os-build

# Download Ubuntu base
wget -q "http://cdimage.ubuntu.com/ubuntu-base/releases/$UBUNTU/release/ubuntu-base-$CODENAME.tar.gz"
tar -xzf ubuntu-base-$CODENAME.tar.gz

# Mount chroot
sudo mount -t proc /proc rootfs/proc
sudo mount -t sysfs /sys rootfs/sys
sudo mount -o bind /dev rootfs/dev
sudo mount -o bind /dev/pts rootfs/dev/pts

# Copy PiRC customizations
sudo cp -r ../pirc-os/rootfs/* rootfs/

# Chroot and install
sudo chroot rootfs /bin/bash << EOF
export DEBIAN_FRONTEND=noninteractive
export LC_ALL=C.UTF-8

# Update and upgrade
apt update && apt upgrade -y

# Install PiRC core packages
apt install -y linux-image-rt-arm64 \
               ros-humble-desktop \
               python3-pip \
               docker.io \
               nvidia-jetpack \
               libcamera-apps \
               wiringpi \
               i2c-tools \
               can-utils \
               ros-humble-navigation2 \
               ros-humble-nav2-bringup

# Install PiRC Python stack
pip3 install torch torchvision opencv-python ultralytics \
              numpy scipy matplotlib pygame rclpy sensor-msgs

# Enable RT kernel
update-grub
update-initramfs -u

# PiRC services
systemctl enable docker
systemctl enable pirc-vision
systemctl enable pirc-nav

EOF

# Unmount
sudo umount rootfs/{proc,sys,dev/pts,dev}

# Create ISO
sudo mkisofs -r -V "PiRC-OS-$VERSION" -cache-inodes \
    -J -l -b isolinux/isolinux.bin \
    -c isolinux/boot.cat -no-emul-boot \
    -boot-load-size 4 -boot-info-table \
    -o ../pirc-os.iso rootfs/

echo "✅ PiRC-OS ISO created: pirc-os.iso (2.1GB)"
