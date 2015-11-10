# -*- coding: utf-8 -*-
"""
TeleMir developpement version with fake acquisition device

lancer dans un terminal :
python examples/test_osc_receive.py
"""

from pyacq import StreamHandler, FakeMultiSignals

from pyacq.gui import Oscilloscope, Oscilloscope_f, TimeFreq, TimeFreq2
from TeleMir.gui import Topoplot, KurtosisGraphics, freqBandsGraphics, spaceShipLauncher, Topoplot_imp

from TeleMir.gui import ScanningOscilloscope,SpectrumGraphics
from TeleMir.analyses import TransmitFeatures
#from TeleMir.example import test_osc_receive

import msgpack
#~ import gevent
#~ import zmq.green as zmq
 
from PyQt4 import QtCore,QtGui
#from multiprocessing import Process

import zmq
import msgpack
import time
import numpy as np

import os

def teleMir_CB():
       
    streamhandler = StreamHandler()
    
    # Configure and start
    #~ dev = FakeMultiSignals(streamhandler = streamhandler)
    #~ dev.configure( #name = 'Test dev',
                                #~ nb_channel = 14,
                                #~ sampling_rate =128.,
                                #~ buffer_length = 10.,
                                #~ packet_size = 1,
                                #~ )
    #~ dev.initialize()
    #~ dev.start()
    

    filename = '/home/ran/Projets/pyacq_emotiv_recording/alex/Emotiv Systems Pty Ltd #SN201105160008860.raw'
    #filename = '/home/ran/Projets/pyacq_emotiv_recording/caro/Emotiv Systems Pty Ltd  #SN201105160008860.raw'
    #filename = '/home/mini/pyacq_emotiv_recording/simple_blink/Emotiv Systems Pty Ltd  #SN201105160008860.raw'
    filenameImp = '/home/ran/Projets/EEG_recordings/anneLise/Emotiv Systems Pty Ltd #SN200709276578911.raw'
    filenameXY = '/home/ran/Projets/EEG_recordings/anneLise/Emotiv Systems Pty Ltd #SN200709276578912.raw'

    
    precomputed = np.fromfile(filename , dtype = np.float32).reshape(-1, 14).transpose()
    precomputedImp = np.fromfile(filenameImp , dtype = np.float32).reshape(-1, 14).transpose()
    precomputedXY = np.fromfile(filenameXY , dtype = np.float32).reshape(-1, 2).transpose()
    
    
    # Configure and start signal
    dev = FakeMultiSignals(streamhandler = streamhandler)
    dev.configure( #name = 'Test dev',
                                nb_channel = 14,
                                sampling_rate =128.,
                                buffer_length = 30.,
                                packet_size = 1,
                                precomputed = precomputed,
                                )
    dev.initialize()
    dev.start()
    
    #~ # Configure and start imp
    #~ devImp = FakeMultiSignals(streamhandler = streamhandler)
    #~ devImp.configure( #name = 'Test dev',
                                #~ nb_channel = 14,
                                #~ sampling_rate =128.,
                                #~ buffer_length = 30.,
                                #~ packet_size = 1,
                                #~ precomputed = precomputedImp,
                                #~ )
    #~ devImp.initialize()
    #~ devImp.start()
    
    # Configure and start gyroXY
    devXY = FakeMultiSignals(streamhandler = streamhandler)
    devXY.configure( #name = 'Test dev',
                                nb_channel = 2,
                                sampling_rate =128.,
                                buffer_length = 30.,
                                packet_size = 1,
                                precomputed = precomputedXY,
                                )
    devXY.initialize()
    devXY.start()
    
     ## Configure and start output stream (for extracted feature)
    fout = TransmitFeatures(streamhandler = streamhandler)
    fout.configure( #name = 'Test fout',
                                nb_channel = 14, # np.array([1:5])
                                nb_feature = 6,
                                nb_pts = 128,
                                sampling_rate =10.,
                                buffer_length = 10.,
                                packet_size = 1,
                                )
    fout.initialize(stream_in = dev.streams[0], stream_xy = devXY.streams[0]) 
    fout.start()
    
    #Osc server
    #p = Process(target=., args=('bob',))
    
    #color = 'summer'
    # Bleu
    #color = 'jet'
    # Rouge
    color = 'hot'
    # vert/jaune
    #color = 'summer'
    
    app = QtGui.QApplication([])
    
        
    # Impedances
    w_imp=Topoplot_imp(stream = dev.streams[0], type_Topo= 'imp')
    w_imp.show()
    
    # freqbands 
    w_sp_bd=freqBandsGraphics(stream = dev.streams[0], interval_length = 3., channels = [12])
    w_sp_bd.run()  
    
    # signal
    w_oscilo=Oscilloscope(stream = dev.streams[0])
    w_oscilo.show()
    w_oscilo.set_params(xsize = 10, mode = 'scroll')
    w_oscilo.auto_gain_and_offset(mode = 2)
    w_oscilo.gain_zoom(100)
    #w_oscilo.set_params(colors = 'jet')
    select_chan = np.ones(14, dtype = bool)
    w_oscilo.automatic_color(cmap_name = 'jet', selected = select_chan)
    
    # parametres
    w_feat1=Oscilloscope_f(stream = fout.streams[0])
    w_feat1.show()
    w_feat1.set_params(colormap = color)
    #w_feat1.auto_gain_and_offset(mode = 1)
    #w_feat1.set_params(xsize = 10, mode = 'scroll')
    #~ select_feat = np.ones(6, dtype = bool)
   #~ # print select
    #~ #w_oscilo.set_params(colormap = 'automn',  selected = select)
    #~ w_feat1.automatic_color(cmap_name = 'jet', selected = select_feat)
    w_feat1.showFullScreen()
    
    w_feat1.set_params(xsize = 10, mode = 'scroll')
    #~ select_feat = np.ones(4, dtype = bool)
    #~ w_feat1.automatic_color(cmap_name = 'jet', selected = select_feat)
    
    
    # topographie
    w_topo=Topoplot(stream = dev.streams[0], type_Topo= 'topo')
    w_topo.show()
    
    # temps frequence 1

    w_Tf=TimeFreq(stream = dev.streams[0])
    w_Tf.show()  
    w_Tf.set_params(xsize = 10)
    w_Tf.change_param_tfr(f_stop = 45, f0 = 1)
    w_Tf.set_params(colormap = color)
    #w_Tf.clim_changed(20)
    #w_Tf.change_param_channel(clim = 20)
    
    # temps frequence 2
    w_Tf2=TimeFreq2(stream = dev.streams[0])
    w_Tf2.show()  
    w_Tf2.set_params(xsize = 10)
    w_Tf2.change_param_tfr(f_stop = 45, f0 = 1)
    w_Tf2.set_params(colormap = color)
    
    
    # kurtosis 
    #w_ku=KurtosisGraphics(stream = dev.streams[0], interval_length = 1.)
    #w_ku.run()  
    

    ## Bien moins fluide
    # Spectre
    #~ w_sp=SpectrumGraphics(dev.streams[0],3.,channels=[11,12])
    #~ w_sp.run()
    
    w1 = spaceShipLauncher(dev.streams[0])
    w1.run()
    w1.showFullScreen()

    
    app.exec_()
    
    # Stope and release the device
    fout.stop()
    fout.close()  
    print 'ici'
    dev.stop()
    dev.close()
    print 'ici'
    devXY.stop()
    devXY.close()
    print 'ici'
    devImp.stop()
    devImp.close()
    print 'ici'

if __name__ == '__main__':
    teleMir_CB()
