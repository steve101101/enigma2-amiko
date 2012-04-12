#!/bin/sh
#DESCRIPTION=This script will update your image with RB MGcamd-CCcam Keys
echo "Mgcamd - CCcam KeyUpdate by redbull301"
echo "erstelle Ordner..."
[ -d /var/keys ] || mkdir -p /var/keys
echo "lade Key Dateien herunter"
wget http://keys.satangels.com/single/RB_Mgamd_CCcam.tar.gz -O /tmp/RB_Mgamd_CCcam.tar.gz
wget http://keys.satangels.com/single/RB_mgcamd.txt -O /tmp/RB_mgcamd.txt
echo "key Dateien werden installiert..."
tar -xzf /tmp/RB_Mgamd_CCcam.tar.gz -C /
chmod 644 /var/keys/AutoRoll.Key
chmod 644 /var/keys/SoftCam.Key
chmod 644 /var/keys/constant.cw
echo "Key-Update erfolgreich abgeschlossen."
echo ""
echo ""
echo ""
echo ""
echo ""
more /tmp/RB_mgcamd.txt
rm /tmp/RB_Mgamd_CCcam.tar.gz
rm /tmp/RB_mgcamd.txt
sleep 2
