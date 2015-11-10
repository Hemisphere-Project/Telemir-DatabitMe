# -*- coding: utf-8 -*-
"""

Extracteur de parametres

Prends un tableau de donnees et extrait des parametres

first version by Lx37

"""

import numpy as np
import scipy as sc
import scipy.stats as st
import time
import pyeeg
#from pyentropy import DiscreteSystem
#from sklearn.decomposition import FastICA
import pylab as pl
import matplotlib.mlab as mlab

class GetFeatures():
    def __init__(self,stream_in, nb_features = 9, name = 'test'):
        print "ok"
        self.name = name
        self.nb_features = nb_features
        self.features = np.zeros((self.nb_features,1),dtype=np.float)
        self.channel_names = [ 'F3', 'F4', 'P7', 'FC6', 'F7', 'F8','T7','P8','FC5','AF4','T8','O2','O1','AF3']
        self.nb_chan = 14
        self.channels = np.arange(self.nb_chan)
        self.interval_length_sec = 1
        print "ok"
        # Get shared mem: to adapt analysis window size to feature caracteristics
        self.stream_in = stream_in
        self.np_arr_in = self.stream_in['shared_array'].to_numpy_array()
        self.half_size_in = self.np_arr_in.shape[1]/2
        self.sr_in = self.stream_in['sampling_rate']
        self.packet_size_in = self.stream_in['packet_size']
        self.nb_pts = self.interval_length_sec * self.stream_in['sampling_rate']
        # self.data is defined in get feature

        #for fft
        self.bands = np.array([[1,4],[4,8],[8,13],[13,35],[30,45],[12,16]])
        self.bands_name = ('delta', 'theta', 'alpha','beta','gamma', 'mu')
        self.nb_bands = 6
        #frequence max en entier
        self.freqMax = np.amax(self.bands)
        self.nFreqMax = int(self.freqMax*self.interval_length_sec)
        self.pows = np.zeros((self.nb_chan,self.nb_bands), dtype = np.float)

        # différentes tailles de fenetre en fonction des bandes
        ## TODO : automatiser ce calcul
        self.band_time_size = [5,1.5,1,1,1,1]#0.5,0.25,0.75]  ## Calculé par rapport aux frequences moy de chaque bande pour avoir 10 cycles et que ça tombe juste / Fe
        self.pows2 = np.zeros((self.nb_chan,self.nb_bands), dtype = np.float)

        #Moyennes glissantes et cumulées
        self.Xsmooth =30
        self.contrib_alpha_cumul = np.zeros((self.Xsmooth))
        self.contrib_beta_cumul =  np.zeros((self.Xsmooth))
        self.contrib_teta_cumul =  np.zeros((self.Xsmooth))
        self.contrib_mu_cumul =  np.zeros((self.Xsmooth))
        self.contrib_FTheta_cumul =  np.zeros((self.Xsmooth))
        self.R_engage_cumul =  np.zeros((self.Xsmooth))
        self.id_cumul = 0
        # self.id_new_cumul = 0

        # self.alpha_cumul_th = 200000#1000000
        self.contrib_alpha_cumul_th = 20

        mean = 0
        variance = 50
        sigma = np.sqrt(variance)
        x = np.linspace(-25,25,50)
        self.template_blink = mlab.normpdf(x,mean,sigma)*2500

        # blink_proj = np.load('/home/mi/Projets/TeleMir/TeleMir/analyses/ICA_proj.npy')
        blink_proj = np.load('E:\Documents\GitHub\TeleMir\TeleMir\\analyses\ICA_proj.npy')
        self.blink_invProj = np.linalg.inv(blink_proj)
        self.n_blink_comp = 2
        self.last_blink = 0
        self.blink_threshold = 0.05#5

    def extract_TCL(self, head):

        self.data = self.np_arr_in[:, head+self.half_size_in-self.nb_pts : head +self.half_size_in]
        self.getFeat(self.data)
        blink_feat = self.is_blink(self.data)
        bandsAv = np.average(self.pows, axis = 0)
        total_power = np.sum(bandsAv[0:5], axis=0)
        # crisp_feat = self.get_crispation(total_power)

        #pDeltaP7P8 = (self.pows[3,0] + self.pows[8,0])/2
        #~ pThetaAF34F34 = (self.pows2[9,1] + self.pows2[13,1] + self.pows2[0,1] + self.pows2[1,1])/2
        # pAlphaO12 = (self.pows[11,2] + self.pows[12,2])/2
        # total_power_O1O2 =  np.sum(self.pows[11,:], axis=0) + np.sum(self.pows[12,:], axis=0)
        #pBetaF34 = (self.pows2[0,3] + self.pows2[1,3])/2
        #pGammaFC56 = (self.pows[4,4] + self.pows[9,4])/2
        #pMuT78 = (self.pows[7,5] + self.pows[11,5])/2
        #contribution alpha O1O2
        # contrib_alpha_O1O2 = pAlphaO12/total_power_O1O2
        # self.contrib_alpha_cumul_O1O2.append(contrib_alpha_O1O2)
        # contrib_alpha_cumul_O1O2 = np.sum(self.contrib_alpha_cumul_O1O2)

        contrib_FTheta = (self.pows[0,1] + self.pows[1,1] + self.pows[3,1] + self.pows[4,1] + self.pows[5,1] + self.pows[8,1] + self.pows[9,1] + self.pows[13,1])/8
        contrib_FTheta = contrib_FTheta/total_power

        #contribution alpha, beta teta mu FrontalTheta
        contrib_alpha = bandsAv[2]/total_power
        if not(np.isnan(contrib_alpha)):
            self.contrib_alpha_cumul[self.id_cumul] = contrib_alpha
        contrib_beta = bandsAv[3]/total_power
        if not(np.isnan(contrib_beta)):
            self.contrib_beta_cumul[self.id_cumul] = contrib_beta
        contrib_teta = bandsAv[1]/total_power
        if not(np.isnan(contrib_teta)):
            self.contrib_teta_cumul[self.id_cumul] = contrib_teta
        contrib_mu = bandsAv[5]/total_power
        if not(np.isnan(contrib_mu)):
            self.contrib_mu_cumul[self.id_cumul] = contrib_mu
        # frontal theta
        contrib_FTheta = (self.pows[0,1] + self.pows[1,1] + self.pows[3,1] + self.pows[4,1] + self.pows[5,1] + self.pows[8,1] + self.pows[9,1] + self.pows[13,1])/8
        contrib_FTheta = contrib_FTheta/total_power
        if not(np.isnan(contrib_FTheta)):
            self.contrib_FTheta_cumul[self.id_cumul] = contrib_FTheta
        #Ratios
        R_engage = bandsAv[3]/(bandsAv[1]+bandsAv[2]) # beta / (theta * alpha)
        if not(np.isnan(R_engage)):
            self.R_engage_cumul[self.id_cumul] = R_engage

        self.id_cumul = (self.id_cumul + 1)%self.Xsmooth

        ## Smooth
        contrib_alpha_smooth = np.average(self.contrib_alpha_cumul)
        contrib_alpha_smooth = np.average(self.contrib_alpha_cumul)
        contrib_beta_smooth = np.average(self.contrib_beta_cumul)
        contrib_teta_smooth = np.average(self.contrib_teta_cumul)
        contrib_mu_smooth = np.average(self.contrib_mu_cumul)
        contrib_FTheta_smooth =  np.average(self.contrib_FTheta_cumul)
        R_engage_smooth =  np.average(self.R_engage_cumul)

        ## Normalize
        contrib_alpha_smooth_norm = self.normalize(contrib_alpha_smooth, 0, 100, 0.1, 0.3)
        contrib_beta_smooth_norm = self.normalize(contrib_beta_smooth, 0, 100, 0.06, 0.3)
        contrib_teta_smooth_norm = self.normalize(contrib_teta_smooth, 0, 100, 0.1, 0.4)
        contrib_mu_smooth_norm = self.normalize(contrib_mu_smooth, 0, 100, 0.1, 0.4)
        contrib_FTheta_smooth_norm = self.normalize(contrib_FTheta_smooth, 0, 100, 0.1, 0.4)
        R_engage_smooth_norm = self.normalize(R_engage_smooth, 0, 100, 0.1, 0.4)

        crisp_feat = self.normalize(total_power, 0, 5, 2000, 6000)
        crisp_feat = crisp_feat * 20
        crisp_feat_continue = self.normalize(total_power, 0, 100, 2000, 6000)

        # if contrib_alpha_smooth_norm>6:
        #     blink_feat =0

        corel_dg = sc.stats.pearsonr(self.data[6,:], self.data[10,:])[0]  #entre T7 et T8
        if not(np.isnan(corel_dg)):
             corel_dg = np.int((corel_dg + 1) * 50)

        features = np.array([contrib_alpha_smooth_norm, blink_feat, crisp_feat, contrib_beta_smooth_norm, contrib_teta_smooth_norm, contrib_mu_smooth_norm, contrib_FTheta_smooth_norm, R_engage_smooth_norm, crisp_feat_continue])
        return features

    def normalize(self, value, min_norm, max_norm, min, max):
        if value < min:
            norm_value = min_norm
        elif value > max:
            norm_value = max_norm
        else:
            norm_value = ((value - min) * (max_norm - min_norm) / (max - min)) + min_norm
        return np.int(norm_value)

    def is_blink(self, data):
        # sur combien de points  ? ici 64 ??
        data = np.transpose(data)
        data_rect = data - np.mean(data, axis = 0)
        data_rect = np.transpose(data_rect)
        blink_comp = np.dot( self.blink_invProj[self.n_blink_comp], data_rect[:,data_rect.shape[1]-15:data_rect.shape[1]])
        if np.mean(blink_comp) > self.blink_threshold and self.lastBlink < self.blink_threshold:
            isBlink = 10
        else:
            isBlink = 0
        self.lastBlink = np.mean(blink_comp)
        return isBlink

    def getFeat(self, data):
        for i in self.channels:
            j=0
            #calcul des fft
            spectrum=np.array(abs(sc.fft(data[i]))[1:self.nFreqMax+1])
            #calcul des puissances par bandes
            self.pows[i]=self.bands_power(spectrum)

    #Calcul des puissance des bandes
    def bands_power(self,spectrum):
        pows=[]
        for f0,f1 in self.bands:
            #Conversion des Hz vers l'indice exacte de la frequence (sortie de la fft)*
            #cf cas ou on tombe au milieu d'un bin
            nf0 = f0*self.interval_length_sec
            nf1 = f1*self.interval_length_sec
            #Cas où l'octave est comprise dans une unique fréquence
            if int(nf1)-int(nf0)==0:
                pows.append(spectrum[int(nf0)-1])
            #Cas où l'octave chevauche plusieurs fréquences :
            else :
                #somme des puissances des fréquences entièrement comprises dans l'octave
                #plus de celles des extrémités, pondérée par largeur de celles-ci comprises
                #dans la bandes
                som=(int(nf0)+1-nf0)*spectrum[int(nf0)-1] + np.sum(spectrum[int(nf0):int(nf1)-1]) + (nf1-int(nf1))*spectrum[int(nf1)-1]
                mean=som/(f1-f0)
                pows.append(mean)
        return pows
