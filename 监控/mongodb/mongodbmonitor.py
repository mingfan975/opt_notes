from pymongo import MongoClient
import sys
import re
import subprocess
from bson.json_util import loads, dumps


# MongoUser = 'usera05name'
# MongoPass = 'passg03word'
# MongoHost = "127.0.0.1:37117"
# host = "45.114.175.78:37117"

MongoUser = 'admin'
MongoPass = 'Bi24ToROPrviPIuS'
MongoHost = "127.0.0.1:27117"
host = "27.124.9.130:27117"

'''
数据库创建角色

db.createUser({
    user:"usera05name",
    pwd:"passg03word",
    roles:[{role:"rolename",db:"admin"},{ role: "clusterMonitor", db: "admin"}]
    })
db.grantRolesToUser( "usera05name", [{ role: "clusterMonitor", db: "admin"}])
'''


def login(mongoHost, MongoUser, MongoPass, cmd, database="admin"):
    '''
    登陆mongodb并执行mongodb命令，返回对应的结果
    :return:
    '''
    try:
        mongoClient = MongoClient(
            mongoHost, username=MongoUser, password=MongoPass)
        result = mongoClient[database].command(cmd)
        return result
    except Exception as e:
        print(e)
    sys.exit()


def getRole(mongoHost, MongoUser, MongoPass):
    """
    获取mongodb角色
    """
    mongoStatus = login(mongoHost, MongoUser, MongoPass, "isMaster")
    if mongoStatus['primary'] == mongoStatus['me'] and mongoStatus['ismaster'] == True:
        role = 'PRIMARY'
    elif mongoStatus['primary'] != mongoStatus['me'] and mongoStatus['secondary'] == True:
        role = 'SECONDARY'
    elif mongoStatus['primary'] != mongoStatus['me'] and mongoStatus['arbiters'] == mongoStatus['me']:
        role = 'ARBITER'
    else:
        role = 'OTHER'
    return role


def getphysicalmemorymb():
    """
    获取服务器物理内存
    """
    meminfo = open('/proc/meminfo').read()
    matched = re.search(r'^MemTotal:\s+(\d+)', meminfo)
    return int(matched.groups()[0])/1024


def RepInfo(masterIp, mongoHost, MongoUser, MongoPass):
    """
    计算主从延时
    """
    if host == masterIp:
        secs = 0
        return secs
    cmd = "mongo %s/admin -u %s  -p %s --quiet --eval 'db.printSlaveReplicationInfo()'" % (host,
                                                                                           MongoUser, MongoPass)
    result = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = result.communicate()
    for i in stdout.decode("utf-8").strip().split('primary'):
        info = i.strip().split('\n\t')
        if len(info) > 2:
            server = info[0].split()[-1]
            secs = int(info[-1].split()[0])
            if server == host:
                return secs


def getServerStatus(mongoHost, MongoUser, MongoPass):
    """
    获取serverStatus
    返回serverStatus
    """
    serverStatus = login(mongoHost, MongoUser, MongoPass, 'serverStatus')
    return serverStatus


def getLogs(mongoHost, MongoUser, MongoPass):
    """获取数据库日志"""
    cmd = "mongo %s/admin -u %s  -p %s --quiet --eval 'db.adminCommand({getLog: \"global\"}).log'" % (
        mongoHost, MongoUser, MongoPass)
    result = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = result.communicate()
    result = {}
    drop_lst = []
    for d in loads(stdout.decode("utf-8")):
        if "COMMAND" in d:
            cmd_time = d.strip().split(" ")[-1]
            if "ms" in cmd_time:
                result[cmd_time.strip("ms")] = d
            elif "drop" in d:
                drop_lst.append(d)
    result_sort = sorted(result.keys())[-10:]
    command_lst = ""
    for i in result_sort:
        for k, v in result.items():
            if i == k:
                command_lst += re.findall(".*command:(.*)numYields.*",
                                          v)[0]+" "+k+"ms" + "\n"
    if command_lst == "":
        return None
    return command_lst


def getCurrentOPs(mongoHost, MongoUser, MongoPass):
    """
    返回当前操作超过3秒的命令
    """
    cmd = {"currentOp": True,  "active": True, "secs_running": {"$gt": 3},
           "$or": [
        {"op": {"$in": ["insert", "update", "remove"]}},
        {"command.findandmodify": {"$exists": True}}
    ]}
    result = login(mongoHost, MongoUser, MongoPass, cmd)
    if len(result["inprog"]) == 0:
        return None
    else:
        return result["inprog"]


def monitor(mongoHost, MongoUser, MongoPass):
    '''
    监控的参数
    :return:
    '''
    result_dict = getServerStatus(mongoHost, MongoUser, MongoPass)
    # 排队等待锁定的操作的总和
    total_operate = result_dict["globalLock"]["currentQueue"]["total"]
    # 当前排队并等待写锁定的操作数
    read_operate = result_dict["globalLock"]["currentQueue"]["readers"]
    # 当前排队并等待写锁定的操作数
    write_operate = result_dict["globalLock"]["currentQueue"]["writers"]

    # 执行读写操作的活动客户端连接数
    total_active_client = result_dict["globalLock"]["activeClients"]["total"]
    # 执行读操作的活动客户端连接数
    read_active_client = result_dict["globalLock"]["activeClients"]["readers"]
    # 执行写操作的活动客户端连接数
    write_active_client = result_dict["globalLock"]["activeClients"]["writers"]

    # # 页面错误总数 在性能低下的时候，extra_info.page_faults计数器可能会急剧增加，并且可能与有限的内存环境和更大的数据集相关
    # extra_info_page_faults = result_dict["extra_info"]["page_faults"]
    # # 自上次刷新周期以来，由mongod或mongos实例缓存在内存中的所有活动本地会话数
    # lsrc_asc = result_dict["logicalSessionRecordCache"]["activeSessionsCount"]

    # # 反映此数据库接收的网络流量的字节数
    # network_in = result_dict["network"]["bytesIn"]
    # # 反映此数据库发送的网络流量的字节数
    # network_out = result_dict["network"]["bytesIn"]
    # # 服务器收到不同请求的总数
    # network_num_request = result_dict["network"]["bytesIn"]

    # # 读取请求延时统计
    # oplatencies_read_late = result_dict["opLatencies"]["reads"]["latency"]
    # oplatencies_read_ops = result_dict["opLatencies"]["reads"]["ops"]

    # # 写请求延时统计
    # oplatencies_write_late = result_dict["opLatencies"]["writes"]["latency"]
    # oplatencies_write_ops = result_dict["opLatencies"]["writes"]["ops"]

    # # command请求延时统计
    # oplatencies_command_late = result_dict["opLatencies"]["commands"]["latency"]
    # oplatencies_command_ops = result_dict["opLatencies"]["commands"]["ops"]

    # # mongo 实例启动以来的操作总数
    # op_insert = result_dict["opcounters"]["insert"]
    # op_query = result_dict["opcounters"]["query"]
    # op_update = result_dict["opcounters"]["update"]
    # op_delete = result_dict["opcounters"]["delete"]
    # op_getmore = result_dict["opcounters"]["getmore"]
    # op_command = result_dict["opcounters"]["command"]

    # # mongo实例启动以来副本集操作总数
    # op_repl_insert = result_dict["opcountersRepl"]["insert"]
    # op_repl_query = result_dict["opcountersRepl"]["query"]
    # op_repl_update = result_dict["opcountersRepl"]["update"]
    # op_repl_delete = result_dict["opcountersRepl"]["delete"]
    # op_repl_getmore = result_dict["opcountersRepl"]["getmore"]
    # op_repl_command = result_dict["opcountersRepl"]["command"]

    # # 获取副本集信息
    # repl_host_lst = result_dict["repl"]["hosts"]
    # repl_ismaster = result_dict["repl"]["ismaster"]
    # repl_secondary = result_dict["repl"]["secondary"]
    # repl_primary = result_dict["repl"]["primary"]
    # repl_me = result_dict["repl"]["me"]
    # # 回滚标示
    # repl_rbid = result_dict["repl"]["rbid"]
    # # 选举标示（主节点）
    # repl_electionId = result_dict["repl"]["electionId"]

    # get master ip
    masterip = result_dict["repl"]["primary"]

    role = getRole(mongoHost, MongoUser, MongoPass)
    delaytime = RepInfo(masterip, mongoHost, MongoUser, MongoPass)

    # 启动时间
    uptime = int(result_dict['uptime'] / 3600 / 24)

    # 物理内存和虚拟内存
    mem = result_dict['mem']
    phyMem = mem['resident']
    virMem = mem['virtual']
    phymemall = getphysicalmemorymb()
    premem = (float(phyMem) / float(phymemall)) * 100

    # connections
    connections = result_dict['connections']
    currentCon = connections['current']
    availableCon = connections['available']
    totalCreatedCon = connections['totalCreated']
    precenConn = float(currentCon) / float((currentCon + availableCon)) * 100

    # active Connecter
    activeConn = result_dict['globalLock']['activeClients']
    readClient = activeConn['readers']
    writerClient = activeConn['writers']

    # opcounters
    opcounters = result_dict['opcounters']
    getmore = opcounters['getmore']
    insert = opcounters['insert']
    update = opcounters['update']
    command = opcounters['command']
    query = opcounters['query']
    delete = opcounters['delete']
    count = getmore + insert + update + command + query + delete

    # Cache
    maxCache = result_dict['wiredTiger']['cache']['maximum bytes configured'] / (
        1024 * 1024)
    currCache = result_dict['wiredTiger']['cache']['bytes currently in the cache'] / (
        1024 * 1024)
    try:
        precenCache = (float(currCache) / float(maxCache)) * 100
    except ZeroDivisionError:
        precenCache = (float(currCache) / 200) * 100

    # Transactions
    tranWirte = result_dict['wiredTiger']['concurrentTransactions']['write']['available']
    tranRead = result_dict['wiredTiger']['concurrentTransactions']['read']['available']
    logs = getLogs(MongoHost, MongoUser, MongoPass)
    currentOps = getCurrentOPs(mongoHost, MongoUser, MongoPass)
    monitorDict = {'uptime': uptime,
                   'phyMem': phyMem,
                   'virMem': virMem,
                   'currentCon': currentCon,
                   'availableCon': availableCon,
                   'totalCreatedCon': totalCreatedCon,
                   'getmore': getmore,  # command错误数
                   'insert': insert,
                   'update': update,
                   'command': command,
                   'query': query,
                   'delete': delete,
                   'count': count,
                   'precenConn': precenConn,
                   'readClient': readClient,
                   'writerClient': writerClient,
                   'maxCache': maxCache,
                   'currCache': currCache,
                   'wtCahcePrecen': precenCache,
                   'tranWirte': tranWirte,  # 并发
                   'tranRead': tranRead,
                   'masterip': masterip,
                   'premem': premem,
                   'delaytime': delaytime,
                   'role': role,
                   "total_operate": total_operate,
                   "read_operate": read_operate,
                   "write_operate": write_operate,
                   "total_active_client": total_active_client,
                   "read_active_client": read_active_client,
                   "write_active_client": write_active_client,
                   "logs": logs,
                   "currentOps": currentOps
                   }

    return monitorDict


if __name__ == '__main__':
    zabbix = monitor(MongoHost, MongoUser, MongoPass)
    if sys.argv[1] in zabbix:
        print(zabbix[sys.argv[1]])
    else:
        print("key error")
