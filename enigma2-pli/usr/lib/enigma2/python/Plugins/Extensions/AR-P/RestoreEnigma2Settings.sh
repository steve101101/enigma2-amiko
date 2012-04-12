#!/bin/sh

echo $LINE 
echo Restore Enigma2 Settings For AP-Project
echo Please Wait
echo $LINE

tar -zxvf /media/hdd/backup/enigma2settingsbackup.tar.gz -C / > /dev/null 2>&1
tar -zxvf /media/usb/backup/enigma2settingsbackup.tar.gz -C / > /dev/null 2>&1
killall -9 enigma2 > /dev/null 2>&1

exit 0