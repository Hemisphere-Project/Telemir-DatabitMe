# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyqtgraphWorker as pw    
from scipy import fft
import BarGraphItem as bg
import random

class freqBandsGraphics(pw.PyQtGraphicsWorker):
    '''
    Cette classe permet la visualisation de la puissance moyenne dans des bandes de fréquences.
    Les bandes par défaut sont celles standards de l'eeg. Les bandes peuvent être chevauchantes
    Le mode couleur colore les bandes en fonction de leur valeur de puissance.
    '''

    def __init__(self, stream, interval_length, colorMode=True,
                 bands=np.array([[1,4],[4,8],[8,13],[13,30],[30,45],[12,16]]),
                 bands_titles=[QtCore.QString(QtCore.QChar(948)),QtCore.QString(QtCore.QChar(952)),QtCore.QString(QtCore.QChar(945)),QtCore.QString(QtCore.QChar(946)),QtCore.QString(QtCore.QChar(947)),QtCore.QString(QtCore.QChar(956))],
                 channels=None, title=None, **kwargs
                 ):
        super(freqBandsGraphics,self).__init__(stream,interval_length,channels,title,**kwargs)
        self.interval_length_sec=interval_length

        self.bands=bands
        self.titles=bands_titles
        self.labels={}

        #frequence max en entier
        self.freqMax=np.amax(self.bands)
        self.nFreqMax=int(self.freqMax*interval_length)
            
        #Fourrier
        if self.nFreqMax > self.interval_length/2:
            self.nFreqMax = self.interval_length/2
                    
        #Pile contenant les dernières puissances
        self.stackLen=100
        self.lastResults={}
        self.posLastResult=0

        #Modes d'affichage
        self.colorMode=colorMode
        
        #window option
        numscreen = 6
        self.setWindowTitle('Spectre')
        #self.resize(1014, 750)
        self.resize(800, 600)
        #~ self.move(1920, 0)
        self.move(1920 + (numscreen-1) * 800 ,200)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.show()
        
    def initPlots(self):
        #Construction de l'axe des abscisses
        x0=self.bands[:,0]
        x1=self.bands[:,1]

        self.barGraphs={}

    #Ajout des étiquettes correspondant aux noms des bandes de fréquence
        #Ajout d'une view box de taille limitée
        v=self.addViewBox()
        v.setMaximumHeight(80)
        #création du widget qui soutient le texte
        p=pg.PlotItem(None)
        #Effacer les axes
        p.showAxis('bottom',False)
        p.showAxis('left',False)
        #mettre l'axe des abscisses à la bonne échelle
        p.getAxis('bottom').setRange(0,self.freqMax)
        #définition des étiquettes
        for i in range(len(self.bands)):
            self.labels[i]=pg.TextItem(html='<div style="text-align: center"><span style="color: #DDD; font-size: 19pt;">'
                                       + self.titles[i] + '</span></div>')
            p.addItem(self.labels[i])
            self.labels[i].setPos(sum(self.bands[i])/2./50.,0.5)
        v.addItem(p)

        self.nextRow()
        
        #window option
        #~ self.setWindowTitle('Spectre')
        #~ self.resize(1000, 600)
        #~ self.move(4000, 0)

            
        for i in self.channels:
            #calcul des fft
            spectrum=np.array(abs(fft(self.data[i]))[1:self.nFreqMax+1])
            
            #calcul des puissances par bandes
            pows=self.bands_power(spectrum)

            #Création de la pile des résultats passees
            self.lastResults[i]=np.zeros(self.stackLen*(len(pows))).reshape(self.stackLen,len(pows))
            self.lastResults[i][0]=pows
            self.posLastResult=1
                
            if self.colorMode:
                #Couleurs en fonction des valeurs de puissances
                #initialisation du gradient
                self.colMap=pg.ColorMap(pos=np.array([1,0.7]),
                                        color=np.array([[255,0,0,128],[0,0,255,128]]),
                                        )
                brushes=self.scaledBrushes(pows,i)
            else:
                brushes=None

                
            #affichage
            p=self.addPlot(None)
            self.barGraphs[i]=bg.BarGraphItem(x0=x0,
                                              x1=x1,
                                              height=pows,
                                              brushes=brushes 
                                              )
            
            p.addItem(self.barGraphs[i])

            #effacer l'axe des ordonnées
            p.showAxis('left',False)
            self.nextRow()
             
    #Construit une liste de couleurs associées aux valeurs de pissances,
    #Compatible avec l'affichage des barGraphItem
    def scaledBrushes(self,spectrum,chan):
        #étalonnage sur du gradient sur les valeurs des résultats passés
        self.sMax=np.amax(self.lastResults[chan])                
        self.colMap.pos[0]=self.sMax
        
        #choix des couleurs en fonction des puissances
        return self.colMap.map(spectrum)

    #Construit les couleurs en hexadécimal à partir d'une liste de tuples (r,g,b,a)
    #Perd l'information alpha
    def brushesToHtmlColors(self,brushes):
        ret=[]
        for r,g,b,a in brushes:
            col=''.join([hex(int(r/16))[-1],
                         hex(int(g/16))[-1],
                         hex(int(b/16))[-1],
                         ])
            ret.append(col)
        return ret
    
    
    def updateLabelsColor(self,colors):
        for i,label in self.labels.items():
            label.setHtml('<div style="text-align: center"><span style="color: #'
                          + colors[i]
                          + '; font-size: 19pt;">'+self.titles[i]+'</span></div>')

    #Calcul des puissance des bandes
    def bands_power(self,spectrum):
        pows=[]
        for f0,f1 in self.bands:
            #Conversion des Hz vers les entiers (sortie de la fft)
            nf0=f0*self.interval_length_sec
            nf1=f1*self.interval_length_sec
                 
            
            if int(nf1)-int(nf0)==0:
                bandes.append(spectrum[int(nf0)])

            #Cas où l'octave est comprise dans une unique fréquence
            if int(nf1)-int(nf0)==0:
                bandes.append(spectrum[int(nf0)-1])
            #Cas où l'octave chevauche plusieurs fréquences :
            else :
                #somme des puissances des fréquences entièrement comprises dans l'octave
                #plus de celles des extrémités, pondérée par largeur de celles-ci comprises
                #dans la bandes
                som=(int(nf0)+1-nf0)*spectrum[int(nf0)-1] + np.sum(spectrum[int(nf0):int(nf1)-1]) + (nf1-int(nf1))*spectrum[int(nf1)-1] 
                mean=som/(f1-f0)
                pows.append(mean)

        return pows

    def updatePlots(self):

        for i in self.channels:
            #calcul des fft
            spectrum=np.array(abs(fft(self.data[i]))[1:self.nFreqMax+1])
                
            pows=self.bands_power(spectrum)

            #enregistrement dans la pile de sauvegardes
            self.lastResults[i][self.posLastResult]=pows
                
            if self.colorMode:
                #étalonnage du gradient de couleurs sur les valeurs des résultats précédents
                brushes=self.scaledBrushes(pows,i)
            else:
                brushes=None
                
            #mise à jour des graphes           
            self.barGraphs[i].updateHeights(pows,brushes)

        #Mise à jour de la position des résultats enrgistrés dans la pile
        self.posLastResult=(self.posLastResult+1)%self.stackLen
        #Mise à jour de la couleur de étiquettes (très important)
        self.updateLabelsColor(self.brushesToHtmlColors(brushes))

    #Adapte l'échelle verticale
    def adaptRange(self):
        for i in self.channels:
            maxS=np.max(self.lastResults[i])
            self.barGraphs[i].parentWidget().setRange(yRange=(0,maxS*1.1))
            
    def keyPressEvent(self,e):
        if e.key()==pg.QtCore.Qt.Key_Escape:
            self.showNormal()
        elif e.key()==pg.QtCore.Qt.Key_Space:
            self.adaptRange()

    def close(self):
        self.close()
    