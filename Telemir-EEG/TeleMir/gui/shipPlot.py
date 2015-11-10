# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui, QtOpenGL,Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy
from objloader import *
from .pyqtgraphWorker import GraphicsWorker
import time

#TO DO: 
# Mettre en vrai plein écran
# Mettre les fichiers dans un truc à part

class glTelemirCube:
    def __init__(self,x,y,z,color=[100,100,0]):
        self.x=x
        self.y=y
        self.z=z
        self.size=5
        self.speed=13
        self.color=color

    def oneStepNearer(self):
        self.y=self.y-self.speed
        if self.y<-190:
            self.y=numpy.random.randint(0,100)
            r=numpy.random.randint(35,55)
            theta=numpy.random.rand(1)*2*numpy.pi-numpy.pi
            self.x=r*numpy.cos(theta)
            self.z=r*numpy.sin(theta)
           

    def dessiner_cube(self):

        glPushMatrix()
        glTranslated(self.x,self.y,self.z)
        #print self.dist
        glBegin(GL_QUADS)
        
        #face rouge
        glColor3ub(75+self.color[0],75+self.color[1],75+self.color[2])
        glVertex3d(self.size,self.size,self.size)
        glVertex3d(self.size,-self.size,self.size)
        glVertex3d(self.size,-self.size,-self.size)
        glVertex3d(self.size,self.size,-self.size)

        #face
        glColor3ub(10+self.color[0],10+self.color[1],10+self.color[2])
        glVertex3d(-self.size,self.size,self.size)
        glVertex3d(-self.size,self.size,-self.size)
        glVertex3d(-self.size,-self.size,-self.size)
        glVertex3d(-self.size,-self.size,self.size)

        #face verte
        glColor3ub(25+self.color[0],25+self.color[1],25+self.color[2])
        glVertex3d(self.size,self.size,self.size)
        glVertex3d(self.size,self.size,-self.size)
        glVertex3d(-self.size,self.size,-self.size)
        glVertex3d(-self.size,self.size,self.size)

        #face bleue
        glColor3ub(45+self.color[0],45+self.color[1],45+self.color[2])
        glVertex3d(self.size,-self.size,self.size)
        glVertex3d(-self.size,-self.size,self.size)
        glVertex3d(-self.size,-self.size,-self.size)
        glVertex3d(self.size,-self.size,-self.size)

        #face blanche
        glColor3ub(60+self.color[0],60+self.color[1],60+self.color[2])
        glVertex3d(self.size,self.size,self.size)
        glVertex3d(-self.size,self.size,self.size)
        glVertex3d(-self.size,-self.size,self.size)
        glVertex3d(self.size,-self.size,self.size)

        #face
        glColor3ub(75+self.color[0],75+self.color[1],75+self.color[2])
        glVertex3d(self.size,self.size,-self.size)
        glVertex3d(self.size,-self.size,-self.size)
        glVertex3d(-self.size,-self.size,-self.size)
        glVertex3d(-self.size,self.size,-self.size)

        
        glEnd()

        glPopMatrix()

        glFlush()

class glAsteroid:
    pass

class glSpaceShip:
    def __init__(self,period):
        self.x=0
        self.y=0
        self.vitx=0
        self.vity=0
        self.obj = None #instanciation
        self.period=period
        #Ressort
        self.k=0.1

    def updatePos(self):
        #filtre des valeurs les plus basses, pour éviter un peu la dérive
        if abs(self.vitx) == 5 : self.vitx=0
        if abs(self.vity) == 5 : self.vity=0

        #Euler
        self.x+=self.vitx*self.period/1000.-self.k*self.x
        self.y+=self.vity*self.period/1000.-self.k*self.y

    def draw(self):

        glPushMatrix()
        
        glTranslated(0,-50,0)
        glScaled(0.6,0.6,0.6)
#rotation en fonction des valeurs enregistrées
        glRotated(-self.x,1,0,0)
        glRotated(self.y,0,0,1)   

        glCallList(self.obj.gl_list)

        glPopMatrix()
        


class spaceShipLauncher(QtOpenGL.QGLWidget,GraphicsWorker):
    '''
    Cette classe affiche un vaisseau spatiale dont les mouvements
    sont liées à des vitesses amenée par un flux (deux canaux).
    Il y a aussi des carrés qui se déplacent vers l'écran.
    C'est pas vraiment fini.
    '''    

    def __init__(self,stream,cubeColor='summer',parent=None):
        QtOpenGL.QGLWidget.__init__(self,parent)
        GraphicsWorker.__init__(self,stream,0.2)# on ne se soucis pas de la taille de la fenêtre, puisqu'on utilisera toujours la dernière valeur. Mais en fait je m'en sert pour l'étalonnage des gyro.
        
        self.spaceShip=glSpaceShip(self.period)

        #Offset des gyro du casques, mesurés dans initPlots
        self.xOffset=0
        self.yOffset=0
        self.nbCubes=9
        if cubeColor=='jet':
            self.cubeColor=[(0,numpy.random.randint(00,125),numpy.random.randint(125,175)) for i in range(self.nbCubes)]
        elif cubeColor=='hot':
            self.cubeColor=[(numpy.random.randint(100,175),0,0) for i in range(self.nbCubes)]
        elif cubeColor=='summer':
            self.cubeColor=[(numpy.random.randint(0,100),numpy.random.randint(100,175),0) for i in range(self.nbCubes)]
        self.cubes=[glTelemirCube(numpy.random.randint(-30,30),
                                  numpy.random.randint(-50,50),
                                  numpy.random.randint(-30,30),              
                                  self.cubeColor[i],
                                   #numpy.random.randint(0,0),
                                   #numpy.random.randint(0,0)],
                                  ) for i in range(self.nbCubes)]

        
        #window option
        self.setWindowTitle('Vaisseau')
        #~ self.resize(1200, 1768)
        #~ self.move(8057,0)
        self.resize(800, 600)
        self.move(6720, 0)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        
        
    def initPlots(self):
     #   self.setFixedSize(1600,1600)
        self.show()
        glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)  

        self.spaceShip.obj = OBJ('spaceFighter.obj', swapyz=True)

        glViewport(0,0,800,600)
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity( )
        gluPerspective(75,800./600,1,250)
        #gluPerspective(70,640./480,1,250)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)

        #Offset measurements of the gyroscopes
        time.sleep(self.time_window)
        self.updateGW() #inherited from parent class
        mx=numpy.mean(self.data[1,:])
        my=numpy.mean(self.data[0,:])        
        self.xOffset=numpy.round(mx)
        self.yOffset=numpy.round(my)
        print self.xOffset,' ',self.yOffset

    def updatePlots(self):

        self.spaceShip.vitx=(self.data[1,-1]-self.xOffset)*5
        self.spaceShip.vity=(self.data[0,-1]-self.yOffset)*5

        self.spaceShip.updatePos()
        #Les cubes avancent
        #self.dists=[(dist-58)%200 - 200 + 50 for dist in self.dists]
        for cube in self.cubes:
            cube.oneStepNearer()

        self.updateGL()


    def paintGL(self):
                
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        #position de la caméra
        gluLookAt(0,-150,0,0,0,0,0,0,1)

#        self.dessiner_navette()
        self.spaceShip.draw()

        for cube in self.cubes:
            cube.dessiner_cube()

        glFlush()

    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Left:
            self.x+=5
        if event.key()==QtCore.Qt.Key_Right:
            self.x-=5

        if event.key()==QtCore.Qt.Key_Q:
            self.y+=5
        if event.key()==QtCore.Qt.Key_D:
            self.y-=5
        
        self.updateGL()

    def mousePressEvent(self, event): #simpleclic
        pass
        #print event.pos()
