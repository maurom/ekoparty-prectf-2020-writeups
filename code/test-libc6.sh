#!/bin/bash

apt install busybox-static

mkdir ./mnt
mkdir -p ./mnt/bin ./mnt/dev ./mnt/etc ./mnt/lib/x86_64-linux-gnu/ ./mnt/lib64 ./mnt/usr/lib/x86_64-linux-gnu/ ./mnt/proc ./mnt/sys

dpkg -x ../libc6_2.15-0ubuntu10.18_amd64.deb ./mnt/

mount -o bind,ro /etc ./mnt/etc
mount -o bind /proc ./mnt/proc
mount -o bind /dev ./mnt/dev
mount -o bind /dev/pts ./mnt/dev/pts
mount -o bind /sys ./mnt/sys

cp -via /bin/busybox ./mnt/bin/busybox
cp -vi gdb-7.10.1-x64 ./mnt/bin/gdb
cp -via ../Ropfan ./mnt/bin/

chmod +x ./mnt/bin/Ropfan ./mnt/bin/gdb
cd ./mnt/bin
ln -s busybox ash
ln -s busybox bash
cd ../../

cat <<EOF
Ready
Remember to run
    export SHELL=/bin/ash
before gdb

Now run
    /usr/sbin/chroot ./mnt /bin/busybox ash
EOF
