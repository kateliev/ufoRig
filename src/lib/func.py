# MODULE: ufoRig / lib / functions
# -----------------------------------------------------------
# (C) Vassil Kateliev, 2021 		(http://www.kateliev.com)
# ------------------------------------------------------------
# https://github.com/kateliev

__version__ = 1.0

# - Functions -----------------------------------------------
def xml_pretty_print(current, parent=None, index=-1, depth=0, indent='  '):
	''' Adapted from: https://stackoverflow.com/questions/28813876/how-do-i-get-pythons-elementtree-to-pretty-print-to-an-xml-file'''
	for i, node in enumerate(current):
		xml_pretty_print(node, current, i, depth + 1)
	
	if parent is not None:
		if index == 0:
			parent.text = '\n' + (indent * depth)
		else:
			parent[index - 1].tail = '\n' + (indent * depth)
		if index == len(parent) - 1:
			current.tail = '\n' + (indent * (depth - 1))