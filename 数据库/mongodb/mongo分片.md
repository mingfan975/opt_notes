# mongodb分片  
## 概念
```
分片(sharding): 是指将数据库拆分，将其分散在不同的机器上的过程。将数据分散到不同的机器上，不需要功能强大的服务器就可以存储更多的数据和处理更大的负载。基本思想就是将集合切成小块，这些块分散到若干片里，每个片只负责总数据的一部分，最后通过一个均衡器来对各个分片进行均衡（数据迁移）。通过一个名为mongos的路由进程进行操作，mongos知道数据和片的对应关系（通过配置服务器）
```
## 使用场景
```
1. 单个服务器无法承受压力时，压力包括负载、频繁写、吞吐量等；
2. 服务器磁盘空间不足时；
3. 增加可用内存大小，以更多的数据在内存中访问。
```
## 角色
```
1. 配置服务器:
    是一个独立的mongod进程，保存集群和分片的元数据，即各分片包含了哪些数据的信息。最先开始建立，启用日志功能。像启动普通的mongod一样启动配置服务器，指定configsvr选项。不需要太多的空间和资源，配置服务器的1KB空间相当于真是数据的200MB。保存的只是数据的分布表。当服务不可用，则变成只读，无法分块、迁移数据
    mongos 启动时会加载配置服务器上的配置信息，以后如果配置服务器信息变化会通知到所有的 mongos 更新自己的状态。生产环境需要多个 配置服务器。也需要定期备份
2. 路由服务器:
    即mongos，起到一个路由的功能，供程序连接。本身不保存数据，在启动时从配置服务器加载集群信息，开启mongos进程需要知道配置服务器的地址，指定configdb选项，生产环境中需要多个 mongos
3. 分片服务器：
    是一个独立普通的mongod进程，保存数据信息。生产环境要求使用副本集
```
## 配置步骤
```
官方文档: 
    https://docs.mongodb.com/v3.6/core/sharded-cluster-components/
    https://docs.mongodb.com/v3.6/tutorial/deploy-shard-cluster/
第一步：创建Config Server实例,配置Config Server实例成Replica Set
第二步：创建Shard Server实例，配置Shard Server实例成Replica Set
第三步：创建Route Server实例，把Config Server实例和Shard Server实例配置进来
第四步：创建数据库并执行db.printShardingStatus()命令验证
```

## 配置服务器配置
```conf
systemLog:
    verbosity: 0
    quiet: false
    traceAllExceptions: true
    path: /data/mongoTest/logs/mongod_40001.log
    logAppend: true
    logRotate: rename
    destination: file
    timeStampFormat: iso8601-local
processManagement:
    fork: true
    pidFilePath: /var/run/mongod_40001.pid
cloud:
    monitoring:
        free:
            state: off
net:
    port: 40001
    bindIp: 0.0.0.0
    #	bindIpAll: true # 3.6 新功能   如果为true，则mongos  或者 mongod实例绑定到所有IPv4地址（即0.0.0.0） 如果以net.ipv6 : true 启动则侦听 所有的ipv6地址
    maxIncomingConnections: 65535
    wireObjectCheck: true
    ipv6: false
#	unixDomainSocket:
#      		enabled: true  # 在UNIX域套接字上启用或禁用侦听 仅适用于基于Unix的系统
#		pathPrefix: /tmp # UNIX套接字的路径 仅适用于基于Unix的系统
#		filePermissions: 0700 # 设置UNIX域套接字文件的权限
#    tls:
#        mode: disabled # requireTLS
#        certificateKeyFile: /data/mongoTest/mongokey/tlsKeyFile
#        certificateKeyFilePassword: Lkab0ZajMDN5lRCyCI3MWiGo1fy1bfMvN
#        clusterFile: /data/mongoTest/mongokey/clusterTlsKeyFile
#        clusterPassword: Lkab0ZajMDN5lRCyCI3MW
#        CAFile: /data/mongoTest/mongokey/caFile
#        clusterCAFile: /data/mongoTest/mongokey/clusterCaFile
#        CRLFile: /data/mongoTest/mongokey/crlFile
#        allowConnectionsWithoutCertificates: true
#        allowInvalidCertificates: false
#        allowInvalidHostnames: true
security:
    authorization: enabled
    keyFile: /data/mongoTest/mongokey/keyFile
    clusterAuthMode: keyFile
    transitionToAuth: false
    javascriptEnabled: true
storage:
    dbPath: /data/mongoTest/configServer/config_40001
    #indexBuildRetry: true # 指定mongdb在下次启东市是否重新创建不完整的索引，默认true
    directoryPerDB: true # MongoDB使用单独的目录来存储每个数据库的数据
    syncPeriodSecs: 60 #在MongoDB将数据通过sync操作刷新到数据文件之前可以传递的时间量,默认60s
    engine: wiredTiger
    wiredTiger:
        engineConfig:
            cacheSizeGB: 1
            journalCompressor: zlib
            directoryForIndexes: true
            maxCacheOverflowFileSizeGB: 0
        collectionConfig:
            blockCompressor: zlib
        indexConfig:
            prefixCompression: true
replication:
    replSetName: config
sharding:
    clusterRole: configsvr
```

## 路由服务器配置
```conf
systemLog:
    verbosity: 0
    quiet: false
    traceAllExceptions: true
    path: /data/mongoTest/logs/mongod_30001.log
    logAppend: true
    logRotate: rename
    destination: file
    timeStampFormat: iso8601-local
processManagement:
    fork: true
    pidFilePath: /var/run/mongod_30001.pid
net:
    port: 30001
    bindIp: 0.0.0.0
    #	bindIpAll: true # 3.6 新功能   如果为true，则mongos  或者 mongod实例绑定到所有IPv4地址（即0.0.0.0） 如果以net.ipv6 : true 启动则侦听 所有的ipv6地址
    maxIncomingConnections: 65535
    wireObjectCheck: true
    ipv6: false
#	unixDomainSocket:
#      		enabled: true  # 在UNIX域套接字上启用或禁用侦听 仅适用于基于Unix的系统
#		pathPrefix: /tmp # UNIX套接字的路径 仅适用于基于Unix的系统
#		filePermissions: 0700 # 设置UNIX域套接字文件的权限
#    tls:
#        mode: disabled # requireTLS
#        certificateKeyFile: /data/mongoTest/mongokey/tlsKeyFile
#        certificateKeyFilePassword: Lkab0ZajMDN5lRCyCI3MWiGo1fy1bfMvN
#        clusterFile: /data/mongoTest/mongokey/clusterTlsKeyFile
#        clusterPassword: Lkab0ZajMDN5lRCyCI3MW
#        CAFile: /data/mongoTest/mongokey/caFile
#        clusterCAFile: /data/mongoTest/mongokey/clusterCaFile
#        CRLFile: /data/mongoTest/mongokey/crlFile
#        allowConnectionsWithoutCertificates: true
#        allowInvalidCertificates: false
#        allowInvalidHostnames: true
security:
    keyFile: /data/mongoTest/mongokey/keyFile
    clusterAuthMode: keyFile
    transitionToAuth: false
    javascriptEnabled: true
sharding:
    configDB: config/121.201.122.224:40001,121.201.122.224:40002,121.201.122.224:40003
```
## 分片服务器配置
```conf
systemLog:
    verbosity: 0
    quiet: false
    traceAllExceptions: true
    path: /data/mongoTest/logs/mongod_20194.log
    logAppend: true
    logRotate: rename
    destination: file
    timeStampFormat: iso8601-local
processManagement:
    fork: true
    pidFilePath: /var/run/mongod_20194.pid
cloud:
    monitoring:
        free:
            state: off
net:
    port: 20194
    bindIp: 0.0.0.0
    #	bindIpAll: true # 3.6 新功能   如果为true，则mongos  或者 mongod实例绑定到所有IPv4地址（即0.0.0.0） 如果以net.ipv6 : true 启动则侦听 所有的ipv6地址
    maxIncomingConnections: 65535
    wireObjectCheck: true
    ipv6: false
#	unixDomainSocket:
#      		enabled: true  # 在UNIX域套接字上启用或禁用侦听 仅适用于基于Unix的系统
#		pathPrefix: /tmp # UNIX套接字的路径 仅适用于基于Unix的系统
#		filePermissions: 0700 # 设置UNIX域套接字文件的权限
#    tls:
#        mode: disabled # requireTLS
#        certificateKeyFile: /data/mongoTest/mongokey/tlsKeyFile
#        certificateKeyFilePassword: Lkab0ZajMDN5lRCyCI3MWiGo1fy1bfMvN
#        clusterFile: /data/mongoTest/mongokey/clusterTlsKeyFile
#        clusterPassword: Lkab0ZajMDN5lRCyCI3MW
#        CAFile: /data/mongoTest/mongokey/caFile
#        clusterCAFile: /data/mongoTest/mongokey/clusterCaFile
#        CRLFile: /data/mongoTest/mongokey/crlFile
#        allowConnectionsWithoutCertificates: true
#        allowInvalidCertificates: false
#        allowInvalidHostnames: true
security:
    authorization: enabled
    keyFile: /data/mongoTest/mongokey/keyFile
    clusterAuthMode: keyFile
    transitionToAuth: false
    javascriptEnabled: true
storage:
    dbPath: /data/mongoTest/configServer/config_20194
    #indexBuildRetry: true # 指定mongdb在下次启东市是否重新创建不完整的索引，默认true ，此选项不能和副本集同时使用
    directoryPerDB: true # MongoDB使用单独的目录来存储每个数据库的数据
    syncPeriodSecs: 60 #在MongoDB将数据通过sync操作刷新到数据文件之前可以传递的时间量,默认60s
    engine: wiredTiger
    wiredTiger:
        engineConfig:
            cacheSizeGB: 1
            journalCompressor: zlib
            directoryForIndexes: true
            maxCacheOverflowFileSizeGB: 0
        collectionConfig:
            blockCompressor: zlib
        indexConfig:
            prefixCompression: true
replication:
    replSetName: shardTest
sharding:
    clusterRole: shardsvr
```
## 分片操作相关命令
```bash
mongos> sh.enableSharding("mydb") # 对指定的db开启分片 或者使用 db.runCommand( { enableSharding: "mydb" } )
mongos> sh.status() # 查看分片状态

mongos> db.test.ensureIndex( {"user_id": 1} ) # 对集合创建索引
mongos> db.test.ensureIndex( {"user_id": 1}, {"name": "idx_user_id", "background": true} ) # 数据量比较大的话可以使用后台创建索引
mongos> sh.shardCollection("mydb.test", {"user_id": 1}) # 对数据进行分片操作（单索引分片）
mongos> sh.shardCollection("mydb.test", { "user_name": 1, "_id": 1 } ) # 混合索引分片
mongos> sh.shardCollection("mydb.test", {"user_id": "hashed"}) # hash 索引分片
mongos> sh.status() # 查看分片状态

```
## 注意事项
```
1. 每个分片副本集名称不能相同
2. 路由服务器配置不需要authorization 选项
3. 对集合(表)创建索引: 
    对于已经存在数据的collection，需要提前在shardkey上创建索引，
    如果collection是空的，MongoDB会在启用分片的过程中自动创建索引
```