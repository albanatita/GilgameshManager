# -*- coding: utf-8 -*-
"""
Created on Mon May 11 11:14:38 2015

@author: admin
"""

from nptdms import TdmsFile
import h5py
import os
import time
import re
import gilgamesh.environmentGilga as envG
#import readHdf5

def convert_tdms(fileName,tempo,env):
    if tempo:    
        time.sleep(20)    
    path=env.path
    tdms_file=TdmsFile(os.path.join(path,fileName+'.tdms'))
   # tdms_file=TdmsFile(r'D:\DATA\00838_Data.tdms')
    hdf5=h5py.File(envG.H5path+fileName+'.h5','w')
    #channel=tdms_file.object('PXI M6251','Lang_U')
    #group=tdms_file.object('PXI M6251')
    grouplist=tdms_file.groups()
    #print grouplist
    for i in grouplist:
        group=tdms_file.object(i)
        grouph=hdf5.create_group(i)
        print group.path
        if group.path=='/\'PXI M6251\'':
            nbchannels=group.properties['Nchannel']
            tstart=group.properties['Tstart']
            sampling=group.properties['SampleTime']
        if group.path=='/\'Tektronix\'':    
            tstart=group.properties['Tstart']
            #sampling=group.properties['SampleTime']
            sampling=1/1.25e9
            nbchannels=group.properties['Nchannel']
        if group.path=='/\'S7\'':
            nbchannels=group.properties['Nchannel']
            tstart=0.
            sampling=1.
        #print nbchannels,tstart,sampling
        grouph.attrs['Nchannel']=nbchannels
        grouph.attrs['Tstart']=tstart
        grouph.attrs['sampling']=1/float(sampling)
        liste=tdms_file.group_channels(i)
    
        for j in liste:
            grouph.create_dataset(re.sub('[\']','',j.path),data=j.data,compression="gzip")
            
#    conn=sqlite3.connect('ishtar')
#    curs=conn.cursor()
#    curs.execute('insert into shots values(?,?,?,?,?)',(int(fileName[0:-5]),fileName,0.,0.,0.))
#    conn.commit()
    hdf5.create_group('Process')
    hdf5.close()
    return 1
    #env.process.addFile(fileName)

def convert_csv(fileName,tempo,env):
    path=env.path
    if tempo:    
        time.sleep(2)   
    try:
        inputfile=open(path+os.sep+fileName+'.csv')
        #inputfile.next()
        print inputfile.readline()
        #timei=datetime.datetime.strptime(inputfile.readline()[13:-1],'%d.%m.%Y %H:%M:%S')
        timei=inputfile.readline()[13:-1]        
    #print timei
        #h5file=fileName[7:].zfill(5)+'_Data'
    #print h5file
    #    readHdf5.saveAttr(h5file,'date',timei,env)  
    #print h5file      
    except:
        print "Doesn't work"
    return timei

