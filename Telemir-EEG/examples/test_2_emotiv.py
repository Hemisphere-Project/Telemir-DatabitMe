# -*- coding: utf-8 -*-
"""
Topoplot example
"""

from pyacq import StreamHandler, EmotivMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq
from TeleMir.gui import Topoplot, KurtosisGraphics, freqBandsGraphics

import msgpack
#~ import gevent
#~ import zmq.green as zmq

from PyQt4 import QtCore,QtGui

import zmq
import msgpack
import time
from TeleMir.analyses import TransmitFeatures

def teleMir_CB():
    streamhandler = StreamHandler()
    
    # Configure and start
    dev1 = EmotivMultiSignals(streamhandler = streamhandler)
    dev1.configure(buffer_length = 1800, # doit être un multiple du packet size
                                device_path = '/dev/hidraw3',)
    dev1.initialize()
    dev1.start()
    
    dev2 = EmotivMultiSignals(streamhandler = streamhandler)
    dev2.configure(buffer_length = 1800, # doit être un multiple du packet size
                                device_path = '/dev/hidraw5',)
    dev2.initialize()
    dev2.start()
    
    
    app = QtGui.QApplication([])

    # gyro 1
    w_oscilo1=Oscilloscope(stream = dev1.streams[2])
    w_oscilo1.show()
    
    # gyro 2
    w_oscilo2=Oscilloscope(stream = dev2.streams[2])
    w_oscilo2.show()
    
    
    app.exec_()
    
    # Stope and release the device
    dev1.stop()
    dev1.close()
    dev2.stop()
    dev2.close()


if __name__ == '__main__':
    teleMir_CB()
