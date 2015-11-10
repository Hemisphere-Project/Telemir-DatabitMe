# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import zmq
import msgpack
from pyacq.gui.tools import RecvPosThread
import time

class GraphicsWorker:
    '''
    /!\Cette classe n'est jamais instanciée directement.
    Elle contient le code qui connecte le worker à un port, 
    le code qui met à jour les positions des informations à
    lire (self.init). Les classes qui en héritent doivent surcharger
    initPlots (mise en place des graphs dans la fenêtre) et 
    updatePlots (mise à jour des graphiques).
    Les flux lus sont des flux de positions fournis par pyacq.
    Les paramètres sont:
    Le flux à lire.
    La taille de la fenêtre temporelle traitée, en seconde.
    (/!\Des comportements étranges peuvent apparaître dans le cas où cette taille proche
    de la taille du buffer dans lequel le flux est écrit.)
    Les canaux à traiter.
    '''
    
    def __init__(self,stream,time_window,channels=None):
        #FIXME : vérifier le type du stream

        #Définition de la zone de mémoire à lire
        self.shared_array=stream['shared_array'].to_numpy_array()
        self.half_size=self.shared_array.shape[1]/2
       
        #Choix des canaux à traiter (tous par défaut)
        if channels==None:
            self.channels=np.arange(self.shared_array.shape[0])
        else:
            self.channels=channels

        #Définition de la fenêtre temporelle traitée
        self.time_window=time_window
        self.init=self.half_size
        self.interval_length=int(time_window*stream['sampling_rate'])
        self.data=self.shared_array[:,self.init:self.init+self.interval_length]

        #initialisation de la connexion
        self.port=stream['port']
        self.context=zmq.Context()
        self.socket=self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:%d"%self.port)
        self.socket.setsockopt(zmq.SUBSCRIBE,'')
        
        #initialisation de la pile de réception des positions
        self.threadPos=RecvPosThread(socket=self.socket,port=self.port)
        self.threadPos.start()

        #initialisation du timer de rafraichissement du graphe
        self.timer=QtCore.QTimer()   
        self.timer.timeout.connect(self.updateGW)
        
        #periode de rafraichissement de l'image, ms
        self.period=100

        
    def initPlots(self):
        raise NotImplementedError

    def run(self):
        self.initPlots()
        self.timer.start(self.period)#taux de rafraichissement de l'image

    def updatePlots(self):
        raise NotImplementedError
        
    def updateGW(self):
        #Réception de la position de la dernière information écrite
        t=self.threadPos.pos
        #print t,' shared_array ',self.shared_array
        self.init=t%(self.half_size)+self.half_size
        #mise à jour de la fenêtre de lecture
        self.data=self.shared_array[:,self.init-self.interval_length:self.init]
        #mise à jour du graph
        self.updatePlots()


class PyQtGraphicsWorker(GraphicsWorker,pg.GraphicsWindow):
    '''
    Héritage de GraphicsWorker qui sert à utiliser pyqtgraph.
    '''
    
    def __init__(self,stream,time_window,channels=None,title=None,**kwargs):
        pg.GraphicsWindow.__init__(self,title)
        GraphicsWorker.__init__(self,stream,time_window,channels)

        #création d'une variable qui contiendra les courbes construites,
        #permettant ainsi la mise à jour de manière trés simple
        self.c={}
        
    #utile pour lier l'arrêt du programme à la fermeture de la fenêtre
    def closeEvent(self,event):
        self.emit(QtCore.SIGNAL("fermeturefenetre()"))
        
    #gestion des évènements clavier
    def keyPressEvent(self,e):
        #sortir du mode plein écran
        if e.key()==pg.QtCore.Qt.Key_Escape:
            self.showNormal()

