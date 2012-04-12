#!/bin/sh
if [ ! `grep -o spark /proc/stb/info/model` ]; then
 /bin/vdstandby &
else
# turn off TV
/bin/stfbcontrol hd

 echo off > /dev/vfd
sleep 2
date +%H%M > /dev/vfd

fi
