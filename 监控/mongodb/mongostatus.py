#!/usr/bin/python
# coding:utf-8
import subprocess

mongoport = "27017"
mongousername = "mongomonitor"
mongopassword ='jpbLTE0NjA0MzA0MzAsLTI2O'

def GetResult():
    mongocmd ='exit'
    cmd = "echo '%s' |mongo -u'%s' -p'%s' 127.0.0.1:'%s'/admin" %(mongocmd,mongousername,mongopassword,mongoport)
    result =  subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    stdout,stderr = result.communicate()
    if stderr:
        return False
    else:
        return  True


def GetPortAlvie():
    cmd = "ss -ltn |grep '%s' " %mongoport
    result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = result.communicate()
    if stdout:
        return True
    else:
        return False

if __name__=="__main__":
    loginresult = GetResult()
    portalve = GetPortAlvie()
    if loginresult == True and portalve == True:
        print(float(1))
    else:
        print(float(0))

