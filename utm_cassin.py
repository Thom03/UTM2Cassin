# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UTM2Cassin
                                 A QGIS plugin
 UTM2Cassin is used for transformation from UTM to Cassin, and the other way around.
                              -------------------
        begin                : 2019-05-13
        git sha              : $Format:%H$
        copyright            : (C) 2019 by George Thomas Muteti
        email                : thomas.muteti@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import QGis, QgsMessageLog, QgsMapLayer
from osgeo import ogr
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from utm_cassin_dialog import UTM2CassinDialog
import os.path
import csv
from osgeo import ogr, gdal
import osgeo.osr as osr
import json, os
from qgis.gui import QgsMessageBar
from os.path import expanduser
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

# DI - Feed the CSV files to the lists in the plugin
home = expanduser("~")

filep = home + "\\.qgis2\\python\\plugins\\utm_cassini_converter_class\\"

Cassini_SheetNo_Id = "CASSINI_identify_sheet_no.csv"
UTM_SheetNo_Id = "UTM_identify_sheet_no.csv"
Cassini_UTM_Params = "CASSINI_to_UTM_with_sheetno.csv"
UTM_Cassini_Params = "UTM_to_CASSINI_with_sheetno.csv"

all_csv = [Cassini_SheetNo_Id, UTM_SheetNo_Id, Cassini_UTM_Params,
UTM_Cassini_Params]
C_S_I = []
U_S_I = []
C_U_P = []
U_C_P = []

for fyl in all_csv:
    with open(filep + fyl, 'rb') as f:
        reader = csv.reader(f)
        your_list = list(reader)

        for k in your_list:
            if your_list[0] != k and fyl == Cassini_SheetNo_Id:
                C_S_I.append(k)
            if your_list[0] != k and fyl == UTM_SheetNo_Id:
                U_S_I.append(k)
            if your_list[0] != k and fyl == Cassini_UTM_Params:
                C_U_P.append(k)
            if your_list[0] != k and fyl == UTM_Cassini_Params:
                U_C_P.append(k)


new_coords = []
ref = ""
shp_name = ""
oncanvas = ""
out_name = ""
oncanvas = False
cas_e = ""
cas_n = ""
sn = ""
utm_e = ""
utm_n = ""



""
""


class UTM2Cassin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'UTM2Cassin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&UTM2Cassin')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'UTM2Cassin')
        self.toolbar.setObjectName(u'UTM2Cassin')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('UTM2Cassin', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = UTM2CassinDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/UTM2Cassin/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&UTM2Cassin'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
