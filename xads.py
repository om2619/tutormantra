#This script is to create multiple NonXA DS
import re

def file_parse():
    global _dict
    _dict={}
    ## Get Current directory path to located properties file
    import os 
    cwd = os.getcwd()
    # Get location of the properties file.
    properties = cwd+'/NonXADS.properties'
    print 'properties=', properties
    
    dsprop = properties
    if os.path.exists(dsprop):
        fo = open(dsprop,'r+')
        lines = fo.readlines()
        for line in lines:
            if "=" in line:
                line = line.rstrip()
                key = line.split('=')[0]
                value = line.split('=')[1]
                _dict[key]=value
    else:
        print(dsprop+" property file is missing !")
        exit()

def connect_domain():
    try:
        AdmSvr = _dict.get('AdminServer')
        AdmPort = _dict.get('AdminPort')
        AdmURL = "t3://"+AdmSvr+":"+AdmPort
        usernName = _dict.get('username')
        passWord = _dict.get('password')
        print("Connecting to Admin server")
        connect(usernName, passWord, AdmURL)
        print("connection successfull")
    except Exception, error:
        print ("\nUnable to connect to admin server")
        print ("Please verify the URL (or) check if Admin server is stopped")
        print ("Error description as follows:\n")
        print(error)
        print dumpStack()
        exit()

def create_NonXA_ds(DSN,DSJ,DSU,DSP,DSC):
    db_host = _dict.get('dbHostName')
    db_port = _dict.get('dbPort')
    db_name = _dict.get('dbServiceName')
    jdbcURL = 'jdbc:oracle:thin:@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST='+db_host+')(PORT='+db_port+')))(CONNECT_DATA=(SERVICE_NAME='+db_name+')))'
    db_driver = _dict.get('dbDriver')

    try:
        edit()
        startEdit()
        print("\nCreating "+DSN+" datasource")
        cd('/')
        cmo.createJDBCSystemResource(DSN)
        cd('/JDBCSystemResources/'+DSN+'/JDBCResource/'+DSN)
        cmo.setName(DSN)
        cd('JDBCDataSourceParams/'+DSN)
        set('JNDINames',jarray.array([String(DSJ)], String))
        cd('/JDBCSystemResources/'+DSN+'/JDBCResource/'+DSN+'/JDBCDriverParams/'+DSN)
        cmo.setUrl(jdbcURL)
        cmo.setDriverName(db_driver)
        cmo.setPassword(DSP)
        cd('/JDBCSystemResources/'+DSN+'/JDBCResource/'+DSN+'/JDBCConnectionPoolParams/'+DSN)
        cmo.setTestTableName('SQL ISVALID\r\n\r\n')
        cd('/JDBCSystemResources/'+DSN+'/JDBCResource/'+DSN+'/JDBCDriverParams/'+DSN+'/Properties/'+DSN)
        cmo.createProperty('user')
        cd('/JDBCSystemResources/'+DSN+'/JDBCResource/'+DSN+'/JDBCDriverParams/'+DSN+'/Properties/'+DSN+'/Properties/user')
        cmo.setValue(DSU)
        cd('/JDBCSystemResources/'+DSN)
        
        cd('/JDBCSystemResources/' + DSN + '/JDBCResource/' + DSN + '/JDBCDataSourceParams/' + DSN)
        #cmo.setGlobalTransactionsProtocol('TwoPhaseCommit')
        #GlobalTransactionsProtocol. The value must be one of the following: [TwoPhaseCommit, LoggingLastResource, EmulateTwoPhaseCommit, OnePhaseCommit, None]
        cmo.setGlobalTransactionsProtocol('None')

        cd('/JDBCSystemResources/'+DSN)

        datasourceTargets = re.split(",",DSC)
        targetArray=[]

        for datasourceTarget in datasourceTargets:
            print 'DataSourceTargets=',datasourceTargets
            print 'DataSourceTarget=',datasourceTarget
            if datasourceTarget=='':
                print ''
            else:
                set('Targets',jarray.array([], ObjectName))
                target=datasourceTarget[datasourceTarget.index("/")+1:len(datasourceTarget)]
                if datasourceTarget.startswith('Cluster'):
                    targetArray.append(ObjectName('com.bea:Name='+target+',Type=Cluster'))
                elif datasourceTarget.startswith('Server'):
                    targetArray.append(ObjectName('com.bea:Name='+target+',Type=Server'))

            print 'Targets: ',targetArray
            set('Targets',jarray.array(targetArray, ObjectName))
            print 'DataSource: ',DSN,',Target has been updated Successfully !!!'
            print '========================================='

        ##set('Targets',jarray.array([ObjectName('com.bea:Name='+DSC+',Type=Cluster')], ObjectName))
        cd('/JDBCSystemResources/'+DSN+'/JDBCResource/'+DSN+'/JDBCConnectionPoolParams/'+DSN)        
        set('TestConnectionsOnReserve', 'true')
        save()
        activate()
        print(DSN+" datasource has been created successfully\n")
    except Exception, error:
        print"------------------------------------------------------------"
        print("\nUnable to create "+DSN+" datasource")
        print(error)
        print dumpStack()
        print("proceeding to create the next datasource\n")
        print"------------------------------------------------------------"
        undo(defaultAnswer='y')
        stopEdit(defaultAnswer='y')

def duplicate_ds_validation(DSN):
    cd('/')
    cd('JDBCSystemResources')
    oldDS = ls(returnMap='true')
    if DSN in oldDS:
        return true
    else:
        return false

def db_credential_validation(DSU,DSP):
    db_typ = _dict.get('dbType')
    db_host = _dict.get('dbHostName')
    db_port = _dict.get('dbPort')
    db_name = _dict.get('dbServiceName')
    #dbTest = "java utils.dbping "+db_typ+" "+DSU+" "+DSP+" "+db_host+":"+db_port+"/"+db_name+">/dev/null 2>&1"
    #dbResult = os.system(dbTest)
    #if dbResult == 0:
    #    return true
    #else:
    #    return false
    return true


import os
import sys

redirect("/dev/null",'false')

file_parse()
print"\n\n------------------------------------------------------------"
connect_domain()
print"------------------------------------------------------------"

ds = _dict.get('DataSource').split(',')
for each_ds in ds:
        DS_N = _dict.get(each_ds+'.Name')
        DS_J = _dict.get(each_ds+'.jndiName')
        DS_U = _dict.get(each_ds+'.dbUName')
        DS_P = _dict.get(each_ds+'.dbPasswd')
        DS_C = _dict.get(each_ds+'.Targets')

        if db_credential_validation(DS_U,DS_P):
           if not duplicate_ds_validation(DS_N):
                create_NonXA_ds(DS_N,DS_J,DS_U,DS_P,DS_C)
           else:
                print"\n------------------- Duplicate DS found ! -------------------"
                print("\nThere is already a ds with the name: "+DS_N)
                print("skipping "+DS_N+" ds creation\n")
                print"------------------------------------------------------------\n"
                print"--------------Welcome to Piraeus Bank------------------\n"
                print"--------------The world of Banking---------------------\n"
                print"--------------Your money is secure just like you-------------\n"
        else:
            print"\n---------------- DB connectivity failure ! -----------------"
            print("\nUnable to connect the database with "+DS_U+" user")
            print("skipping "+DS_N+" ds creation\n")
            print"------------------------------------------------------------\n"
            print"--------------------Scripting Complete !---------------------\n"
            
print"\n------------------------------------------------------------\n"
print"                     cheers for using WLST !                    "
print"\n------------------------------------------------------------\n"

print"\n------------------------------------------------------------\n"
print"\n-------------------Scripting In Process---------------------\n"
print"\n-------------------We are working on the UI-----------------\n"
print"\n-------------------Server looks to be down------------------\n"
print"\n-------------------Maintenance Complete---------------------\n"
print"\n------------------------------------------------------------\n"
print"\n------------------------------------------------------------\n"
print"\n------------------------------------------------------------\n"
print"\n------------------------------------------------------------\n"
