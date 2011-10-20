#!/bin/sh
#
##
sleep 4
echo $LINE 
echo Please Wait
echo $LINE

fdisk -l
swapoff /media/hdd > /dev/null 2>&1
swapoff /media/sda1 > /dev/null 2>&1
swapoff /media/sdb1 > /dev/null 2>&1
umount -f /media/hdd > /dev/null 2>&1
umount -f /media/sda1 > /dev/null 2>&1
umount -f /media/sdb1 > /dev/null 2>&1
umount -f /dev/sda1 > /dev/null 2>&1
umount -f /dev/sdb1 > /dev/null 2>&1
mkfs.ext3 -F /dev/sda1 > /dev/null 2>&1
mkfs.ext3 -F /dev/sdb1 > /dev/null 2>&1

echo $LINE
echo Done !
echo $LINE

echo "Mount HDD" > /dev/vfd
mount /dev/sda1 /hdd > /dev/null 2>&1
mount /dev/sdb1 /hdd > /dev/null 2>&1

ln -s /hdd/ /media/sda1
echo "Done" > /dev/vfd

sleep 2
echo "Backup started" > /dev/vfd
sleep 2
echo "syncing disk" > /dev/vfd
sync
echo "kill rcS" > /dev/vfd
sleep 1
killall -9 rcS
echo "kill enigma2" > /dev/vfd
killall -9 enigma2
sleep 1
echo "touch firstboot" > /dev/vfd
touch /var/etc/.firstboot
sleep 1
echo "Waiting" > /dev/vfd
sleep 2

## create media execlude list

TMP=.tmp
EXECLUDLIST=.execludlist
echo "" > $TMP
echo "" > $EXECLUDLIST

ls -1 /media > $TMP
LIST=`cat $TMP`

for ROUND in $LIST; do
        echo " --exclude=/media/$ROUND/*" >> $EXECLUDLIST
        sed '/^ *$/d' -i $EXECLUDLIST

done
EXECLUDMEDIA=`cat $EXECLUDLIST | tr -d '\n' | sed 's/*/* /'`
rm $EXECLUDLIST
rm $TMP

## create mnt execlude list

TMP=.tmp
EXECLUDLIST=.execludlist
echo "" > $TMP
echo "" > $EXECLUDLIST

ls -1 /mnt > $TMP
LIST=`cat $TMP`

for ROUND in $LIST; do
        echo " --exclude=/mnt/$ROUND/*" >> $EXECLUDLIST
        sed '/^ *$/d' -i $EXECLUDLIST

done
EXECLUDMNT=`cat $EXECLUDLIST | tr -d '\n' | sed 's/*/* /'`
rm $EXECLUDLIST
rm $TMP

## create sda1 execlude list

TMP=.tmp
EXECLUDLIST=.execludlist
echo "" > $TMP
echo "" > $EXECLUDLIST

ls -1 /hdd > $TMP
LIST=`cat $TMP`

for ROUND in $LIST; do
        echo  " --exclude=/media/sda1/$ROUND/*" >> $EXECLUDLIST
        sed '/^ *$/d' -i $EXECLUDLIST

done
EXECLUDHDD=`cat $EXECLUDLIST | tr -d '\n' | sed 's/*/* /'`
rm $EXECLUDLIST
rm $TMP

##
echo "| BACKUP"
echo "|"
echo "| KOMPRESS      : cf"
echo "| EXECLUD-SELF  : --exclude=test.tar"
echo "| EXECLUD-FILE  : --exclude=.execludlist --exclude=.tmp --exclude=swapfile" 
echo "| EXECLUD-SYS   : --exclude=sys/* --exclude=proc/* --exclude=tmp/* --exclude=ram/*"
echo "| EXECLUD-HDD   : $EXECLUDHDD"
echo "| EXECLUD-MNT   : $EXECLUDMNT"
echo "| EXECLUD-MEDIA : $EXECLUDMEDIA"
echo "| ADD-LIST      : --add-file=/dev/MAKEDEV /"
echo "|"
echo "| Backup started"

mkdir /media/sda1/save/
mkdir /media/sda1/enigma2/


/sbin/tar cf /media/sda1/test1.tar --exclude=test1.tar --exclude=.execludlist --exclude=.tmp --exclude=swapfile --exclude=sys/* --exclude=proc/* --exclude=tmp/* --exclude=ram/*  $EXECLUDHDD $EXECLUDMNT $EXECLUDMEDIA --add-file=/dev/MAKEDEV / 
echo "| Backup done"
/sbin/tar xvpf /media/sda1/test1.tar -C /media/sda1/save/

rm  /media/sda1/test1.tar
mkfs.jffs2 -n -e 128 -d /media/sda1/save/ -o /media/sda1/enigma2/e2jffs2.img

mv /media/sda1/enigma2/ /media/sda1/`date +"%Y.%m.%d_%H.%M.%S"`enigma2/

rm -r /media/sda1/save/

echo "syncing disk" > /dev/vfd
sync
sleep 2
echo "Backup ready"
echo "Backup ready" > /dev/vfd
sleep 2
number=`ls -l /media/sda1/ | wc -l`

until false
do
	count=`ls -l /media/sda1/ | wc -l`
	if [ "$number" = "$count" ]; then
		echo "waiting" > /dev/vfd
		sleep 1
		echo "Please copy your" > /dev/vfd
		sleep 1
		echo "Backup and" > /dev/vfd
		sleep 1
		echo "remove this !!" > /dev/vfd
		sleep 1
	else
		echo "syncing disk" > /dev/vfd
		sync
		sleep 1
		echo "Thanks" > /dev/vfd
		sleep 1
		echo "Rebooting now"
		echo "Rebooting now" > /dev/vfd
		reboot -f
	fi
done

echo "done"

