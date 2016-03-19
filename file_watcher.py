# -*- coding: utf-8 -*-
"""
Created on Mon May 11 11:38:05 2015

@author: admin
"""

import os
import win32file
import win32event
import win32con
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
    
        change_handle=win32file.FindFirstChangeNotification (self.path_to_watch,0,win32con.FILE_NOTIFY_CHANGE_FILE_NAME)
        try:
            old_path_contents=dict([(f,None) for f in os.listdir (self.path_to_watch)])
            while 1:
                result=win32event.WaitForSingleObject(change_handle,500)
                
                if result==win32con.WAIT_OBJECT_0:
                    new_path_contents=dict([(f,None) for f in os.listdir (self.path_to_watch)])
                    added=[f for f in new_path_contents if not f in old_path_contents]
#                    deleted=[f for f in old_path_contents if not f in new_path_contents]
                    for f in added:
                        fileName, fileExtension = os.path.splitext(f)
                                       
                        self.msg('Converting '+fileName + '\n')                    
                        
                        
                        try:                
                            getattr(ConvertFiles,'convert_'+fileExtension[1:])(fileName,True,self.env)
                            self.msg('File succesfully converted to hdf5.')
                        #self.emit(QtCore.SIGNAL('converted(QString)'),fileName)
                            
                        except :
#                            print str(e)
                            self.msg( "Unknown format..: "+fileExtension[1:]+'\n')
                            
                    old_path_contents=new_path_contents
                    win32file.FindNextChangeNotification(change_handle)
        finally:
            win32file.FindCloseChangeNotification (change_handle)
           
            
    def msg(self,text):
        self.emit(QtCore.SIGNAL('update(QString)'),'FileWatcher : '+text)