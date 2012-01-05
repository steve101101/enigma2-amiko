#!/bin/sh
#!/bin/sh
case "$1" in
	titan)
	echo "titan" | cat > /etc/init.d/start
	init 6
	echo "Titan" > /dev/vfd
	 ;;
	enigma)
	echo "enigma" | cat > /etc/init.d/start
	init 6
	echo "Enigma2" > /dev/vfd
	;;
	*)
		echo "<enigma|titan>"
		exit 1
	 ;;	
esac 
exit 0
