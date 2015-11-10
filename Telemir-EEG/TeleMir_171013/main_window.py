# -*- coding: utf-8 -*-
"""


"""

import TeleMir

from pyacq import StreamHandler, EmotivMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq


import msgpack

from PyQt4 import QtCore,QtGui

import zmq
import msgpack
import time

def main():
    streamhandler = StreamHandler()
    

    dev = EmotivMultiSignals(streamhandler = streamhandler)
    dev.configure(buffer_length = 1800)
    dev.initialize()
    dev.start()
    
    app = QtGui.QApplication([])
    w1=Oscilloscope(stream = dev.streams[0])
    w1.auto_gain_and_offset(mode = 2)
    w1.change_param_global(xsize = 10., refresh_interval = 100)
    w1.show()
    
    w2 = TimeFreq(stream = dev.streams[0], max_visible_on_open = 4)
    w2.change_param_global(refresh_interval = 100, xsize = 2.)
    w2.show()
    
    app.exec_()
    
    dev.stop()
    dev.close()



if __name__ == '__main__':
    main()
