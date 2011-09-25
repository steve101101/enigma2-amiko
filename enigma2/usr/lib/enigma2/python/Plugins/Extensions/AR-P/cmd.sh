#!/bin/sh
TMP=/tmp/.mftemp
PLUGINDIR=/usr/lib/enigma2/python/Plugins/Extensions/AR-P
CMDS=startup.cmd

touch $PLUGINDIR/$CMDS
#maximal 4 arguments per command !

case $1 in 
  "remove")
     grep -v $2 $PLUGINDIR/$CMDS > $TMP
     cp $TMP $PLUGINDIR/$CMDS
     echo "----------------------------------------------------------"
     cat $PLUGINDIR/$CMDS
     echo "----------------------------------------------------------"
  ;;
  "add")
     # maximal 6 arguments per command !
     grep -v $2 $PLUGINDIR/$CMDS > $TMP
     echo "$3 $4 $5 $6 $7 $8 # $2" >> $TMP
     cp $TMP $PLUGINDIR/$CMDS
     echo "----------------------------------------------------------"
     cat $PLUGINDIR/$CMDS
     echo "----------------------------------------------------------"
  ;;
  "list")
     echo "----------------------------------------------------------"
     cat $PLUGINDIR/$CMDS
     echo "----------------------------------------------------------"
  ;;
  
  *)
    echo "no command passed sorry"
    exit 1
  ;;
esac

exit 0
    
