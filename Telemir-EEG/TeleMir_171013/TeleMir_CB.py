# -*- coding: utf-8 -*-
"""
Topoplot example

ca marche pas terrible tout ca
"""

from pyacq import StreamHandler, EmotivMultiSignals
from pyacq.gui import Oscilloscope, Oscilloscope_f, TimeFreq, TimeFreq2
from TeleMir.gui import Topoplot, KurtosisGraphics, freqBandsGraphics, spaceShipLauncher, Topoplot_imp
from TeleMir.gui import ScanningOscilloscope,SpectrumGraphics
from TeleMir.analyses import TransmitFeatures

import msgpack
#~ import gevent
#~ import zmq.green as zmq

from PyQt4 import QtCore,QtGui
from PyQt4.QtCore import QTimer

import zmq
import msgpack
import time
import numpy as np

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
                                nb_feature = 6,
                                nb_pts = 128,
                                sampling_rate =10.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    fout.initialize(stream_in = dev.streams[0], stream_xy = dev.streams[2]) 
    fout.start()

    # 1 : Rouge
    #~ color = 'hot'
    # 2 : vert/jaune
    #~ color = 'summer'
    # 3 : Bleu
    color = 'jet'
    
    app = QtGui.QApplication([])
    
    # Impedances
    w_imp=Topoplot_imp(stream = dev.streams[1], type_Topo= 'imp')
    w_imp.show()
    
    # freqbands 
    w_sp=freqBandsGraphics(stream = dev.streams[0], interval_length = 1., channels = [12])
    w_sp.run()  
    
    #spaceship
    #~ w_spsh=spaceShipLauncher(dev.streams[2], cubeColor = color)
    #~ w_spsh.run()

    # signal
    w_oscilo=Oscilloscope(stream = dev.streams[0])
    w_oscilo.show()
    w_oscilo.auto_gain_and_offset(mode = 2)
    #w_oscilo.gain_zoom(10)
    w_oscilo.set_params(xsize = 10, mode = 'scroll')
    select_chan = np.ones(14, dtype = bool)
    w_oscilo.automatic_color(cmap_name = 'jet', selected = select_chan)
    
    # parametres
    w_feat1=Oscilloscope_f(stream = fout.streams[0])
    w_feat1.show()
    w_feat1.set_params(xsize = 10, mode = 'scroll')
    select_feat = np.ones(6, dtype = bool)
    w_feat1.automatic_color(cmap_name = 'jet', selected = select_feat)
    
    #topographie
    w_topo=Topoplot(stream = dev.streams[0], type_Topo = 'topo')
    w_topo.show()
    
    # temps frequence 1
    w_Tf1=TimeFreq(stream = dev.streams[0])
    w_Tf1.show()  
    w_Tf1.set_params(xsize = 10)
    w_Tf1.set_params(colormap = color)
    w_Tf1.change_param_tfr(f_stop = 45, f0 = 1)
    
    
    # temps frequence 2
    w_Tf2=TimeFreq2(stream = dev.streams[0])
    w_Tf2.show()  
    w_Tf2.set_params(xsize = 10)
    w_Tf2.change_param_tfr(f_stop = 45, f0 = 1)
    w_Tf2.set_params(colormap = color)
    
    
    #~ timer = QTimer()
    #~ timer.setInterval(3000) # 5 seconds
    #~ timer.start()
    #~ timer.timeout.connect(app.quit)
    
    app.exec_()
    #app.startTimer(2000)
    
    # Stope and release the device
    fout.stop()
    fout.close()  
    dev.stop()
    dev.close()



if __name__ == '__main__':
    
    teleMir_CB()
    
    print "suivant"





