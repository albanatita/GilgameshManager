# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 12:53:44 2016

@author: admin
"""

import os
import sys
from PyQt4.uic import loadUiType,loadUi
from PyQt4 import QtCore
#from PyQt5.QtGui import QRegExpValidator
from PyQt4.QtGui import QApplication, QMainWindow,QStandardItem,QStandardItemModel,QDialog
#from PyQt5.QtNetwork import QAbstractSocket, QTcpSocket
sys.path.append("C:\ISHTAR")
import gilgamesh.gilgamesh as gil
import gilgamesh.core.wrapper as wrapper
import gilgamesh
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
from PyQt4 import QtGui
import gilgamesh.readGenerator as rg
import gilgamesh.core.hdf5Manager as h5

class genCreateDialog(QtGui.QDialog):
    def __init__(self,parent=None):
         super(genCreateDialog,self).__init__(parent)
         layout=QtGui.QVBoxLayout(self)
         label1=QtGui.QLabel('Generator file:')
         self.text1=QtGui.QLineEdit('')
         label2=QtGui.QLabel('First Shot:')
         self.text2=QtGui.QLineEdit('')
         label3=QtGui.QLabel('Last Shot:')
         self.text3=QtGui.QLineEdit('')
         readFile=QtGui.QPushButton("Open File")
         readFile.clicked.connect(self.openFile)
         layout.addWidget(label1)
         layout.addWidget(self.text1)
         layout.addWidget(readFile)
         layout.addWidget(label2)
         layout.addWidget(self.text2)
         layout.addWidget(label3)
         layout.addWidget(self.text3)         
         buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,QtCore.Qt.Horizontal, self)
         buttons.accepted.connect(self.accept)
         buttons.rejected.connect(self.reject)
         layout.addWidget(buttons)
    
    def openFile(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, 'Dialog Title', 'd:\\')
        if fileName:
            self.text1.setText(fileName)
    
    def getValues(self):
        name=self.text1.text()
        firstShot=int(self.text2.text())
        lastShot=int(self.text3.text())
        return name,firstShot,lastShot       
         
    @staticmethod     
    def getData(parent=None):
        dialog=genCreateDialog(parent)
        result=dialog.exec_()
        name,firstShot,lastShot=dialog.getValues()
        return (name,firstShot,lastShot,result==QtGui.QDialog.Accepted)

class gasCreateDialog(QtGui.QDialog):
    def __init__(self,parent=None):
         super(gasCreateDialog,self).__init__(parent)
         layout=QtGui.QVBoxLayout(self)
         self.listGas=QtGui.QComboBox()
         self.listGas.addItems(['Argon','Helium','Hydrogen'])
         label1=QtGui.QLabel('Type of Gas:')
         layout.addWidget(label1)
         layout.addWidget(self.listGas)
         buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,QtCore.Qt.Horizontal, self)
         buttons.accepted.connect(self.accept)
         buttons.rejected.connect(self.reject)
         layout.addWidget(buttons)
    
    def getValues(self):
        name=self.listGas.currentText()
        return name         
         
    @staticmethod     
    def getData(parent=None):
        dialog=gasCreateDialog(parent)
        result=dialog.exec_()
        name=dialog.getValues()
        return (name,result==QtGui.QDialog.Accepted)

class setPositionDialog(QtGui.QDialog):
    def __init__(self,parent=None):
         super(setPositionDialog,self).__init__(parent)
         layout=QtGui.QVBoxLayout(self)
         self.position=QtGui.QLineEdit()
         label1=QtGui.QLabel('Position of manipulator (in V):')
         layout.addWidget(label1)
         layout.addWidget(self.position)
         buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,QtCore.Qt.Horizontal, self)
         buttons.accepted.connect(self.accept)
         buttons.rejected.connect(self.reject)
         layout.addWidget(buttons)
    
    def getValues(self):
        position=int(self.position.text())
        return position
         
    @staticmethod     
    def getData(parent=None):
        dialog=setPositionDialog(parent)
        result=dialog.exec_()
        position=dialog.getValues()
        return (position,result==QtGui.QDialog.Accepted)

Ui_gilgamesh, QMainWindow = loadUiType('mainWindow.ui')
#UIdensDialog=loadUiType('densityDialog.ui')

class densDialog(QDialog):
     def __init__(self,shots,parent=None):   
        super(QDialog, self).__init__()
        self.ui=loadUi('densityDialog.ui', self)
        self.shots=shots
        self.ui.rampEdit.setText('10')
        self.ui.backgndEdit.setText('False')
        self.ui.directionBox.addItems(['up','down'])
        self.ui.directionBox.setCurrentIndex(1)
        self.ui.processEdit.setText('smooth')
        self.ui.sweepEdit.setText('1000')
        self.ui.timeStart.setText('0.')
        self.ui.timeStop.setText('8.')
        self.ui.timeStep.setText('0.1')
        self.ui.buttonBox.accepted.connect(self.startCalculating)
        self.ui.buttonBox.rejected.connect(self.close)
        liste=[]
        # display only probes common to all shots
        for x in self.shots:
            component=cpt.loadFromShot(x)
            listname=component.findElement(cpt.LangmuirProbe)
            liste.append([z.name for z in listname])
        result = set(liste[0])
        for s in liste[1:]:
            result.intersection_update(s)
        result=list(result)
        for z in result:
            self.ui.listWidget.addItem(z)
        
     def startCalculating(self):
         param={'ramp':int(self.ui.rampEdit.text()),'typ':self.ui.directionBox.currentText(),'sweep':float(self.ui.sweepEdit.text()),'backgnd':bool(self.ui.backgndEdit.text()),'process':self.ui.processEdit.text()}
         self.langmuirname=self.ui.listWidget.selectedItems()[0].text()
         for x in self.shots:
             component=cpt.loadFromShot(x)
             liste=component.findElement(cpt.LangmuirProbe)
             z=[value for value in liste if value.name==self.langmuirname][0]
             result=z.calculateTime(x,float(self.ui.timeStart.text()),float(self.ui.timeStop.text()),float(self.ui.timeStep.text()),param=param)
             print result
             h5.saveData(x,'dens',result['n'].values,subgroup=self.langmuirname+'/')
             h5.saveData(x,'Vfloat',result['Vfloat'].values,subgroup=self.langmuirname+'/')
             h5.saveData(x,'Vplasma',result['Vplasma'].values,subgroup=self.langmuirname+'/')
             h5.saveData(x,'temp',result['T'].values,subgroup=self.langmuirname+'/')
             h5.saveData(x,'Time',result['time'].values,subgroup=self.langmuirname+'/')


     def close(self):
        self.ui.close()
        #self.setupUi(self)

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
            for x in populateTree(component.children):
                item.appendRow(x)
            itemList.append(item)
    return itemList
    

class Environment():   
    def __init__(self):
        self.path=r"\\ISHTARPC2\Users\Public"
        
class gilgameshManager(QMainWindow, Ui_gilgamesh):
    def __init__(self):
        super(gilgameshManager, self).__init__()
        self.setupUi(self)
        self.env=Environment()
        self.actionQuit.triggered.connect(self.exit)
        self.actionSet_Gas.triggered.connect(self.setGas)
        self.actionReinitialize_Shot_database.triggered.connect(self.reinit)
        self.actionImport_Mapping_from_CSV.triggered.connect(self.importMapping)
        self.actionAdd_Generator_data.triggered.connect(self.addGenerator)
        self.actionSet_Parameters.triggered.connect(self.setParameters)
        self.actionSet_Manual_Position.triggered.connect(self.setPosition)
        #QtGui.QShortcut(QtGui.QKeySequence("Ctrl+P"), self, self.setParameters)
        self.actionExport_Mapping_from_CSV.triggered.connect(self.exportMapping)
        self.actionReload_Signal_Database.triggered.connect(self.reloadSignalDB)
        self.actionConvert_to_Real_Pos.triggered.connect(self.convertPos)
        self.actionCalculate_density.triggered.connect(self.calculateDensity)
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
        self.connect(self.watcher,QtCore.SIGNAL("update(QString)"), self.msg)
        self.connect(self.watcher,QtCore.SIGNAL("newshot"), self.addShot)
        self.connect(self.watcher,QtCore.SIGNAL("newcsv"), self.addTime)
        
        
    def exit(self):
        self.close()

    def calculateDensity(self):
        shots=[]
        for x in self.ShotTableView.selectedIndexes():
            shots.append(self.ShotTableView.model().datarow(x.row())[0])
        self.densityDialog=densDialog(shots)
        self.densityDialog.show()

    def convertPos(self):
        shots=[]
        for x in self.ShotTableView.selectedIndexes():
            shots.append(self.ShotTableView.model().datarow(x.row())[0])
        for x in shots:
            component=cpt.loadFromShot(x)
            manip=component.findElement([],cpt.Manipulator)[0]
            position=manip.convertPos(x)
            gil.sm.changeAttr(x,'AvgManip_pos',position)
        self.loadDB()

    def reloadSignalDB(self):
        gil.sm.wrapper.importSignalDB()            

    def setPosition(self):
        shotrow=(self.ShotTableView.selectedIndexes())[0].row()
        shot=self.ShotTableView.model().datarow(shotrow)[0]   
        position,ok=setPositionDialog.getData()
        gil.sm.changeAttr(shot,'AvgManip_posRaw',position)
        self.loadDB()

    def setParameters(self):
        shots=[]
        for x in self.ShotTableView.selectedIndexes():
            shots.append(self.ShotTableView.model().datarow(x.row())[0])
        for x in shots:
            print x
            try:
                signal=gil.sm.readSignal([x],['Ngas_P'])
                maximum=np.mean(signal['Ngas_P'])            
            except Exception as e:
                print e
                maximum=np.nan
            gil.sm.changeAttr(x,'AvgNgas_P',maximum)
            try:
                signal=gil.sm.readSignal([x],['H_Pinj'])
                maximum=max(signal['H_Pinj'])
            except Exception as e:
                print e
                maximum=np.nan
            gil.sm.changeAttr(x,'MaxH_Pinj',maximum) 
            try:
                signal=gil.sm.readSignal([x],['IC_Pinj'])
                maximum=max(signal['IC_Pinj'])
            except Exception as e:
                print e
                maximum=np.nan
            gil.sm.changeAttr(x,'MaxIC_Pinj',maximum)
            try:
                signal=gil.sm.readSignal([x],['BigCoil_I'])
                maximum=max(signal['BigCoil_I'])
            except Exception as e:
                print e
                maximum=np.nan
            gil.sm.changeAttr(x,'MaxBigCoil_I',maximum)            
            try:
                signal=gil.sm.readSignal([x],['SmallCoil_I'])
                maximum=max(signal['SmallCoil_I'])
            except Exception as e:
                print e
                maximum=np.nan
            gil.sm.changeAttr(x,'MaxSmallCoil_I',maximum)
        self.loadDB()

    def addGenerator(self):
        fileName,firstShot,lastShot,ok=genCreateDialog.getData()
        rg.convertGenerator(fileName,firstShot,lastShot,self.env,gil.sm)
        print "finished converting"
        self.loadDB()
        

    def addTime(self,shot,time):       
        gil.sm.changeAttr(shot,'Date',time)
        self.loadDB()

    def importMapping(self):
        gil.sm.wrapper.loadMappingfromCSV()

    def exportMapping(self):
        gil.sm.wrapper.saveMappingtoCSV()
    
    def reinit(self):
        gil.sm.initializeDB()
        self.loadDB()

    def setGas(self):
        name,ok=gasCreateDialog.getData()
        shots=[]
        for x in self.ShotTableView.selectedIndexes():
            shots.append(self.ShotTableView.model().datarow(x.row())[0])
        for x in shots:
            gil.sm.changeAttr(x,'Gas',name)
        self.loadDB()
    
    def addShot(self,shot):
        gil.sm.wrapper.addShotMapping(shot)
        gil.sm.addShot(shot)
        present=cpt.present()
        cpt.attachShot(present,[shot])
        self.loadDB()
        
    
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
        self.treeView.clicked.connect(self.treeClicked)
        self.contentWidget.clear()
        liste=wrapper.signalWrapper.signalPresent(shot)
        for x in liste:
            self.contentWidget.addItem(x)
        liste2=wrapper.signalWrapper.attrPresent(shot)
        for x in liste2:
            self.contentWidget.addItem(x)


    def treeClicked(self,clickedIndex):
        select=self.model(clickedIndex[0])
        
 
    def updateList(self):
        criterion=self.criterionEdit.text()
        if criterion=='':
            criterion=None
        self.loadDB(criterion=criterion)
   
    def loadDB(self,criterion=None)        :
        try:
            list=gil.listShots(criterion=criterion)
            list['Shot'] = list.index  
            list['Date']=list['Date'].apply(lambda x: cvrttime(x))
            self.pdata=list.reindex( columns=['Shot','Date','Program','MaxH_Pinj','AvgNgas_P','Gas','MaxBigCoil_I','MaxSmallCoil_I','MaxIC_Pinj','Maxdensity','AvgManip_pos','AvgManip_posRaw','Useful'])  
            self.model=PandasModel(self.pdata) 
            self.ShotTableView.setModel(self.model)
            self.ShotTableView.update()
        except:
            self.msg('Database corrupted. Please reinitialize')
        
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