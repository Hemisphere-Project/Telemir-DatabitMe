# -*- coding: utf-8 -*-
"""
TeleMir phase 2 : vol
"""

from pyacq import StreamHandler, EmotivMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq
from gui import Topoplot, Topoplot_imp#,  KurtosisGraphics, freqBandsGraphics

import msgpack
#~ import gevent
#~ import zmq.green as zmq

from PyQt4 import QtCore,QtGui
from PyQt4.QtCore import QTimer

import zmq
import msgpack
import time
from TeleMir.analyses import TransmitFeatures
import numpy as np

class TeleMir_Vol:
    def __init__(self):
        print 'debut vol'
        self.streamhandler = StreamHandler()
        ## Configure and start
        self.dev = EmotivMultiSignals(streamhandler = self.streamhandler)
        self.dev.configure(buffer_length = 1800)
        self.dev.initialize()
        self.dev.start()

        self.fout = TransmitFeatures(streamhandler = self.streamhandler)
        self.fout.configure( #name = 'Test fout',
                                    nb_channel = 14, # np.array([1:5])
                                    nb_feature = 9,
                                    nb_pts = 128,
                                    sampling_rate =10.,
                                    buffer_length = 10.,
                                    packet_size = 1,
                                    )

        # <pyacq.core.streamtypes.AnalogSignalSharedMemStream object at 0x000000001A8D5A20>
        self.fout.initialize(stream_in = self.dev.streams[0]) #, stream_xy = self.dev.streams[2])
        self.fout.start()

        mainScreen = 1920
        subScreen = 640
        # signal
        numscreen = 4
        self.w_oscilo=Oscilloscope(stream = self.dev.streams[0])
        self.w_oscilo.auto_gain_and_offset(mode = 2)
        self.w_oscilo.set_params(xsize = 10, mode = 'scroll')
        self.w_oscilo.automatic_color('jet')
        self.w_oscilo.move(mainScreen + (numscreen-1) * subScreen- 30 , -40)
        self.w_oscilo.resize(810,530)
        # self.w_oscilo.setWindowState(QtCore.Qt.WindowFullScreen)
        self.w_oscilo.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.w_oscilo.show()
        #parametres
        numscreen = 5
        self.w_feat1=Oscilloscope(stream = self.fout.streams[0])
        self.w_feat1.auto_gain_and_offset(mode = 0)
        self.w_feat1.set_params(xsize = 10, mode = 'scroll')
        self.w_feat1.automatic_color('jet')
        self.w_feat1.set_params(colors = [[0, 0, 255], [255, 0, 255], [255, 0 ,0], [255, 255, 0], [0, 0, 0], [0, 0, 0], [0, 255, 0], [0, 255, 255], [0, 0, 0]])
        self.w_feat1.set_params(selected = [True, True, True, True, False, False, True, True, False])
        self.w_feat1.set_params(xsize = 10, mode = 'scroll', selected = [True, True, True, True, False, False, True, True, False])
        self.w_feat1.set_params(ylims = [-10,110])
        self.w_feat1.move(mainScreen + (numscreen-1) * subScreen- 30 , -40)
        self.w_feat1.resize(800,500)
        # self.w_feat1.setWindowState(QtCore.Qt.WindowFullScreen)
        # self.w_feat1.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.w_feat1.show()

        self.timer = QTimer(singleShot=True, interval=13000)
        self.timer.timeout.connect(lambda :self.w_oscilo.auto_gain_and_offset(mode = 2))
        self.timer.start()
        #topo
        # numscreen = 3
        # self.w_topo=Topoplot(stream = self.dev.streams[0], type_Topo = 'topo')
        # self.w_topo.move(self.screensize + (numscreen-1) * 800 ,200)
        # self.w_topo.show()

    def close(self):

        #close windows
        # self.w_imp.close()
        self.w_oscilo.close()
        self.w_feat1.close()

        # Stope and release the device
        self.fout.stop()
        self.fout.close()
        self.dev.stop()
        self.dev.close()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    t = TeleMir_Vol()
    app.exec_()
    t.close()
