# MODULE: ufoRig / lib / widgets
# -----------------------------------------------------------
# (C) Vassil Kateliev, 2021 		(http://www.kateliev.com)
# ------------------------------------------------------------
# https://github.com/kateliev

__version__ = 1.9

# - Dependencies --------------------------------------------
import plistlib
import xml.etree.ElementTree as ET

from PyQt5 import QtCore, QtGui, QtWidgets
from .func import xml_pretty_print
from .objects import data_collector

# - Config ----------------------------
cfg_trw_columns_class = ['Tag/Key', 'Data/Value', 'Type']
cfg_data_types = ['tag', 'attribute', 'str', 'int', 'float', 'bool', 'tuple', 'list', 'dict']

# - Helper functions ----------------------------------------
def set_font(widget, style):
	font = widget.font()
	font.setItalic('i' in style)
	font.setBold('b' in style)
	return font

def set_color(qt_color_name, alpha=255):
	color = QtGui.QColor(qt_color_name)
	color.setAlpha(alpha)
	return color

def set_brush(qt_color_name, alpha=255):
	return QtGui.QBrush(set_color(qt_color_name, alpha))

def string_plural(count, text='items', remove=1):
	text = text[:-remove] if count == 1 else text
	return '{} {}'.format(count, text)

# - Widgets -------------------------------------------------
# -- Shared
class trw_tree_explorer(QtWidgets.QTreeWidget):
	def __init__(self, status_hook):
		super(trw_tree_explorer, self).__init__()
		
		# - Init
		self.status_hook = status_hook
		self.itemClicked.connect(self.set_status)
		self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

		# - String
		self.__info_parent = 'Info: Tag <{}> with {} / {}'
		self.__info_child =  'Info: Attribute "{}" of <{}>'

		# - Drag and drop
		self.setDragEnabled(True)
		self.setDragDropMode(self.InternalMove)
		self.setDropIndicatorShown(True)

		# - Styling
		self.setAlternatingRowColors(True)
		
		# -- Fonts
		self.font_bold = set_font(self, 'b')
		self.font_italic = set_font(self, 'i')
		self.brush_gray = set_color('Gray')
		self.attrib_background = set_color('Yellow', 15)

		# -- Icons
		self.folder_attrib_name = 'attributes'
		self.folder_attrib_icon = self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon)
		
		self.folder_children_name = 'children'
		self.folder_children_icon = self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon)	

		# - Menus
		self.menu_context = QtWidgets.QMenu(self)
		self.menu_context.setTitle('Actions')

		self.menu_type = QtWidgets.QMenu(self)
		self.menu_type.setTitle('Set Type')

		# -- Actions
		act_add_parent = QtWidgets.QAction('New Parent', self)
		act_add_child = QtWidgets.QAction('New Child', self)
		act_item_remove = QtWidgets.QAction('Remove', self)
		act_item_duplicate = QtWidgets.QAction('Duplicate', self)
		act_item_eject = QtWidgets.QAction('Eject', self)
		
		self.menu_context.addAction(act_add_parent)
		self.menu_context.addAction(act_add_child)
		self.menu_context.addSeparator()
		self.menu_context.addMenu(self.menu_type)
		self.menu_context.addSeparator()
		self.menu_context.addAction(act_item_remove)
		self.menu_context.addAction(act_item_duplicate)
		self.menu_context.addSeparator()
		self.menu_context.addAction(act_item_eject)
		
		act_add_parent.triggered.connect(lambda: self._item_add(is_parent=True))
		act_add_child.triggered.connect(lambda: self._item_add(is_parent=False))
		act_item_duplicate.triggered.connect(lambda: self._item_duplicate())
		act_item_eject.triggered.connect(lambda: self._item_eject())
		act_item_remove.triggered.connect(lambda: self._item_remove())

		for data_type in cfg_data_types:
			act_new = QtWidgets.QAction(data_type, self)
			self.menu_type.addAction(act_new)
			act_new.triggered.connect(lambda checked, data=data_type: self._item_type(data))

	# - Internals --------------------------
	def _item_type(self, data_type):
		root = self.invisibleRootItem()
		
		for item in self.selectedItems():
			item.setText(2, data_type)

	def _item_remove(self):
		root = self.invisibleRootItem()
		
		for item in self.selectedItems():
			(item.parent() or root).removeChild(item)

	def _item_add(self, data=None, is_parent=False):
		defualt_text = 'New Tag' if is_parent else 'New Attribute'
		new_item_data = [defualt_text] if data is None else data
		new_item = QtWidgets.QTreeWidgetItem(new_item_data)
		new_item.setFont(2, self.font_italic)
		new_item.setForeground(2, self.brush_gray)
		
		if is_parent:	
			new_item.setIcon(0, self.folder_children_icon)
			new_item.setFlags(new_item.flags() | QtCore.Qt.ItemIsEditable)
		else:
			new_item.setFlags(new_item.flags() & ~QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsEditable)
			new_item.setIcon(0, self.folder_attrib_icon)

		parent = self.selectedItems()[0].parent()
		parent.addChild(new_item)

	def _item_duplicate(self):
		for item in self.selectedItems():
			item.parent().addChild(item.clone())
		
	def _item_eject(self):
		root = self.invisibleRootItem()
		
		for item in reversed(self.selectedItems()):
			old_parent = item.parent()
			
			if old_parent is not None:
				new_parent = old_parent.parent()
				ix = old_parent.indexOfChild(item)
				item_without_parent = old_parent.takeChild(ix)
				root.addChild(item_without_parent)
	
	# - Event Handlers ----------------------
	def contextMenuEvent(self, event):
		self.menu_context.popup(QtGui.QCursor.pos())

	@QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
	def set_status(self, item, col):
		status_message = ''

		try:
			if item.childCount() and item.text(2) != 'attribute':
				tags, attributes = 0, 0

				for c in range(item.childCount()):
					if item.child(c).childCount():
						tags += 1
					else:
						attributes += 1

				status_message = self.__info_parent.format(item.text(0), string_plural(tags), string_plural(attributes, 'attributes'))
			else:
				status_message = self.__info_child.format(item.text(0), item.parent().text(0))
			
		except AttributeError:
			status_message = 'Info: ...'

		self.status_hook.showMessage(status_message)


# -- XML -----------------------------------
class trw_xml_explorer(trw_tree_explorer):
	''' XML parsing and exporting tree widget'''

	# - Getter/Setter -----------------------
	def __tree_walker_set(self, node, parent):
		# - Set Tag	
		new_item_text = node.text.strip().strip('\n') if node.text is not None else ''
		new_item = QtWidgets.QTreeWidgetItem(parent, [node.tag, new_item_text, 'tag'])
		new_item.setFlags(new_item.flags() | QtCore.Qt.ItemIsEditable)
		new_item.setFont(2, self.font_italic)
		new_item.setForeground(2, self.brush_gray)
		
		# - Set Icon
		if len(list(node)) or len(node.attrib):	
			new_item.setIcon(0, self.folder_children_icon)
		else:
			new_item.setIcon(0, self.folder_attrib_icon)

		# - Set Attribute
		for pair in node.attrib.items():
			new_attribute = QtWidgets.QTreeWidgetItem(new_item, [pair[0], pair[1], 'attribute'])
			new_attribute.setFlags(new_item.flags() & ~QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsEditable)
			new_attribute.setIcon(0, self.folder_attrib_icon)
			new_attribute.setFont(2, self.font_italic)
			new_attribute.setForeground(2, self.brush_gray)
			
			for col in range(self.columnCount()):
				new_attribute.setBackground(col, self.attrib_background)

		# - Set Children
		if len(node):
			for child in node:
				self.__tree_walker_set(child, new_item)

	def __tree_walker_get(self, node, parent):
		if node.childCount() or 'attribute' not in str(node.text(2)):
			new_element = ET.Element(node.text(0))

			if len(node.text(1)):
				new_element.text = node.text(1)
			
			for c in range(node.childCount()):
				self.__tree_walker_get(node.child(c), new_element)

			parent.append(new_element)
		else:
			parent.set(node.text(0), node.text(1))

	def set_tree(self, data, headers):
		self.blockSignals(True)
		self.clear()
		self.setHeaderLabels(headers)
			
		# - Insert 
		if data is not None and isinstance(data, type(ET.ElementTree(None))):
			data_root = data.getroot()
			self.__tree_walker_set(data_root, self)

		# - Format
		self.expandAll()
		for c in range(self.columnCount()):
			self.resizeColumnToContents(c)	
		self.collapseAll()

		# - Set
		self.blockSignals(False)

	def get_tree(self):
		root = self.invisibleRootItem().child(0)
		new_element = ET.Element(None)
		
		self.__tree_walker_get(root, new_element)
		xml_pretty_print(new_element)
		
		root_element = ET.ElementTree(new_element)
		return root_element

class trw_plist_explorer(trw_tree_explorer):
	''' pList parsing and exporting tree widget'''
	def __init__(self, status_hook):
		super(trw_plist_explorer, self).__init__(status_hook)

		# - String
		self.__info_parent = 'Info: Parent <{}> with {} / {}'
		self.__info_child =  'Info: Child "{}" of <{}>'

	# - Internals
	@QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
	def set_status(self, item, col):
		status_message = ''
		try:
			if item.childCount() and (item.text(2) == 'dict' or item.text(2) == 'list'):
				parents, children = 0, 0

				for c in range(item.childCount()):
					if item.child(c).childCount():
						parents += 1
					else:
						children += 1

				status_message = self.__info_parent.format(item.text(0), string_plural(parents), string_plural(children, 'children', 3))
			else:
				status_message = self.__info_child.format(item.text(0), item.parent().text(0))
		except AttributeError:
			status_message = 'Info: ...'
			
		self.status_hook.showMessage(status_message)	
	
	# - Getter/Setter -----------------------
	def __tree_walker_set(self, node, parent):
		if isinstance(node, tuple):
			node_text, node_data = str(node[0]), node[1]
			node_data_text = str(node_data)
			node_type = str(type(node[1]).__name__)

			new_item = QtWidgets.QTreeWidgetItem(parent, [node_text, node_data_text, node_type])
			new_item.setFlags(new_item.flags() | QtCore.Qt.ItemIsEditable)
			new_item.setForeground(2, self.brush_gray)
			new_item.setFont(2, self.font_italic)
			new_item.setIcon(0, self.folder_attrib_icon)

			if isinstance(node_data, (list, dict)):
				node_data_list = node_data.values() if isinstance(node_data, dict) else node_data
				if any([isinstance(item, (list, dict)) for item in node_data_list]):
					new_item.setIcon(0, self.folder_children_icon)
					new_item.setText(1, '')

				self.__tree_walker_set(node_data, new_item)

		elif isinstance(node, list):
			for item in node:
				if isinstance(item, (list, dict)):
					sub_node_type = str(type(item).__name__)
					new_sub_item = QtWidgets.QTreeWidgetItem(parent, ['List Item', '', sub_node_type])
					new_sub_item.setIcon(0, self.folder_children_icon)
					new_sub_item.setForeground(0, self.brush_gray)
					new_sub_item.setFont(0, self.font_italic)
					new_sub_item.setForeground(2, self.brush_gray)
					new_sub_item.setFont(2, self.font_italic)

					self.__tree_walker_set(item, new_sub_item)
				else:
					self.__tree_walker_set(item, parent)
		
		elif isinstance(node, dict):
			for item in node.items():
				self.__tree_walker_set(item, parent)
		
	def __tree_walker_get(self, node):
		node_name, node_value, node_type = node.text(0), node.text(1), node.text(2)
		if node_type == 'dict' and 'List Item' in node_name: node_name = None
		new_element = data_collector(node_name, node_value, node_type)

		if node.childCount():
			for c in range(node.childCount()):
				sub_element = self.__tree_walker_get(node.child(c))
				new_element.append(sub_element)
		
		return new_element.export(evaluate=True)

	def set_tree(self, data, headers):
		self.blockSignals(True)
		self.clear()
		self.setHeaderLabels(headers)
			
		# - Insert 
		self.__tree_walker_set(data, self)

		# - Format
		self.expandAll()
		for c in range(self.columnCount()):
			self.resizeColumnToContents(c)	
		self.collapseAll()

		# - Set
		self.blockSignals(False)

	def get_tree(self):
		root = self.invisibleRootItem().child(0)
		return self.__tree_walker_get(root)

class wgt_designspace_manager(QtWidgets.QWidget):
	def __init__(self, data_tree, status_hook):
		super(wgt_designspace_manager, self).__init__()
		
		# - Init
		self.file_type = '.designspace'

		# - Widgets
		# -- Trees
		self.trw_explorer = trw_xml_explorer(status_hook)
		self.trw_explorer.set_tree(data_tree, cfg_trw_columns_class)

		# - Layout
		lay_main = QtWidgets.QVBoxLayout()
		lay_main.addWidget(self.trw_explorer)
		self.setLayout(lay_main)

class wgt_plist_manager(QtWidgets.QWidget):
	def __init__(self, data_tree, status_hook):
		super(wgt_plist_manager, self).__init__()
		
		# - Init
		self.file_type = '.plist'

		# - Widgets
		# -- Trees
		self.trw_explorer = trw_plist_explorer(status_hook)
		self.trw_explorer.set_tree(data_tree, cfg_trw_columns_class)

		# - Layout
		lay_main = QtWidgets.QVBoxLayout()
		lay_main.addWidget(self.trw_explorer)
		self.setLayout(lay_main)