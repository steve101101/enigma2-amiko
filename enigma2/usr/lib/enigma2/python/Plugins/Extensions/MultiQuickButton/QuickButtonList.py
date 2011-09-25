from Components.MenuList import MenuList
from Tools.Directories import SCOPE_SKIN_IMAGE, resolveFilename
from enigma import RT_HALIGN_LEFT, eListboxPythonMultiContent, gFont
from Tools.LoadPixmap import LoadPixmap

def QuickButtonListEntry(key, text):
	res = [ text ]
	if text[0] == "--":
		png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "cli_default/op_separator.png"))
		if png is not None:
			res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 0, 12, 780, 25, png))
	else:
		res.append((eListboxPythonMultiContent.TYPE_TEXT, 45, 00, 780, 25, 0, RT_HALIGN_LEFT, text[0]))
		if key == "green" or key == "red":
			path = "cli_default/" + key + ".png"
		else:
			path = "skin_default/buttons/key_" + key + ".png"
			
		png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, (path)))
		if png is not None:
			res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 5, 0, 35, 25, png))
	return res

class QuickButtonList(MenuList):
	def __init__(self, list, selection = 0, enableWrapAround=False):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		self.l.setFont(0, gFont("Regular", 20))
		self.l.setItemHeight(25)
		self.selection = selection

	def postWidgetCreate(self, instance):
		MenuList.postWidgetCreate(self, instance)
		self.moveToIndex(self.selection)
