


# -*- coding: utf-8 -*-
"""

Very simple acquisition with a fake multi signal device.

"""
from TeleMir.gui import ScanningOscilloscope,KurtosisGraphics,KurtosisGraphicsSci,SpectrumGraphics,freqBandsGraphics,spaceShipLauncher,Oscilloscope

from pyacq import StreamHandler, FakeMultiSignals
from pyqtgraph.Qt import QtGui, QtCore
import zmq
import msgpack
import time
import numpy as np

def test1():
    import sys
    np.random.seed(6)
    app=QtGui.QApplication([])

    streamhandler = StreamHandler()
    
    # Configure and start
    dev = FakeMultiSignals(streamhandler = streamhandler)
    dev.configure(#name = 'Test dev',
                                nb_channel = 14,
                                sampling_rate =1000.,
                                buffer_length = 6.4,
                                packet_size = 1,
                                )
    dev.initialize()
    dev.start()
    
    # Read the buffer on ZMQ socket
    port = dev.streams[0]['port']
    np_array = dev.streams[0]['shared_array'].to_numpy_array()
    print np_array.shape # this should be (nb_channel x buffer_length*samplign_rate)

    #initialize plots
    
 #   w1 = ScanningOscilloscope(dev.streams[0],2.,channels=[0])
#    w2 = Oscilloscope(dev.streams[0],2.,channels=[0,1,2])
    w1 = spaceShipLauncher(dev.streams[0])
   # w1 = freqBandsGraphics(dev.streams[0],5.,channels=[1])
  #  w1 = SpectrumGraphics(dev.streams[0],2.,logMode=True,channels=range(2))
  #  w1 = SpectrumGraphics(dev.streams[0],2.,logMode=True,channels=range(14),octavMode=True,octaveRan=1.26)
    
#    w1 = KurtosisGraphicsSci(dev.streams[0],2.,channels=range(10),title='Kurtosis')
    
#    w1.setFixedSize(600,600)
    #start plots
    w1.run()
   # w2.run()

#    timer=QtCore.QTimer()
#    timer.timeout.connect(w1.update)
#    timer.start(100)

   # w2.run()    

 #   w1.showFullScreen()
    #When you close the window the fake device stop emmiting
    w1.connect(w1,QtCore.SIGNAL("fermeturefenetre()"),dev.stop)
    dev.close()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


if __name__ == '__main__':

    test1()

