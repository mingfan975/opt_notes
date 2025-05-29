
## ZABBIX监控MongoDB 部署步骤：
### 一.客户端操作
1.客户端安装zabbix-agent,建议使用4.0以上版本,配置文件配置timeout=30，其他此处省略。
2. mongodb创建角色与用户（副本集集群在PRIMARY上创建）
```
onlineDb:PRIMARY> db.createRole(        
    { role:"rolename",
    privileges:[{resource:{cluster:true},actions:["serverStatus","replSetGetStatus"]}],
 roles:[]}
)


onlineDb:PRIMARY> db.createUser(
 {
user:"username",
 pwd:"password",
 roles:[{role:"rolename",db:"admin"}]}
 )
```
3.监控脚本放入/etc/zabbix/zabbix_agentd.d 目录下，脚本属主属组设置为zabbix，增加执行权限

4.修改脚本配置
```
4.1 mongodbmonitor.py修改如下内容
MongoUser = 'username'
MongoPass = 'password'
MongoRepliset = "127.0.0.1:port"
host = "公网ip:port"

4.2 mongostatus.py修改如下内容
port = "port"
username = "username"
password ="password"
```

5./etc/zabbix/zabbix_agentd.d/UserParameters.conf文件增加如下内容
```
UserParameter=mongo_monitor[*],/usr/bin/python /etc/zabbix/script/mongodbmonitor.py $1
UserParameter=mongostatus,/usr/bin/python /etc/zabbix/script/mongostatus.py
```

6.安装pymongo
```
pip install pymongo
```

7.测试
```
python mongodbmonitor.py role
python mongostatus.py 
```


### 二.ZABBIX SERVER操作
导入模版mongodb_templates.xml


<!--stackedit_data:
eyJoaXN0b3J5IjpbLTE0NjA0MzA0MzAsLTI2ODIyMzA0NSwxNT
c4OTA1MDI3LC03NTY0MjEzODgsNzMwOTk4MTE2XX0=
-->

db.auth("admin","KpWwAjI9kSttMQG21VSk")
db.changeUserPassword("mongomonitor","jpbLTE0NjA0MzA0MzAsLTI2O")
jpbLTE0NjA0MzA0MzAsLTI2O

58.82.228.184
apt install -y  python python-pip 
pip install pymongo


tail -f /var/log/zabbix/zabbix_agentd.log
systemctl restart zabbix-agent.service
