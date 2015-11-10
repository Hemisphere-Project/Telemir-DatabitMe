# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyqtgraphWorker as pw    
from scipy import fft
import BarGraphItem as bg

class SpectrumGraphics(pw.PyQtGraphicsWorker):
    '''
    Cette classe permet la visualisation en temps réel du spectre en fréquence d'un signal.
    Une fft est effectuée sur une fenêtre glissante, dont la taille est définie par l'utilisateur.
    Les fenêtres successives sont chevauchantes.
    Les paramètres sont :
     - Le flux qui enrobe le signal
     - La taille de la fenêtre sur laquelle la fft est calculée
     - La fréquence maximal souhaitée
     
     Les options possibles sont :
      - Axe logarithmique
      - Affichage des octaves plutôt que des fréquences seuls (moyennage des puissances)
      - Plutôt que des octaves, l'utilisateur peut choisr d'afficher le moyennage des puissances 
        sur d'autres intervals, en fixant le rapport entre les bandes successives (ex :
          octave : 2, tiers d'octave : 1.26 )
      - Affichage d'une couleur en fonction de la puissance associée à la fréquence.

    Appuyer sur Espace pour adapter l'échelle de l'axe des ordonnées.

    A faire : en logMode, les graduations ne correspondent pas aux fréquences en Hz
'''


    def __init__(self,stream,interval_length,freqMax=50,colorMode=True,octavMode=False,octavRan=2,channels=None,logMode=False,title=None,**kwargs):
        super(SpectrumGraphics,self).__init__(stream,interval_length,channels,title,**kwargs)

        self.interval_length_sec=interval_length
            
            #Shannon
        if freqMax > stream['sampling_rate']/2:
            freqMax = stream['sampling_rate']/2
			
            #frequence max en entier
        self.freqMax=freqMax
        self.nFreqMax=int(freqMax*interval_length)
            
            #Fourrier
        if self.nFreqMax > self.interval_length/2:
            self.nFreqMax = self.interval_length/2
                    
            #Pile contenant les dernières fft
        self.stackLen=100
        self.lastResults={}
        self.posLastResult=0
        
        #window option
        self.setWindowTitle('spectre')
        self.resize(500, 300)
        self.move(3580, 300)

            #Modes d'affichage
        self.colorMode=colorMode
        self.octavMode=octavMode
        self.octavRan=octavRan
        self.logMode=logMode

    def initPlots(self):

        self.barGraphs={}            
        for i in self.channels:
            #Calcul des fft
            spectrum=np.array(abs(fft(self.data[i]))[1:self.nFreqMax])
            
            #Affichages par octaves
            if self.octavMode:
                x0,x1=self.freqToOctave_freq()
                spectrum=self.freqToOctave_pow(spectrum)
            else:
                #Transformation de l'axe des abscisses pour le mode logarithme
                if self.logMode :
                    x0=[np.log(j/self.interval_length_sec) for j in range(1,self.nFreqMax)]
                    x1=[np.log((j+1)/self.interval_length_sec) for j in range(1,self.nFreqMax)]
                else:
                    x0=[j/self.interval_length_sec for j in range(1,self.nFreqMax)]
                    x1=[(j+1)/self.interval_length_sec for j in range(1,self.nFreqMax)]
                

            #Initialisation de la pile des fft passees
            self.lastResults[i]=np.zeros(self.stackLen*(len(spectrum))).reshape(self.stackLen,len(spectrum))
            self.lastResults[i][0]=spectrum
            self.posLastResult=1
                
            if self.colorMode:
                #Couleurs en fonction des valeurs de puissances
                #initialisation du gradient
                self.colMap=pg.ColorMap(pos=np.array([1,0.7]),
                                        color=np.array([[255,0,0],[0,0,255]]),
                                        mode=pg.ColorMap.HSV_POS,
                                        )
                #Application du gradient sur les valeurs
                brushes=self.scaledBrushes(spectrum,i)
            else:
                brushes=None

                #Affichage
            p=self.addPlot(None)

            self.barGraphs[i]=bg.BarGraphItem(x0=x0,
                                              x1=x1,
                                              height=spectrum,
                                              brushes=brushes,
                                              )
            
            p.addItem(self.barGraphs[i])
            #Le prochain dessin est à la ligne d'après
            self.nextRow()
         
    #Construit une liste de couleurs compatibles avec le BarGraphItem, à partir des valeurs du spectre
    def scaledBrushes(self,spectrum,chan):
        #étalonnage sur du gradient sur les valeurs des spectres précédents
        self.sMax=np.amax(self.lastResults[chan])                
        self.colMap.pos[0]=self.sMax
        
        #choix des couleurs en fonction des puissances
        return self.colMap.map(spectrum)

    #Calcul des intervals de fréquence correspondant aux octaves.
    def freqToOctave_freq(self):
        x0_oct=[]
        x1_oct=[]
             #frequences en Hz !
        f0=1/self.interval_length_sec
        f1=f0*self.octavRan

        while f1 < self.freqMax :
            #Les intervals sont de taille constante lorsqu'on affiche le logarithme des valeurs en fréquence
            x0_oct.append(np.log(f0))
            x1_oct.append(np.log(f1))
            #On passe d'une octave à l'autre en multipliant la fréquence par une constante
            f0=self.octavRan*f0
            f1=self.octavRan*f0

        #Dernière octave, incomplète.
        x0_oct.append(np.log(f0))
        x1_oct.append(np.log(self.freqMax))
                 
        return x0_oct,x1_oct

    #Calcul des puissances des octaves
    def freqToOctave_pow(self,spectrum):
        bandes=[]

        #fréquences en Hz
        f0=1/self.interval_length_sec
        f1=f0*self.octavRan
        while f1 < self.freqMax:
            #conversion des fréquence en Hz en fréquence indices dans le résultat de la fft
            nf0=f0*self.interval_length_sec
            nf1=f1*self.interval_length_sec
                 
            #Cas où l'octave est comprise dans une unique fréquence
            if int(nf1)-int(nf0)==0:
                bandes.append(spectrum[int(nf0)])
            #Cas où l'octave chevauche plusieurs fréquences :
            else :
                #somme des puissances des fréquences entièrement comprises dans l'octave
                #plus de celles des extrémités, pondérée par largeur de celles-ci comprises
                #dans la bandes
                som = (int(nf0)+1-nf0)*spectrum[int(nf0)] + np.sum(spectrum[int(nf0)+1:int(nf1)]) + (nf1-int(nf1))*spectrum[int(nf1)] 
                mean=som/(f1-f0)
                bandes.append(mean)
            #On passe d'une octave à l'autre en multipliant la fréquence par une constante
            f0=self.octavRan*f0
            f1=self.octavRan*f0

        #Dernière octave, incomplete
        nf0=f0*self.interval_length_sec
        if self.nFreqMax-int(nf0)==0:
            bandes.append(spectrum[int(nf0)])
        else :
            som=(int(nf0)+1-nf0)*spectrum[int(nf0)] + np.sum(spectrum[int(nf0)+1:self.nFreqMax])
            mean=som/(self.freqMax-f0)
            bandes.append(mean)

        return bandes

    def updatePlots(self):

        for i in self.channels:
            #calcul des fft
            spectrum=np.array(abs(fft(self.data[i]))[1:self.nFreqMax])
                
            if self.octavMode:
                spectrum=self.freqToOctave_pow(spectrum)

            #enregistrement dans la pile de sauvegardes
            self.lastResults[i][self.posLastResult]=spectrum
                
            if self.colorMode:
                #étalonnage du gradient de couleurs sur les valeurs du spectre
                brushes=self.scaledBrushes(spectrum,i)
            else:
                brushes=None

                #mise à jour des graphes           
            self.barGraphs[i].updateHeights(spectrum,brushes)

        #Avancée dans la pile des résultats précédents.
        self.posLastResult=(self.posLastResult+1)%self.stackLen

    def adaptRange(self):
        for i in self.channels:
            maxS=np.max(self.lastResults[i])
            self.barGraphs[i].parentWidget().setRange(yRange=(0,maxS*1.1))    
    
    def keyPressEvent(self,e):
        if e.key()==pg.QtCore.Qt.Key_Escape:
            self.showNormal()
        elif e.key()==pg.QtCore.Qt.Key_Space:
            self.adaptRange()

