# -*- coding: utf-8 -*-
"""
TeleMir depend on pyacq that offer some device and in particular Emotiv.

You can find here main core object of teleMir that can be re-usable projet by projets.

Divide in 2 parts:
    * TeleMir.analyses   for Rt analysis with no graphic interface
    * TeleMir.gui   for displaying signals and everything related based on PyQt4 and pyqtgraph


"""

from .analyses import *
from .fake_TeleMir_Calibration import Fake_TeleMir_Calibration
from .fake_TeleMir_Vol import Fake_TeleMir_Vol
from .teleMir_Calibration import TeleMir_Calibration
from .teleMir_Vol import TeleMir_Vol
