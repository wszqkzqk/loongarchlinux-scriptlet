#!/usr/bin/bash

echo "Building rootfs..."

BUILD_DATE=$(date +%Y.%m.%d)
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}"
ROOTFS_DIR="$CACHE_DIR/devtools-loong64/root.loong64"
sudo mkdir -p "$ROOTFS_DIR"

sudo pacstrap \
    -C /usr/share/devtools/pacman.conf.d/extra-loong64.conf \
    -M \
    "$ROOTFS_DIR" \
    base arch-install-scripts

echo "Clean up pacman package cache..."
yes y | sudo pacman -Scc --sysroot "$ROOTFS_DIR"

echo "Compressing rootfs to tar.zst..."
# Use pipe instead of buitin compression in bsdtar for better control over compression options
# Upstream's release has a top directory `rootfs.$CARCH` so we also need this
sudo bsdtar --create \
    --xattrs --acls \
    -C "$(dirname "$ROOTFS_DIR")" \
    "$(basename "$ROOTFS_DIR")" \
    | zstd -c -f -T0 -15 - \
    -o "archlinux-bootstrap-${BUILD_DATE}-loong64.tar.zst"
sha512sum "archlinux-bootstrap-${BUILD_DATE}-loong64.tar.zst" > "archlinux-bootstrap-${BUILD_DATE}-loong64.tar.zst.sha512"

echo "Compressing rootfs to squashfs..."
# Uncomment -keep-as-directory will include top directory `rootfs.loong64`
sudo mksquashfs \
    "$ROOTFS_DIR" \
    "archlinux-bootstrap-${BUILD_DATE}-loong64.sfs" \
    -noappend \
    -comp zstd \
    -Xcompression-level 15 #-keep-as-directory
sha512sum "archlinux-bootstrap-${BUILD_DATE}-loong64.sfs" > "archlinux-bootstrap-${BUILD_DATE}-loong64.sfs.sha512"

echo "Clean up rootfs directory..."
sudo rm -rf "$ROOTFS_DIR"
