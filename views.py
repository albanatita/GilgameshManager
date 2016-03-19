# -*- coding: utf-8 -*-
"""
Created on Mon Mar 07 15:55:05 2016

@author: admin
"""

import sys
from PyQt4.uic import loadUiType
from PyQt4 import QtCore
#from PyQt5.QtGui import QRegExpValidator
from PyQt4.QtGui import QApplication, QDialog,QStandardItem,QStandardItemModel
#from PyQt5.QtNetwork import QAbstractSocket, QTcpSocket
sys.path.append("C:\ISHTAR")
import gilgamesh.gilgamesh as gil
import gilgamesh.core.wrapper as wrapper
import gilgamesh.components.component as cpt
import pandas as pd
Qt = QtCore.Qt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
#from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
    
Ui_langmuir,QDialog = loadUiType('langmuirDialog.ui')
Ui_plot,QDialog=loadUiType('plotView.ui')

class LangmuirView(QDialog, Ui_langmuir):
    def __init__(self,shot):
        super(LangmuirView, self).__init__()
        self.setupUi(self)
        self.shot=shot
        self.shotEdit.setText(str(shot))
        self.plotU=pg.PlotWidget()
        self.plotI=pg.PlotWidget()   
        self.plotIV=pg.PlotWidget()   
        self.verticalLayout.addWidget(self.plotU)
        self.verticalLayout.addWidget(self.plotI)
        self.horizontalLayout.addWidget(self.plotIV)
        component=cpt.loadFromShot(self.shot)
        liste=component.findElement([],cpt.LangmuirProbe)
        self.listprobes=dict()
        for y in liste:
            self.langlistWidget.addItem(y.name)
            self.listprobes[y.name]=y
        self.displayButton.clicked.connect(self.displayData)
        self.calculateButton.clicked.connect(self.calculate)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        #langmuir=component.
        
    def displayData(self):      
        self.langmuir=self.listprobes[self.langlistWidget.selectedItems()[0].text()]
        
        char=self.langmuir.getData()
        self.charEdit.clear()
        text='Type : '+char['Type']+'\n'+'Surface : '+str(char['Surface'])+'\n'
        self.charEdit.setText(text)
        self.rampEdit.setText('10')
        self.sweepEdit.setText('1000')
        self.directionBox.addItems(['up','down'])
        self.directionBox.setCurrentIndex(1)
        self.backgndEdit.setText('False')
        self.processEdit.setText('smooth')
        UI=self.langmuir.getUI(self.shot)
        self.plotU.plot(UI.index.values,UI[char['Voltage']].values)
        self.plotI.plot(UI.index.values,UI[char['Current']].values)
        self.plotI.getPlotItem().setXLink(self.plotU.getPlotItem())
        self.marker=pg.InfiniteLine(pos=2.0,movable=True)
        self.plotI.addItem(self.marker)
        
    def calculate(self):
        param={'ramp':int(self.rampEdit.text()),'typ':self.directionBox.currentText(),'sweep':float(self.sweepEdit.text()),'backgnd':bool(self.backgndEdit.text()),'process':self.processEdit.text()}
        
        time=self.marker.getPos()[0]
        
        values=self.langmuir.calculateSingle(self.shot,time,param=param,show=True,showData=[self.plotIV])
        self.resultEdit.clear()
        text='Vfloat : '+str(values[1])+'\n Density : '+str(values[2])+'\n Temperature : '+str(values[3])+'\n Vplasma : '+str(values[4])
        self.resultEdit.setText(text)
        
class PlotView(QDialog, Ui_plot):
    def __init__(self,shots):
        super(PlotView, self).__init__()
        self.setupUi(self)
        self.shots=shots
#        self.verticalLayout.addWidget(self.plotU)
        liste=gil.listSignals()
        for x in liste['Name'].values:
            self.signalWidget.addItem(x)
        self.plotButton.clicked.connect(self.plot)
        
    def plot(self):
        l1=self.signalWidget.selectedItems()
        n=len(l1)
        table=[]
        listsignal=[]
        for x in l1:
            aa=pg.plotWidget()
            table.append(aa)
            sig=x.text()
            listsignal.append(sig)
            self.verticalLayout.addWidget(aa)
            result=gil.getSignal(self.shots,[sig])
            aa.plot()
        
        