# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyqtgraphWorker as pw
from scipy import stats 


class KurtosisGraphicsSci(pw.PyQtGraphicsWorker):
    '''
    Représentation du kurtosis en temps réel. La valeur de kurtosis calculée est associée à 
    une visualisation de la distribution des valeurs (nécessaire à l'interprétation du
    kurtosis). Cette distribution est positionnée sur une échelle de distributions donnant 
    des exemples de kurtosis. Version moins jolie que l'autre mais un peu plus lisible.
    Les paramètres sont:
    Le flux de position des données à interpréter
    La taille de la fenêtre, en s, sur laquelle le kurtosis et la distribution est calculée
    (/!\Des comportements étranges peuvent apparaître dans le cas où cette taille proche
    de la taille du buffer dans lequel le flux est écrit.)
    Les canaux à traiter.
    Tout autre paramètre traiter par les GraphicsWidget de pyqtgraph devrait fonctionner
    '''

    def __init__(self,stream,interval_length,channels=None,title=None,**kwargs):
        super(KurtosisGraphicsSci,self).__init__(stream,interval_length,channels,title,**kwargs)
       
        self.labels={}
      

    def initPlots(self):
        #Calcul des courbes de référence pour le kurtosis
        xmin=-2.5
        xmax=3
      
        #Laplace, K=3
        laplace=np.array([0.5*np.exp(-np.abs(x)) for x in np.linspace(xmin,xmax,self.interval_length)])+3
        #Sécante hyperbolique,K=2
        sechyp=np.array([0.5/np.cosh(np.pi*x) for x in np.linspace(xmin,xmax,self.interval_length)])+2
        #Normale, K=0
        normal=np.array([1/(2*np.pi)**0.5 * np.exp(-0.5*x**2) for x in np.linspace(xmin,xmax,self.interval_length)])
        #Demi-cercle, K=-1
        R=min(np.abs(xmax),np.abs(xmin))
        demicercle=np.array([1/(np.pi*R**2) * np.sqrt(R**2-x**2) if x < R and x > -R else 0 for x in np.linspace(xmin,xmax,self.interval_length)]) - 1
        
        
        for i in self.channels:
            fen = self.data[i]
            p = self.addPlot(None)

            #Affichage des courbes de références pour le kurtosis
            p.plot(laplace,pen='9999')
            p.plot(sechyp,pen='9999')
            p.plot(normal,pen='9999')
            p.plot(demicercle,pen='9999')
            p.addItem(pg.InfiniteLine(-3,0,pen='999'))

            p.enableAutoRange('xy',False)

            #Calcul du kurtosis des valeurs du signal
            kurtosis=stats.kurtosis(fen)
            #Affichage de la courbe (ac offset)
            hist=self.distrib(fen)
            self.c[i]=p.plot(np.arange(len(hist))*len(fen)/len(hist),hist+kurtosis,
                             pen=pg.mkPen(color='F00',width=4),
                             #stepmode=True,
                             )
            

            #Affichage de l'étiquette indiquant la valeur du kurtosis
            self.labels[i]=pg.TextItem(html='<span style="color: #F00; font-size:30pt;>%0.2f</span>'%kurtosis,
                                       border='r',
                                       )
            p.addItem(self.labels[i])
            self.labels[i].setPos(0,-2)

            #Effacer les axes
            p.showAxis('bottom',False)
            if i>0:
                p.showAxis('left',False)

            self.nextCol()

    def updatePlots(self):
        for i in self.channels:
            fen = self.data[i]
            #Calcul du kurtosis
            kurtosis=stats.kurtosis(fen)            
            #Mise à jour de la courbe densité
            hist=self.distrib(fen)
            self.c[i].setData(np.arange(len(hist))*len(fen)/len(hist),hist+kurtosis)
            #Mise à jour de l'étiquette
            self.labels[i].setText('%0.2f'%kurtosis,color='F00')
            
    def distrib(self,signal):
        hist,bin_edges=np.histogram(signal)
        return hist/float(len(signal))
