#!/bin/sh

echo $LINE 
echo Backup Enigma2 Settings - HDD - For AR-Project
echo Please Wait
echo $LINE

cd /media/hdd
mkdir -p backup > /dev/null 2>&1
cd
tar -czvf enigma2settingsbackup.tar.gz /etc/enigma2 > /dev/null 2>&1
mv -f enigma2settingsbackup.tar.gz /media/hdd/backup > /dev/null 2>&1
cd /media/hdd/backup
chmod 644 enigma2settingsbackup.tar.gz > /dev/null 2>&1
cd

echo $LINE
echo Done !

exit 0