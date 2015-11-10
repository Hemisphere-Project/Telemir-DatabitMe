# -*- coding: utf-8 -*-
"""
Topoplot example
"""

from pyacq import StreamHandler, EmotivMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq
from TeleMir.gui import Topoplot, KurtosisGraphics, freqBandsGraphics, spaceShipLauncher
from TeleMir.gui import ScanningOscilloscope,SpectrumGraphics
from TeleMir.analyses import TransmitFeatures

import msgpack
#~ import gevent
#~ import zmq.green as zmq

from PyQt4 import QtCore,QtGui

import zmq
import msgpack
import time

def teleMir_CB():
    streamhandler = StreamHandler()
    
    # Configure and start
    dev = EmotivMultiSignals(streamhandler = streamhandler)
    dev.configure(buffer_length = 1800, # doit être un multiple du packet size
                                device_path = '',)
    dev.initialize()
    dev.start()
    
     ## Configure and start output stream (for extracted feature)
    fout = TransmitFeatures(streamhandler = streamhandler)
    fout.configure(# name = 'Test fout',
                                nb_channel = 14, # np.array([1:5])
                                nb_feature = 4,
                                nb_pts = 128,
                                sampling_rate =10.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    fout.initialize(stream_in = dev.streams[0]) 
    fout.start()
    
    
    app = QtGui.QApplication([])

    #impédances
    w_imp=Topoplot(stream = dev.streams[1], type_Topo = 'imp')
    w_imp.show()
    
    w_oscilo=Oscilloscope(stream = dev.streams[1])
    w_oscilo.show()
    
    app.exec_()
    
    # Stope and release the device
    fout.stop()
    fout.close()  
    dev.stop()
    dev.close()



if __name__ == '__main__':
    teleMir_CB()
