# -*- coding: utf-8 -*-
"""
TeleMir application - with fake devices
"""
from pyacq import StreamHandler, EmotivMultiSignals
from PyQt4 import QtCore,QtGui
from TeleMir import TeleMir_Calibration, TeleMir_Vol
import numpy as np
from PyQt4.phonon import Phonon
import OSC
import threading

class TeleMirMainWindow(QtGui.QWidget):

    def __init__(self):
        super(TeleMirMainWindow, self).__init__()
        self.initUI()

    def initUI(self):

        self.setGeometry(300, 300, 250, 250)
        self.setWindowTitle('TeleMir')
        #~ self.setWindowIcon(QtGui.QIcon('web.png'))

        self.btn_1 = QtGui.QPushButton('Calibration', self)
        self.btn_1.clicked.connect(self.calibration)
        self.btn_1.resize(self.btn_1.sizeHint())
        self.btn_1.move(90, 50)
        self.btn_1.setEnabled(True)

        self.btn_2 = QtGui.QPushButton('Start', self)
        self.btn_2.clicked.connect(self.start)
        self.btn_2.resize(self.btn_2.sizeHint())
        self.btn_2.move(90, 100)
        self.btn_2.setEnabled(False)

        self.btn_3 = QtGui.QPushButton('Stop', self)
        self.btn_3.clicked.connect(self.stop)
        self.btn_3.resize(self.btn_3.sizeHint())
        self.btn_3.move(90, 150)
        self.btn_3.setEnabled(False)


        self.oscIP = '127.0.0.1'
        self.oscPort = 9009
        self.oscClient = OSC.OSCClient()
        self.oscMsg = OSC.OSCMessage()

        self.receive_address = self.oscIP, 9010

        self.mainScreen = 1920
        self.subScreen = 640
        self.screensize = np.array((1920))
        self.show()

        self.state = 0
        self.oscServer = OSC.ThreadingOSCServer(self.receive_address)
        self.oscServer.addMsgHandler("/stop", self.stop_handler)
        self.serverThread = threading.Thread(target=self.oscServer.serve_forever)
        self.serverThread.start()

        self.streamhandler = StreamHandler()
        ## Configure and start
        self.dev = EmotivMultiSignals(streamhandler = self.streamhandler)
        self.dev.configure(buffer_length = 1800) # doit être un multiple du packet size
        self.dev.initialize()
        self.dev.start()

    def stop_handler(self, arg1, arg2, arg3, arg4):
        print "OSC stop received"
        if self.state == 1:
            self.stop()

    def calibration(self):

        print 'TeleMir :: Calibration'

        self.sendOSC('/calib', self.oscPort)
        self.TC = TeleMir_Calibration()
        self.btn_1.setEnabled(False)
        self.btn_2.setEnabled(True)
        print 'TeleMir :: fin Calibration'

    def start(self):

        print 'TeleMir :: entree start'
        self.state = 1
        # self.oscServer = OSC.ThreadingOSCServer(self.receive_address)
        # self.oscServer.addMsgHandler("/stop", self.stop)
        # self.serverThread = threading.Thread(target=self.oscServer.serve_forever)

        ## Boutons
        self.btn_2.setEnabled(False)
        self.btn_3.setEnabled(True)

        self.TV = TeleMir_Vol()
        self.sendOSC('/start', self.oscPort)
        # self.serverThread.start()

        ## Close Calibration phase
        self.TC.close()
        # self.vp1.close()
        # self.vp2.close()
        print "sortie start"

    def stop(self):
        print 'TeleMir :: entree stop'
        self.state = 0
        self.sendOSC('/stop', self.oscPort)
        # self.serverThread.
        # self.oscServer.close()
        ## Boutons
        self.btn_1.setEnabled(True)
        self.btn_2.setEnabled(False)
        self.btn_3.setEnabled(False)
        ## Close Vol phase
        self.TV.close()
        print 'TeleMir :: sortie stop'

    def addNext(media, media_file):
        media.enqueue(Phonon.MediaSource(media_file))
    #def setScreen(self, Qwidget, screenNumber):

    def sendOSC(self,features, port):
        self.oscMsg.append(features)
        self.oscClient.sendto(self.oscMsg, (self.oscIP, port))
        self.oscMsg.clearData()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = TeleMirMainWindow()
    app.exec_()
