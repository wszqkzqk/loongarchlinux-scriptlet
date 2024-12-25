#!/usr/bin/bash

echo "Building rootfs..."

CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}"
ROOTFS_DIR="$CACHE_DIR/devtools-loong64/rootfs"
mkdir -p "$ROOTFS_DIR"

sudo pacstrap \
    -C /usr/share/devtools/pacman.conf.d/extra-loong64.conf \
    -M \
    "$ROOTFS_DIR" \
    base

echo "Clean up pacman package cache..."
yes y | sudo pacman -Scc --sysroot "$ROOTFS_DIR"

echo "Compressing rootfs to tar.zst..."
# Use pipe instead of buitin compression in bsdtar for better control over compression options
sudo bsdtar --create \
    --xattrs --acls \
     -C "$ROOTFS_DIR/" . \
    | zstd -c -T0 -15 - > \
    "archlinux-bootstrap-$(date +%Y.%m.%d)-loong64.tar.zst"
sha512sum "archlinux-bootstrap-$(date +%Y.%m.%d)-loong64.tar.zst" > "archlinux-bootstrap-$(date +%Y.%m.%d)-loong64.tar.zst.sha512"

echo "Compressing rootfs to squashfs..."
sudo mksquashfs \
    "$ROOTFS_DIR/" \
    "archlinux-bootstrap-$(date +%Y.%m.%d)-loong64.sfs" \
    -comp zstd \
    -Xcompression-level 15
sha512sum "archlinux-bootstrap-$(date +%Y.%m.%d)-loong64.sfs" > "archlinux-bootstrap-$(date +%Y.%m.%d)-loong64.sfs.sha512"

echo "Clean up rootfs directory..."
sudo rm -rf "$ROOTFS_DIR"
