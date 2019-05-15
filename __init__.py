# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UTM2Cassin
                                 A QGIS plugin
 UTM2Cassin is used for transformation from UTM to Cassin, and the other way around.
                             -------------------
        begin                : 2019-05-13
        copyright            : (C) 2019 by George Thomas Muteti
        email                : thomas.muteti@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load UTM2Cassin class from file UTM2Cassin.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .utm_cassin import UTM2Cassin
    return UTM2Cassin(iface)
