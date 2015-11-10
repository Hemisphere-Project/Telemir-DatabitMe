# -*- coding: utf-8 -*-
"""
Transmit Stream oscillo Example
"""

from pyacq import StreamHandler, FakeMultiSignals
from pyacq.gui import Oscilloscope
from TeleMir.analyses import TransmitFeatures

import msgpack

from PyQt4 import QtCore,QtGui

def run_test():
    streamhandler = StreamHandler()
    
     ## Configure and start acquisition stream
    dev = FakeMultiSignals(streamhandler = streamhandler)
    dev.configure( #name = 'Test dev',
                                nb_channel = 14,
                                sampling_rate =128.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    dev.initialize()
    dev.start()
    
    ## Configure and start output stream (for extracted feature)
    fout = TransmitFeatures(streamhandler = streamhandler)
    fout.configure( #name = 'Test fout',
                                nb_channel = 14, # np.array([1:5])
                                nb_feature = 21,
                                nb_pts = 128,
                                sampling_rate =10.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    fout.initialize(stream_in = dev.streams[0]) 
    fout.start()
    
    app = QtGui.QApplication([])
    
    w_in=Oscilloscope(stream = dev.streams[0])
    w_in.show()
    
    w_out=Oscilloscope(stream = fout.streams[0])
    w_out.show()
    

    app.exec_()


    ## Stop and release devices
    fout.stop()
    fout.close()   
    dev.stop()
    dev.close()
    print 'fout and dev devises closed'
    

if __name__ == '__main__':
    run_test()
