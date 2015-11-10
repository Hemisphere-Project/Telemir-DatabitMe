# -*- coding: utf-8 -*-
"""


"""

from TeleMir.gui import ScanningOscilloscope,KurtosisGraphics,SpectrumGraphics,spaceShipLauncher,Topoplot

from pyacq import StreamHandler, FakeMultiSignals, EmotivMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq


import msgpack

from PyQt4 import QtCore,QtGui

import zmq
import msgpack
import time

def main():
    streamhandler = StreamHandler()
    

    dev = EmotivMultiSignals(streamhandler = streamhandler)
    dev.configure(buffer_length = 1800,device_path = '',) # doit être un multiple du packet size
    
    
    
    # Configure and start
    #dev = FakeMultiSignals(streamhandler = streamhandler)
    #dev.configure( #name = 'Test dev',
     #                           nb_channel = 14,
      #                          sampling_rate =128.,
       #                         buffer_length = 10.,
        #                        packet_size = 1,
         #                       )
    
    dev.initialize()
    dev.start()
    
    app = QtGui.QApplication([])
#    w1=ScanningOscilloscope(dev.streams[2],2.,channels=[0,1])
    w1=spaceShipLauncher(dev.streams[2])
#    w1=SpectrumGraphics(dev.streams[0],3.,channels=[11,12])
  #  w2=KurtosisGraphics(dev.streams[0],3.,channels=range(2,8))
#    w2=Topoplot(stream = dev.streams[1], type_Topo ='imp')
    w1.run()
 #   w2.show()

    #w1.showFullScreen()
    
    app.exec_()
    
    w1.connect(w1,QtCore.SIGNAL("fermeturefenetre()"),dev.stop)
    dev.close()
    



if __name__ == '__main__':
    main()
