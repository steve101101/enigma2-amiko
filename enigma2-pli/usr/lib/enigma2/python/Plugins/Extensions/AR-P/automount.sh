#!/bin/sh 

/bin/stfbcontrol he 
umount -f /hdd
 
 devs=`fdisk -l | grep '/dev/' | awk '{gsub("/"," "); print $2}' | awk '{gsub("dev",""); print $1}'`
 id=1
 
 for i in $devs; do
     echo "/dev/$i"
 done
 
      fs_id=`fdisk -l | grep $devs | tr -d '*' | awk '{print $5}'`
    
      if [ $fs_id == 83 ]; then
      echo "Detect & mount ext2/3 partition on /dev/$i"
      mount /dev/$i /hdd/
      elif [ $fs_id == 6 ] || [ $fs_id == 5 ] || [ $fs_id == b ] || [ $fs_id == c ] || [ $fs_id == e ] || [ $fs_id == f ]; then
      echo "Detect & mount FAT16/32 partition on /dev/$i"
      mount /dev/$i /hdd/ 
      elif [ $fs_id == 7 ]; then
      echo "Detect & mount HPFS/NTFS on /dev/$i"
      ntfs-3g  /dev/$i /hdd/    
      else 
      echo "No such device"
      fi

exit 0