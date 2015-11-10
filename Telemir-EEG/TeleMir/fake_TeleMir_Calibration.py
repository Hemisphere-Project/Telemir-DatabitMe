# -*- coding: utf-8 -*-
"""
TeleMir phase 1 : calibration des impedances
"""

from pyacq import StreamHandler, EmotivMultiSignals
from pyacq import StreamHandler, FakeMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq
from TeleMir.gui import Topoplot, Topoplot_imp, KurtosisGraphics, freqBandsGraphics

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

class Fake_TeleMir_Calibration:
    
    def __init__(self, precomputed):
    
        self.streamhandler = StreamHandler()
        # Configure and start
        self.dev = FakeMultiSignals(streamhandler = self.streamhandler)
        self.dev.configure( #name = 'Test dev',
                                    nb_channel = 14,
                                    sampling_rate =128.,
                                    buffer_length = 30.,
                                    packet_size = 1,
                                    precomputed = precomputed,
                                    )
        self.dev.initialize()
        self.dev.start()
            
        # Impedances
        self.w_imp=Topoplot_imp(stream = self.dev.streams[0], type_Topo = 'imp')
        self.w_imp.show()
        
        
    def close(self):
        
        #close window
        self.w_imp.close()
    
        # Stope and release the device
        self.dev.stop()
        self.dev.close()



if __name__ == '__main__':
    
    
    app = QtGui.QApplication([])
    
    filename = '/home/mini/pyacq_emotiv_recording/alex/Emotiv Systems Pty Ltd #SN201105160008860.raw'
    filenameImp = '/home/mini/pyacq_emotiv_recording/alex/Emotiv Systems Pty Ltd #SN201105160008861.raw'
    filenameXY = '/home/mini/pyacq_emotiv_recording/alex/Emotiv Systems Pty Ltd #SN201105160008862.raw'
    
    precomputed = np.fromfile(filename , dtype = np.float32).reshape(-1, 14).transpose()
    precomputedImp = np.fromfile(filenameImp , dtype = np.float32).reshape(-1, 14).transpose()
    precomputedXY = np.fromfile(filenameXY , dtype = np.float32).reshape(-1, 2).transpose()
    
    t = Fake_TeleMir_Calibration(precomputedImp)
    
    app.exec_()
    
    t.close()
    





