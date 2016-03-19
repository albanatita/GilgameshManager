# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 12:53:44 2016

@author: admin
"""

import os
import sys
from PyQt4.uic import loadUiType
from PyQt4 import QtCore
#from PyQt5.QtGui import QRegExpValidator
from PyQt4.QtGui import QApplication, QMainWindow,QStandardItem,QStandardItemModel
#from PyQt5.QtNetwork import QAbstractSocket, QTcpSocket
sys.path.append("C:\ISHTAR")
import gilgamesh.gilgamesh as gil
import gilgamesh.core.wrapper as wrapper
import pandas as pd
Qt = QtCore.Qt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import gilgamesh.components.component as cpt
import views
import file_watcher


Ui_gilgamesh, QMainWindow = loadUiType('mainWindow.ui')

class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = np.array(data.values)
        self._cols = data.columns
        self.r, self.c = np.shape(self._data)

    def rowCount(self, parent=None):
        return self.r

    def columnCount(self, parent=None):
        return self.c

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return self._data[index.row(),index.column()]
        return None

    def datarow(self,row):
        return self._data[row,:]

    def headerData(self, p_int, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._cols[p_int]
            elif orientation == QtCore.Qt.Vertical:
                return p_int
        return None

def cvrttime (x):
    try:
        y=x.strftime('%d-%m-%Y')
    except:
        y='NaT'
    return y

def populateTree(componentList):
    itemList=[]
    for component in componentList:
        item=QStandardItem(component.name)
        if component.children==[]:
            itemList.append(item)
        else:
            item.appendRow(populateTree(component.children))
            itemList.append(item)
    return itemList
    

class Environment():   
    def __init__(self):
        self.path=r"c:"+os.sep+"ISHTAR"+os.sep+"DATA"
        
class gilgameshManager(QMainWindow, Ui_gilgamesh):
    def __init__(self):
        super(gilgameshManager, self).__init__()
        self.setupUi(self)
        self.env=Environment()
        self.actionQuit.triggered.connect(self.exit)
        self.loadDB()
        self.ShotTableView.clicked.connect(self.selectShot)
        self.header = self.ShotTableView.horizontalHeader()
        self.header.sectionClicked.connect(self.headerClicked)
        self.fig=Figure()
        self.canvas = FigureCanvas(self.fig)        
        self.hLayout.addWidget(self.canvas)
        self.updateButton.clicked.connect(self.updateList)
        self.listeAction=['Langmuir probe analysis','Data plot']
        self.listActions.addItems(self.listeAction)
        self.actionButton.clicked.connect(self.executeAction)
        self.watcher=file_watcher.fileWatcher(self.env)
        self.watcher.start()
        self.connect(self.watcher,QtCore.SIGNAL("update(QString)"), self.msg )
        
        
    def exit(self):
        self.close()
    
    def msg(self,text)    :
        self.logWidget.append(text)
    
    def executeAction(self):
        select=self.listActions.currentText()
        if select=='Langmuir probe analysis':
             shotrow=(self.ShotTableView.selectedIndexes())[0].row()
             shot=self.ShotTableView.model().datarow(shotrow)[0]
             self.viewLangmuir=views.LangmuirView(shot)
             self.viewLangmuir.show()
        if select=='Data plot':
            shots=[]
            for x in self.ShotTableView.selectedIndexes():
                shots.append(self.ShotTableView.model().datarow(x.row())[0])
            self.viewPlot=views.PlotView(shots)
            self.viewPlot.show()
    
    def selectShot(self,clickedIndex):
        self.fig.clear()
        row=clickedIndex.row()
        model=clickedIndex.model()
        shot=model.datarow(row)[0]
        try:
            gil.overview(shot,self.fig)
        except Exception,e:
            print e
            pass
        self.canvas.draw()
        self.model = QStandardItemModel()
        self.treeView.setModel(self.model)
        component=cpt.loadFromShot(shot)
        self.model.appendRow(populateTree([component]))
        self.treeView.show()
        self.treeView.clicked.connect(self.treeClicked)
        self.contentWidget.clear()
        liste=wrapper.signalWrapper.signalPresent(shot)
        for x in liste:
            self.contentWidget.addItem(x)

    def treeClicked(self,clickedIndex):
        select=self.model(clickedIndex[0])
        
 
    def updateList(self):
        criterion=self.criterionEdit.text()
        if criterion=='':
            criterion=None
        self.loadDB(criterion=criterion)
   
    def loadDB(self,criterion=None)        :
        list=gil.listShots(criterion=criterion)
        list['Shot'] = list.index  
        list['Date']=list['Date'].apply(lambda x: cvrttime(x))
        self.pdata=list.reindex( columns=['Shot','Date','Program','MaxH_Pinj','AvgNgas_P','Gas','MaxBigCoil_I','MaxSmallCoil_I','MaxIC_Pinj','Maxdensity','Useful','MaxH_Ping'])  
        self.model=PandasModel(self.pdata) 
        self.ShotTableView.setModel(self.model)
        self.ShotTableView.update()
        
    def headerClicked(self, logicalIndex):
        self.order = self.header.sortIndicatorOrder()
        self.pdata.sort(self.pdata.columns[logicalIndex],
                        ascending=self.order,inplace=True)
        self.model = PandasModel(self.pdata)
        self.ShotTableView.setModel(self.model)
        self.ShotTableView.update()

       
app = QApplication(sys.argv)
window = gilgameshManager()
window.show()
sys.exit(app.exec_())