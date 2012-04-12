#!/bin/sh

cd /
ipkg install /tmp/*.ipk

sleep 2
killall -9 enigma2