import string
import cPickle
import sys
sys.path.append("/usr/lib/enigma2/python/Plugins/SystemPlugins/WirelessLan")
sys.path.append("/usr/lib/enigma2/python")
from iwlibs import Wireless, Iwscan
from string import maketrans, strip

a = ''; b = ''
scanfile="/tmp/wlanscan"
for i in range(0, 255):
	a = a + chr(i)
	if i < 32 or i > 127:
		b = b + ' '
	else:
		b = b + chr(i)
try:
	iface=sys.argv[1];
except:
	msg = "No interface to scan\n";
	o_file=open(scanfile,"w");
	o_file.write(msg);
	o_file.close();
	print msg;
	sys.exit();

asciitrans = maketrans(a, b)
ifobj = Wireless(iface) # a Wireless NIC Object
stats, quality, discard, missed_beacon = ifobj.getStatistics()
snr = quality.signallevel - quality.noiselevel
scanresults = ifobj.scan()

if scanresults is not None:
	aps = {}
	for result in scanresults:
	
		bssid = result.bssid

		encryption = map(lambda x: hex(ord(x)), result.encode)
		
		if encryption[-1] == "0x8":
			encryption = True
		else:
			encryption = False
		
		extra = []
		for element in result.custom:
			element = element.encode()
			extra.append( strip(element.translate(asciitrans)) )
				
		if result.quality.sl is 0 and len(extra) > 0:
			begin = extra[0].find('SignalStrength=')+15
									
			done = False
			end = begin+1
			
			while not done:
				if extra[0][begin:end].isdigit():
					end += 1
				else:
					done = True
					end -= 1
			
			signal = extra[0][begin:end]
			#print "[Wlan.py] signal is:" + str(signal)

		else:
			signal = str(result.quality.sl)
				
		aps[bssid] = {
			'active' : True,
			'bssid': result.bssid,
			'channel': result.frequency.getChannel(result.frequency.getFrequency()),
			'encrypted': encryption,
			'essid': strip(result.essid.translate(asciitrans)),
			'iface': iface,
			'maxrate' : result.rate[-1],
			'noise' : result.quality.getNoiselevel(),
			'quality' : str(result.quality.quality),
			'signal' : signal,
			'custom' : extra,
		}
		print aps[bssid]
	cPickle.dump(aps, open(scanfile, 'wb'))
