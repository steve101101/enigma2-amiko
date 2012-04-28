#!/bin/sh
/bin/stfbcontrol hd 
echo off > /dev/vfd 
sleep 2 
DISPL7162=`grep -c 'spark7162' /proc/stb/info/model`
if [ "$DISPL7162" -eq "1" ]; then
/bin/fp_control -c
/bin/fp_control -s `date +"%H:%M:%S %d-%m-%Y"`
else
/bin/fp_control -s `date +"%H:%M:%S %d-%m-%Y"`
fi
echo "done"