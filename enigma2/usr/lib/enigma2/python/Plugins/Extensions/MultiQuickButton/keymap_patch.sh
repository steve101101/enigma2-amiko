#!/bin/sh

sed -ie s!"			<key id=\"KEY_YELLOW\" mapto=\"timeshiftStart\" flags=\"m\" />"!"			<key id=\"KEY_YELLOW\" mapto=\"timeshiftStart\" flags=\"b\" />"!g "/usr/share/enigma2/keymap.xml"
sed -ie s!"			<key id=\"KEY_YELLOW\" mapto=\"timeshiftActivateEndAndPause\" flags=\"m\" />"!"			<key id=\"KEY_YELLOW\" mapto=\"timeshiftActivateEndAndPause\" flags=\"b\" />"!g "/usr/share/enigma2/keymap.xml"
sed -ie s!"		<key id=\"KEY_VIDEO\" mapto=\"showMovies\" flags=\"m\" />"!"		<key id=\"KEY_VIDEO\" mapto=\"showMovies\" flags=\"b\" />"!g "/usr/share/enigma2/keymap.xml"
sed -ie s!"		<key id=\"KEY_RADIO\" mapto=\"showRadio\" flags=\"m\" />"!"		<key id=\"KEY_RADIO\" mapto=\"showRadio\" flags=\"b\" />"!g "/usr/share/enigma2/keymap.xml"
sed -ie s!"		<key id=\"KEY_TEXT\" mapto=\"startTeletext\" flags=\"m\" />"!"		<key id=\"KEY_TEXT\" mapto=\"startTeletext\" flags=\"b\" />"!g "/usr/share/enigma2/keymap.xml"
sed -ie s!"		<key id=\"KEY_HELP\" mapto=\"displayHelp\" flags=\"m\" />"!"		<key id=\"KEY_HELP\" mapto=\"displayHelp\" flags=\"b\" />"!g "/usr/share/enigma2/keymap.xml"
exit 0