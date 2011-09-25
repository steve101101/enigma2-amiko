#!/bin/sh
set -x
exec > /var/log/Enigma2_Setting_Update.log 2>&1
#DESCRIPTION=Downloads, Installs & Reloads the latest Enigma2 Bouquets & Picons

#Transfer script to /usr/script and chmod 755 
#A log file will be created in /var/log

#Change the URL to point to your Bouquet tar.gz file
BQ="http://upload.sat-universum.de/gensh4sat.tar.gz"
#BP="http://upload.sat-universum.de/Setings_jodasa.tar.gz"

## Bouquet Download, Installation + Reload ##
cd /tmp/
wget $BQ
chmod 755 /tmp/gensh4sat.tar.gz
/sbin/tar -xzvf gensh4sat.tar.gz

cd /tmp/enigma2
rm -rf /etc/tuxbox/satellites.xml
mv /tmp/enigma2/satellites.xml /etc/tuxbox/

cd /etc/enigma2
rm -rf *.tv
rm -rf *.radio
rm -rf blacklist
rm -rf lamedb
rm -rf *_org
mv /tmp/enigma2/* /etc/enigma2

rm -rf /tmp/enigma2
rm -rf /tmp/gensh4sat.tar.gz

wget -qO - http://127.0.0.1/web/servicelistreload?mode=1
wget -qO - http://127.0.0.1/web/servicelistreload?mode=2

## Picon Installation ##
#cd /tmp/
#wget $BP
#chmod 755 /tmp/Setings_jodasa.tar.gz
#/sbin/tar -xzvf Setings_jodasa.tar.gz
#rm -rf /etc/enigma2/
#mv /tmp/enigma2/ /etc/

#rm -rf /tmp/Setings_jodasa.tar.gz
