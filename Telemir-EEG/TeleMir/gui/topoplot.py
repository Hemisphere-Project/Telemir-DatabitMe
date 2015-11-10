# -*- coding: utf-8 -*-

# 3d plot in pyqtgraph :
# apt-get install python-opengl
# apt-get install python-qt4-gl

from PyQt4 import QtCore,QtGui
from PyQt4 import Qt
import pyqtgraph as pg
import zmq
import pyacq
import numpy as np

from pyacq.gui.tools import RecvPosThread
#from pyacq.guiutil import *
#from pyacq.multichannelparam import MultiChannelParam

from matplotlib.cm import get_cmap
from matplotlib.colors import ColorConverter
import time

import pyqtgraph.opengl as gl


class Topoplot(QtGui.QWidget):
    def __init__(self, stream = None, parent = None, type_Topo = 'topo'):
        QtGui.QWidget.__init__(self, parent)
        
        assert type(stream).__name__ == 'AnalogSignalSharedMemStream'
        
        self.stream = stream
        
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.SUBSCRIBE,'')
        self.socket.connect("tcp://localhost:{}".format(self.stream['port']))
        
        self.thread_pos = RecvPosThread(socket = self.socket, port = self.stream['port'])
        self.thread_pos.start()
        
        # Create parameters
        n = stream['nb_channel']
        self.np_array = self.stream['shared_array'].to_numpy_array()
        self.half_size = self.np_array.shape[1]/2
        sr = self.stream['sampling_rate']
        
        if type_Topo == 'topo':
            self.imgLevels = (7500,9500)
            self.iblack = 0
            self.colormap = "jet"
        if type_Topo == 'imp':
            self.imgLevels = (0,15)
            self.iblack = 0
            self.colormap = "winter"
        if type_Topo == 'fakeAc':
            self.imgLevels = (-100,100)
            self.iblack = 500
            self.colormap = "jet"
    
        # Matrix initialisation
        self.data = np.zeros((6,6), dtype=np.int)
        self.chanName = [ 'F3', 'F4', 'P7', 'FC6', 'F7', 'F8','T7','P8','FC5','AF4','T8','O2','O1','AF3'] 
        self.chanPosX=[2,3,1,4,0,5,0,4,1,4,5,3,2,1]
        self.chanPosY=[5,5,2,4,5,5,3,2,4,6,3,1,1,6]
        
        #Graphical instances
        self.mainlayout = QtGui.QVBoxLayout()
        self.setStyleSheet("background-color:black;");
        self.setLayout(self.mainlayout)
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle('pyqtgraph example: Isocurve')
        self.vb = self.win.addViewBox()
        self.img = pg.ImageItem(self.data)
        self.vb.addItem(self.img)
        self.vb.setAspectLocked()
        self.mainlayout.addWidget(self.win)
        
        #window option
        self.setWindowTitle('Topographie')
        #~ self.resize(1200, 1768)
        #~ self.move(7034, 0)
        self.resize(800, 600)
        #~ self.move(5920, 0)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
     
        # Set the sensor names
        self.setNameChan()
        
        # colormap 
        self.lut = [ ]
        self.cmap = get_cmap(self.colormap , 2000)
        for i in range(2000):
            r,g,b =  ColorConverter().to_rgb(self.cmap(i) )
            self.lut.append([r*255,g*255,b*255])
            self.jet_lut = np.array(self.lut, dtype = np.uint8)
        
        # associate black to the rest of the matrix (where there is no chan)
        self.jet_lut[self.iblack,:] = [0,0,0]
        
        self.timer = QtCore.QTimer(interval = 100)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        
        self.img.setImage(self.data, lut = self.jet_lut, levels=self.imgLevels)
        
    def setNameChan(self):
        for i in range(0,14):	
            self.txt = pg.TextItem(self.chanName[i], color = (0,0,0))
            self.txt.setPos(self.chanPosX[i],self.chanPosY[i])
            self.vb.addItem(self.txt)
        
    def refresh(self):
        self.getChanMatrix()
        self.img.setImage(self.data, lut = self.jet_lut, levels=self.imgLevels)
        
        
    def getChanMatrix(self):
        pos = (self.thread_pos.pos - 1)%self.half_size
        
        #~ if self.np_array.shape[1] > 128:
            #~ meanchan = np.average(self.np_array[:,pos-128:pos], dim =1)
            #~ dataChan = self.np_array[:,pos] - meanchan
        #~ else:
            #~ dataChan = self.np_array[:,pos]
        
        dataChan = self.np_array[:,pos]
        
        # commence en bas a gauche a (0,0), dim1 = g, dim2 = haut
        self.data[1,5] = dataChan[13]   # AF3
        self.data[4,5] = dataChan[9]     # AF4
        self.data[0,4] = dataChan[4]     # F7
        self.data[2,4] = dataChan[0]     # F3
        self.data[3,4] = dataChan[1]     # F4
        self.data[5,4] = dataChan[5]     # F8
        self.data[1,3] = dataChan[8]     # FC5
        self.data[4,3] = dataChan[3]     # FC6
        self.data[0,2] = dataChan[6]     # T7
        self.data[5,2] = dataChan[10]   # T8
        self.data[1,1] = dataChan[2]     # P7
        self.data[4,1] = dataChan[7]     # P8
        self.data[2,0] = dataChan[12]   # O1
        self.data[3,0] = dataChan[11]   # O2
        
        
        
        
        
        