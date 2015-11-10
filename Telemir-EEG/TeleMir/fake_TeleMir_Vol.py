# -*- coding: utf-8 -*-
"""
TeleMir phase 2 : vol
"""

from pyacq import StreamHandler, EmotivMultiSignals
from pyacq import StreamHandler, FakeMultiSignals
from pyacq.gui import Oscilloscope, TimeFreq
from TeleMir.gui import Topoplot, Topoplot_imp#, KurtosisGraphics, freqBandsGraphics

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

class Fake_TeleMir_Vol:

    def __init__(self, precomputed, precomputedXY):

        print "1"
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
        print "2"
         # Configure and start
        self.devXY = FakeMultiSignals(streamhandler = self.streamhandler)
        self.devXY.configure( #name = 'Test dev',
                                    nb_channel = 2,
                                    sampling_rate =128.,
                                    buffer_length = 30.,
                                    packet_size = 1,
                                    precomputed = precomputedXY,
                                    )
        self.devXY.initialize()
        self.devXY.start()
        print "3"
             ## Configure and start output stream (for extracted feature)
        self.fout = TransmitFeatures(streamhandler = self.streamhandler)
        self.fout.configure( #name = 'Test fout',
                                    nb_channel = 14, # np.array([1:5])
                                    nb_feature = 9,
                                    nb_pts = 128,
                                    sampling_rate =10.,
                                    buffer_length = 20.,
                                    packet_size = 1,
                                    )
        print "4"
        self.fout.initialize(stream_in = self.dev.streams[0])#, stream_xy = self.devXY.streams[0])
        print "5"
        self.fout.start()

        #self.screensize = np.array((1920))

        print "ici"
        # Impedances
        # self.w_imp=Topoplot_imp(stream = self.dev.streams[0], type_Topo = 'imp')
        # self.w_imp.show()

        # signal
        # numscreen = 1
        self.w_oscilo=Oscilloscope(stream = self.dev.streams[0])
        self.w_oscilo.auto_gain_and_offset(mode = 2)
        self.w_oscilo.set_params(xsize = 10, mode = 'scroll')
        self.w_oscilo.automatic_color('jet')
        # self.w_oscilo.move(self.screensize + (numscreen-1) * 800 ,200)
        #~ self.w_oscilo.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.w_oscilo.show()

        #parametres
        # numscreen = 2
        self.w_feat1=Oscilloscope(stream = self.fout.streams[0])
        self.w_feat1.auto_gain_and_offset(mode = 0)
        self.w_feat1.set_params(xsize = 10, mode = 'scroll')
        self.w_feat1.automatic_color('jet')
        # self.w_feat1.set_params(colors = [[0, 0, 255], [255, 0, 255], [255, 0 ,0], [255, 255, 0], [0, 255, 0],  [0, 255, 255]])
        self.w_feat1.set_params(ylims = [0,100])
        # self.w_feat1.move(self.screensize + (numscreen-1) * 800 ,200)
        #~ self.w_feat1.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.w_feat1.show()

        #topo
        # numscreen = 3
        # self.w_topo=Topoplot(stream = self.dev.streams[0], type_Topo = 'topo')
        # self.w_topo.move(self.screensize + (numscreen-1) * 800 ,200)
        # self.w_topo.show()

        # giro
        #~ self.w_xy=Oscilloscope(stream = self.devXY.streams[0])
        #~ self.w_xy.show()
        #~ self.w_xy.auto_gain_and_offset(mode = 1)
        #~ self.w_xy.set_params(xsize = 10, mode = 'scroll')

        # temps frequence
        # numscreen = 4
        # self.w_Tf=TimeFreq(stream = self.dev.streams[0])
        # self.w_Tf.set_params(xsize = 10)
        # self.w_Tf.change_param_tfr(f_stop = 45, f0 = 1)
        # self.w_Tf.move(self.screensize + (numscreen-1) * 800 ,200)
        # self.w_Tf.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        # self.w_Tf.show()

        # numscreen = 5
        # self.w_Tf2=TimeFreq2(stream = self.dev.streams[0])
        # self.w_Tf2.set_params(xsize = 10)
        # self.w_Tf2.change_param_tfr(f_stop = 45, f0 = 1)
        # self.w_Tf2.move(self.screensize + (numscreen-1) * 800 ,200)
        # self.w_Tf2.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        # self.w_Tf2.show()
        #w_Tf.change_param_channel(clim = 20)

        #~ # freqbands
        # numscreen = 6 # dans le code
        # self.w_sp_bd=freqBandsGraphics(stream = self.dev.streams[0], interval_length = 3., channels = [11])
        # self.w_sp_bd.run()





    def close(self):

        #close windows
        # self.w_imp.close()
        self.w_oscilo.close()
        self.w_feat1.close()
        # self.w_topo.close()
        # #~ self.w_xy.close()
        # self.w_Tf.close()
        # self.w_Tf2.close()
        #~ self.w_sp_bd.close()

        # Stope and release the device
        self.fout.stop()
        self.fout.close()
        self.dev.stop()
        self.dev.close()
        self.devXY.stop()
        self.devXY.close()



if __name__ == '__main__':


    app = QtGui.QApplication([])

    filename = 'E:\Documents\GitHub\TeleMir\\recorded_data\\alex\Emotiv Systems Pty Ltd #SN201105160008860.raw'
    filenameImp = 'E:\Documents\GitHub\TeleMir\\recorded_data\\alex\Emotiv Systems Pty Ltd #SN201105160008861.raw'
    filenameXY = 'E:\Documents\GitHub\TeleMir\\recorded_data\\alex\Emotiv Systems Pty Ltd #SN201105160008862.raw'

    precomputed = np.fromfile(filename , dtype = np.float32).reshape(-1, 14).transpose()
    precomputedImp = np.fromfile(filenameImp , dtype = np.float32).reshape(-1, 14).transpose()
    precomputedXY = np.fromfile(filenameXY , dtype = np.float32).reshape(-1, 2).transpose()

    t = Fake_TeleMir_Vol(precomputed, precomputedXY )

    app.exec_()

    t.close()
