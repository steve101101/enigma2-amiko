#!/bin/sh
#DESCRIPTION=This script will show you the performance of your internet-connection
echo "Ping Router: #### please write your router address in /usr/lib/enigma2/python/Plugins/Extensions/AR-P/Network.sh ########"
ping -c 1 xxx.xxx.xxx.xxx
echo "*****************************"
echo "Ping google.de:"
ping -c 1 www.google.de
echo "*****************************"
echo "Ping CS Server: #### please write your CS Server address in /usr/lib/enigma2/python/Plugins/Extensions/AR-P/Network.sh ########"
ping -c 1 xxx.xxx.xxx.xxx
echo "*****************************"
echo ""
exit 0
