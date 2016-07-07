#!/usr/bin/env bash
# Script that will copy and implement a test of the Cesium oscillator in the HiPAT system.
# The program monitors the oscillator for 8 days and performs a frequency adjustment on the oscillator.
#

# Log into the specified machine

#echo "Specify ip address:"
#read ip_address
ip_address="158.112.116.41"

scp external.sh crontab_cesium_test.txt hipat_log.py timeout.py admin@$ip_address:/mnt/tmpfs/
echo Going to, $ip_address
ssh -t admin@$ip_address '/mnt/tmpfs/external.sh'

echo We are back