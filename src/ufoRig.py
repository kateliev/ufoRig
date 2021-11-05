# SCRIPT: ufoRig
# DESCRIPTION: A GUI based low level tool for editing 
# DESCRIPTION: Unified Font Object (.UFO) files 
# -----------------------------------------------------------
# (C) Vassil Kateliev, 2021 		(http://www.kateliev.com)
# ------------------------------------------------------------
# https://github.com/kateliev

# - Dependencies ---------------------------------------------
import os
import sys
import pathlib
import json
import plistlib
import xml.etree.ElementTree as ET

from lib import widgets
from PyQt5 import QtCore, QtGui, QtWidgets

# - Init ----------------------------------------------------
app_name, app_version = 'ufoRig', '1.36'

# - Config --------------------------------------------------
cfg_file_open_formats = 'UFO Designspace (*.designspace);; UFO (*.plist);;'

# - Dialogs and Main -----------------------------------------	
class main_ufoRig(QtWidgets.QMainWindow):
	def __init__(self):
		super(main_ufoRig, self).__init__()

		# - Init
		self.setTabPosition(QtCore.Qt.TopDockWidgetArea, QtWidgets.QTabWidget.North )
		self.setDockOptions(QtWidgets.QMainWindow.ForceTabbedDocks )

		# -- Status bar
		self.status_bar = QtWidgets.QStatusBar()
		self.setStatusBar(self.status_bar)
		
		# -- Tab widget
		self.wgt_tabs = QtWidgets.QTabWidget()
		self.wgt_tabs.setTabsClosable(True)
		self.wgt_tabs.tabCloseRequested.connect(lambda index: self.wgt_tabs.removeTab(index))
		
		# -- Central Widget
		self.setCentralWidget(self.wgt_tabs)
		
		# - Menu bar
		self.menu_file = QtWidgets.QMenu('File', self)

		# -- Actions
		act_data_open_file = QtWidgets.QAction('Open', self)
		act_data_save_file = QtWidgets.QAction('Save', self)
		act_data_open_file.triggered.connect(self.file_open)
		act_data_save_file.triggered.connect(self.file_save)
		
		self.menu_file.addAction(act_data_open_file)
		self.menu_file.addAction(act_data_save_file)
	
		# -- Set Menu
		self.menuBar().addMenu(self.menu_file)

		# - Set
		self.setWindowTitle('%s %s' %(app_name, app_version))
		self.setGeometry(300, 100, 900, 720)

	# - Docks ----------------------------------------------
	def __park_docks(self):
		all_docks = self.findChildren(QtWidgets.QDockWidget)
		for dock in all_docks[1:]:
			self.tabifyDockWidget(all_docks[0], dock)

	# - File IO ---------------------------------------------
	# -- Classes Reader
	def file_save(self):
		curr_path = pathlib.Path(__file__).parent.absolute()
		
		# - Get data from current active tab
		curr_tab = self.wgt_tabs.widget(self.wgt_tabs.currentIndex())
		curr_data = curr_tab.trw_explorer.get_tree()
		export_file = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', str(curr_path), cfg_file_open_formats)

		if len(export_file[0]):
			with open(export_file[0], 'wb') as exportFile:
				curr_data.write(exportFile, encoding='utf-8', xml_declaration=True)
		
		self.status_bar.showMessage('File Saved: {}'.format(export_file[0]))
				
	def file_open(self):
		curr_path = pathlib.Path(__file__).parent.absolute()
		import_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', str(curr_path), cfg_file_open_formats)
			
		if len(import_file[0]):
			if '.designspace' in import_file[0]:
				file_tree = ET.parse(import_file[0])
				tab_caption = os.path.split(import_file[0])[1]
				self.wgt_tabs.addTab(widgets.wgt_designspace_manager(file_tree, self.status_bar), tab_caption)

			if '.plist' in import_file[0]:
				with open(import_file[0], 'rb') as plist_file:
					file_tree = plistlib.load(plist_file)
				tab_caption = os.path.split(import_file[0])[1]
				self.wgt_tabs.addTab(widgets.wgt_plist_manager((tab_caption, file_tree), self.status_bar), tab_caption)

		self.status_bar.showMessage('File Loaded: {}'.format(import_file[0]))

# - Run -----------------------------
main_app = QtWidgets.QApplication(sys.argv)
main_dialog = main_ufoRig()
main_dialog.show()
main_app.exec_()


