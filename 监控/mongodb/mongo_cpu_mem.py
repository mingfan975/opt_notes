#!/usr/bin/python3
import subprocess
import sys
port = '37119'


def GetPid():
    """
    获取进程id
    """
    cmd = "netstat  -luntp |grep 'mongod' |grep %s|grep -v grep|awk '{print $NF}'" % port
    result = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = result.communicate()
    formatResult = stdout.decode("utf-8").strip().split('/')[0]
    if formatResult != None:
        return formatResult


def DealDataCpu():
    """
    获取程序cpu和内存
    """
    info = {}
    pid = GetPid()
    cmd = "pidstat -ur -h -p %s 1 2|grep 'mongod' |egrep -v grep" % pid
    result = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = result.communicate()
    formatResult = stdout.decode("utf-8").strip().split("\n")[-1]
    formatResult = formatResult.split()[3:-1]
    info['cpu'] = formatResult[5]
    info['mem'] = formatResult[-1]
    if info != "":
        return info


if __name__ == "__main__":
    result = DealDataCpu()
    if result != None:
        if sys.argv[1] in result:
            print(float(result[sys.argv[1]]))
        else:
            print("key error")
