#!/bin/sh
#Thanks to dillinger http://linux-sat.tv

        	echo "===================================================="
    		echo "Файлы  подгружаемого  с  инета  E P G  находятся  в  папке  var/epg"
		echo "                       usb - флешь  нам  не  понадобится."
		echo "         Директория  var/epg  будет  очищаться  автоматически "
                echo "                 перед  каждым  новым  запуском  плагина."
                if [ -f /tmp/epg.dat ]; then
                rm -rf /tmp/epg.dat
                elif [ -f /tmp/epg.dat.gz ]; then
                rm -rf /tmp/epg.dat.gz
                fi
                echo "===================================================="
 
        	echo " "
    		echo "             Началаль  загрузка,  подождите......."
		echo "    Можете  попить  кофейку  и  выкурить  сигарету ! "
        	echo " "
    		sleep 2 
		wget -q http://linux-sat.tv/epg/epg_new.dat.gz -O /tmp/epg.dat.gz 
		if [ $? = 1 ]; then
		echo " "
    		echo "       Сори,  но  EPG  файл  пока  недоступен !"
		echo " "
    		echo "    Пожалуйста,  попробуйте  загрузить  позже!"
		echo " "
		echo "===================================================="
		echo " "
		exit 1
                fi
      		gzip -d /tmp/epg.dat.gz
                sleep 2
                cp /tmp/epg.dat /var/
		sleep 2
		echo "    Enigma2  перезапустится  после  окончания  загрузки!"
		echo " "
		echo "===================================================="
		echo " "
		echo "     В С Е  получилось.  Наслаждайтесь  программой  Т В !   "
		echo "                  Перегружаюсь,  один  момент......."
	        sleep 2
	        killall -9 enigma2