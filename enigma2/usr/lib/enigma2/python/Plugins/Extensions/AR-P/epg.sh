#!/bin/sh
#Thanks to dillinger http://linux-sat.tv

                if [ -f /media/hdd/epg.dat ]; then
                rm /usr/media/hdd/epg.dat > /dev/null 2>&1
                fi
echo "=============================================="
 
        	echo " "
    		echo "Downloading EPG file, please wait..."
		echo " "
    		sleep 2 
		wget -q http://linux-sat.tv/epg/epg_new.dat.gz -O /hdd/epg.dat.gz 
		if [ $? = 1 ]; then
		echo " "
    		echo "Sorry, the EPG file is not available!"
		echo " "
    		echo "Please try later!"
		echo " "
		echo "=============================================="
		echo " "
		exit 1
                fi
      		gzip -d /hdd/epg.dat.gz
		sleep 2
		echo "Enigma2 a restart to load the EPG data!"
		echo " "
		echo "=============================================="
		echo " "
		echo "Enjoy -:) "
		echo "Restarting enigma2..."
	        sleep 2
	        killall -9 enigma2