# -*- coding: utf-8 -*-
"""
Created on Mon May 11 11:38:05 2015

@author: admin
"""

import os
import time
import Queue
import ConvertFiles
from PyQt4 import QtCore


class fileWatcher(QtCore.QThread):
    
    def __init__(self,env):
        QtCore.QThread.__init__(self)
        self.path_to_watch=env.path
        self.listFiles=Queue.Queue()
        self.env=env
        
    def run(self):
        self.msg("Starting file watcher")
        try:
            old_path_contents=dict([(f,None) for f in os.listdir (self.path_to_watch)])
            while 1:
                time.sleep (10)
                

                new_path_contents=dict([(f,None) for f in os.listdir (self.path_to_watch)])
                added=[f for f in new_path_contents if not f in old_path_contents]
#                    deleted=[f for f in old_path_contents if not f in new_path_contents]
                for f in added:
                    fileName, fileExtension = os.path.splitext(f)
                                   
                    self.msg('Converting '+fileName + '\n')                    
                    
                    
                    try:                
                        result=getattr(ConvertFiles,'convert_'+fileExtension[1:])(fileName,True,self.env)
                        if fileExtension[1:]=='tdms':
                            shot=int(fileName[0:-5])
                            self.msg('File succesfully converted to hdf5.')
                            self.emit(QtCore.SIGNAL('newshot'),shot)
                    #self.emit(QtCore.SIGNAL('converted(QString)'),fileName)
                        if fileExtension[1:]=='csv':
                            shot=int(fileName[7:])
                            self.msg('CSV succesfully imported.')
                            self.emit(QtCore.SIGNAL('newcsv'),shot,result)
                        
                    except :
#                            print str(e)
                        self.msg( "Unknown format..: "+fileExtension[1:]+'\n',0)
                        
                old_path_contents=new_path_contents

        except:
            print "error"
           
            
    def msg(self,text):
        self.emit(QtCore.SIGNAL('update(QString)'),'FileWatcher : '+text)