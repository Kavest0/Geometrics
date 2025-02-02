# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoMetrics
                                 A QGIS plugin
 Counts the ammount of certain geometries on each layer
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-12-11
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Kavest0 | Kayo
        email                : felipebrkr@gmail.com
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
from qgis.core import QgsProject, QgsWkbTypes, QgsGeometry
from qgis.utils import iface
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .GeoMetrics_dockwidget import GeoMetricsDockWidget
import os.path


class GeoMetrics:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
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
            'GeoMetrics_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GeoMetrics')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GeoMetrics')
        self.toolbar.setObjectName(u'GeoMetrics')

        #print "** INITIALIZING GeoMetrics"

        self.pluginIsActive = False
        self.dockwidget = None


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
        return QCoreApplication.translate('GeoMetrics', message)


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

        icon_path = ":/plugins/GeoMetrics/icon.png"
        self.add_action(
            icon_path,
            text=self.tr(u'Enable GeoMetrics'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING GeoMetrics"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD GeoMetrics"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GeoMetrics'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING GeoMetrics"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = GeoMetricsDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
            
            # Connect the selection change signal to the select_count function
            for layer in QgsProject.instance().mapLayers().values():
                layer.selectionChanged.connect(self.select_count)
            
            # Call the select_count function for the current selection
            self.select_count()

    def select_count(self):
        total_point_count = 0
        total_line_count = 0
        total_polygon_count = 0
        total_intersection_count = 0
        total_vertex_count = 0
        results = ""

        def on_segment(p, q, r):
            return min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and min(p[1], r[1]) <= q[1] <= max(p[1], r[1])

        def orientation(p, q, r):
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if val == 0:
                return 0  # collinear
            return 1 if val > 0 else 2  # 1: Clock-Wise, 2: Counter Clock-Wise

        def do_intersect(p1, q1, p2, q2):
            o1 = orientation(p1, q1, p2)
            o2 = orientation(p1, q1, q2)
            o3 = orientation(p2, q2, p1)
            o4 = orientation(p2, q2, q1)

            if o1 != o2 and o3 != o4:
                return True
            if o1 == 0 and on_segment(p1, p2, q1):
                return True
            if o2 == 0 and on_segment(p1, q2, q1):
                return True
            if o3 == 0 and on_segment(p2, p1, q2):
                return True
            if o4 == 0 and on_segment(p2, q1, q2):
                return True
            return False

        def count_intersections(layer, feature, vertices):
            intersection_count = 0
            for i in range(len(vertices) - 1):
                p1 = (vertices[i].x(), vertices[i].y())
                q1 = (vertices[i + 1].x(), vertices[i + 1].y())

                for other_feature in layer.getFeatures():
                    if other_feature.id() == feature.id():
                        continue

                    other_geom = other_feature.geometry()
                    if other_geom.type() == QgsWkbTypes.LineGeometry:
                        other_vertices = list(other_geom.vertices())
                        for j in range(len(other_vertices) - 1):
                            p2 = (other_vertices[j].x(), other_vertices[j].y())
                            q2 = (other_vertices[j + 1].x(), other_vertices[j + 1].y())

                            if do_intersect(p1, q1, p2, q2):
                                intersection_count += 0.5
            return intersection_count
        
        def process_layer(layer):
            point_count = 0
            line_count = 0
            polygon_count = 0
            intersection_count = 0
            vertex_count = 0

            for feature in layer.selectedFeatures():
                geom = feature.geometry()
                if geom.type() == QgsWkbTypes.PointGeometry:
                    point_count += 1
                elif geom.type() == QgsWkbTypes.LineGeometry:
                    line_count += 1
                    vertices = list(geom.vertices())
                    vertex_count += len(vertices)
                    intersection_count += count_intersections(layer, feature, vertices)
                elif geom.type() == QgsWkbTypes.PolygonGeometry:
                    polygon_count += 1
            return point_count, line_count, polygon_count, int(intersection_count), vertex_count

        for layer in QgsProject.instance().mapLayers().values():
            if layer.selectedFeatureCount() > 0:
                point_count, line_count, polygon_count, intersection_count, vertex_count = process_layer(layer)

                total_point_count += point_count
                total_line_count += line_count
                total_polygon_count += polygon_count
                total_intersection_count += intersection_count
                total_vertex_count += vertex_count

                results += (
                    f"Camada: {layer.name()}\n"
                    f"  Quantidade de Pontos: {point_count}\n"
                    f"  Quantidade de Poligonos: {polygon_count}\n"
                    f"  Quantidade de Linhas: {line_count}\n"
                    f"  Quantidade de Interseções: {intersection_count}\n"
                    f"  Quantidade de Vértices: {vertex_count}\n\n"
                )

        results += (
            f"Resultados Totais:\n"
            f"  Quantidade Total de Pontos: {total_point_count}\n"
            f"  Quantidade Total de Poligonos: {total_polygon_count}\n"
            f"  Quantidade Total de Linhas: {total_line_count}\n"
            f"  Quantidade Total de Interseções: {total_intersection_count}\n"
            f"  Quantidade Total de Vértices: {total_vertex_count}\n"
        )

        if self.dockwidget:
            self.dockwidget.update_results(results)
