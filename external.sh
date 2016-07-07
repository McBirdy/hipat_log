#!/usr/bin/env sh
# Test script that will perform actions on the external machine

# Will check for root and change to root user and call script again
[ `whoami` = root ] || exec su -m root -c $0 root
# Rest of the script is now run as root
echo You are now root and running program

# All files are copied to tmpfs and run from there
cd /mnt/tmpfs

# Mount filesystem
mount -o rw /
echo "Mounted read write filesystem"

# Make copy of running crontab
crontab -l >> /mnt/tmpfs/crontab_original.txt
echo "Made copy of original crontab"

# Kill the hipat_control.py process
pkill -F /mnt/tmpfs/check_offset.pid python
echo "Killed hipat_control.py"

# Make sure it is killed
echo
ps -x | grep hipat_control.py
echo "Output from ps -x"

# Copy in the new crontab
crontab /mnt/tmpfs/crontab_cesium_test.txt
echo "Copying in the new crontab"
