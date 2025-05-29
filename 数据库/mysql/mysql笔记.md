
- [mysql 安装配置文档](#mysql-安装配置文档)
	- [部署安装](#部署安装)
		- [Ubuntu](#ubuntu)
		- [Centos](#centos)
		- [部署公共部分(数据库)](#部署公共部分数据库)
		- [DCL(数据库控制)](#dcl数据库控制)
			- [赋予相关权限](#赋予相关权限)
			- [赋予exDb库所有权限](#赋予exdb库所有权限)
			- [撤销某种权限](#撤销某种权限)
			- [撤销所有权限](#撤销所有权限)
			- [注意：检查现有`版本号`是否还存在,可以换成其他新版本的源码包](#注意检查现有版本号是否还存在可以换成其他新版本的源码包)
- [主从复制](#主从复制)
	- [基本概念](#基本概念)
	- [复制的目的](#复制的目的)
	- [复制原理](#复制原理)
	- [复制的类型](#复制的类型)
		- [MySQL基于SQL语句的主从复制详解](#mysql基于sql语句的主从复制详解)
		- [1. 概述](#1-概述)
		- [2. 工作原理](#2-工作原理)
		- [3. 优点](#3-优点)
		- [4. 缺点](#4-缺点)
		- [5. 适用场景](#5-适用场景)
		- [6. 配置步骤](#6-配置步骤)
			- [主服务器配置](#主服务器配置)
			- [从服务器配置](#从服务器配置)
	- [7. 注意事项](#7-注意事项)
	- [8. 故障排除](#8-故障排除)
	- [9. 最佳实践](#9-最佳实践)
	- [结论](#结论)
			- [MySQL基于行的主从复制详解](#mysql基于行的主从复制详解)
	- [1. 概述](#1-概述-1)
	- [2. 工作原理](#2-工作原理-1)
	- [3. 优点](#3-优点-1)
	- [4. 缺点](#4-缺点-1)
	- [5. 适用场景](#5-适用场景-1)
	- [6. 配置步骤](#6-配置步骤-1)
			- [主服务器配置](#主服务器配置-1)
			- [从服务器配置](#从服务器配置-1)
	- [7. 注意事项](#7-注意事项-1)
	- [8. 故障排除](#8-故障排除-1)
	- [9. 最佳实践](#9-最佳实践-1)
	- [10. 与其他复制模式的比较](#10-与其他复制模式的比较)
	- [结论](#结论-1)
	- [复制模式](#复制模式)
	- [基于GTID复制](#基于gtid复制)

# mysql 安装配置文档

## 部署安装

### Ubuntu

~~~bash
wget http://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-5.7.10.tar.gz
bash ubuntu_install_db.sh init mysql-5.7.10 /data/mysql_3307 3307
#!/bin/bash
# ubuntu_install_db.sh
init(){
 apt install -y make cmake gcc g++ perl bison libaio-dev libncurses5 libncurses5-dev libnuma-dev
 groupadd mysql
 useradd -r -g mysql mysql
 tar zxvf $1.tar.gz;sleep 3
 mkdir -p /usr/local/boost
}

install(){
 echo $2;sleep 3
 cd $1
 mkdir -p $2/data
 mkdir -p $2/conf
 mkdir -p $2/pid
 mkdir -p $2/socket
 chown mysql:mysql $2/data
 mv /etc/my.cnf /etc/my.cnf_old
 cmake . -DCMAKE_INSTALL_PREFIX=$2 -DMYSQL_DATADIR=$2/data -DSYSCONFDIR=$2/conf -DDOWNLOAD_BOOST=1 -DWITH_BOOST=/usr/local/boost
 make -j `grep processor /proc/cpuinfo | wc -l` && make -j `grep processor /proc/cpuinfo |wc -l` install && echo "$1 install successful!"
 $2/bin/mysqld --datadir="$2/data" --basedir="$2" --initialize --user=mysql
 chown -R mysql.mysql $2
}


case  $1 in
 "init")
 init $2 && install $2 $3 $4 || exit 1
 ;;
 "install")
 install $2 $3 $4
 ;;
 *)
 echo "error!!!!"
 exit 1
 ;;
esac
~~~

### Centos

~~~bash
wget http://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-5.7.10.tar.gz
bash db_install.sh init mysql-5.7.10 /data/mysql_3307 3307
#!/bin/bash
#db_install.sh
init(){
 yum install -y gcc gcc-c++ ncurses-devel.x86_64 cmake.x86_64 libaio.x86_64 bison.x86_64 gcc-c++.x86_64

 groupadd mysql
 useradd -r -g mysql mysql
 tar zxvf $1.tar.gz;sleep 3
 mkdir -p /usr/local/boost
}

install(){
 echo $2;sleep 3
 cd $1
 mkdir -p $2/data
 mkdir -p $2/conf
 mkdir -p $2/pid
 mkdir -p $2/socket
 chown mysql:mysql $2/data
 mv /etc/my.cnf /etc/my.cnf_old
 cmake . -DCMAKE_INSTALL_PREFIX=$2 -DMYSQL_DATADIR=$2/data -DSYSCONFDIR=$2/conf -DDOWNLOAD_BOOST=1 -DWITH_BOOST=/usr/local/boost
 make -j `grep processor /proc/cpuinfo | wc -l` && make -j `grep processor /proc/cpuinfo |wc -l` install && echo "$1 install successful!"
 $2/bin/mysqld --datadir="$2/data" --basedir="$2" --initialize-insecure --user=mysql
 $2/bin/mysql_ssl_rsa_setup
 chown -R root $2
 chown -R mysql $2/data
 cp $2/support-files/mysql.server /etc/init.d/mysql_$3
}
case  $1 in
 "init")
 init $2 && install $2 $3 $4 || exit 1
 ;;
 "install")
 install $2 $3 $4
 ;;
 *)
 echo "error!!!!"
 exit 1
 ;;
esac
~~~

编译安装后
![](img/mysql部署init生成.png)

### 部署公共部分(数据库)

~~~bash
cp /data/mysql_3306/conf/my.cnf /data/mysql_3010/conf
sed "s/3306/3010/g" /data/mysql_3010/conf/my.cnf
cd /data/mysql_3010/bin && nohup ./mysqld &
mysql -S -uroot /data/mysql_3306/socket/mysql.sock
SET PASSWORD = PASSWORD('your_new_password');
grant all privileges on *.* to root@'%' identified by "adminadmin";
flush privileges;
~~~

### DCL(数据库控制)

#### 赋予相关权限

~~~
grant select,delete,update,insert on exDb.* to superboy@'localhost' identified by 'your_password';
flush privileges;
~~~

#### 赋予exDb库所有权限

~~~
grant all privileges on exDb.* to superboy@localhost identified by 'your_password';
flush privileges;
~~~

#### 撤销某种权限

~~~
revoke update on exDb.* from superboy@localhost;
~~~

#### 撤销所有权限

~~~
revoke all on exDb.* from superboy@localhost;
~~~

#### 注意：检查现有`版本号`是否还存在,可以换成其他新版本的源码包

# 主从复制

## 基本概念

MySQL 主从复制是一个过程，允许将一个 MySQL 实例（称为主服务器）的数据自动复制到一个或多个 MySQL 实例（称为从服务器）

## 复制的目的

* 提高数据的可用性
* 实现读写分离、提高性能
* 数据备份
* 数据分析和报表生成

## 复制原理

**1. 复制的主要线程**

* Binlog dump 线程（主服务器）
* I/O线程（从服务器）
* SQL线程（从服务器）

**2. 复制的过程**

* 主服务器将更改记录到二进制日志（binary log）中
* 从服务器的I/O线程连接到主服务器，请求二进制事件
* 主服务器的Binlog dump线程都去二进制日志，发送事件给从服务器
* 从服务器的接收事件并写入到中继日志（relay log）中
* 从服务器的SQL线程读取中继日志并在从服务器上执行事件

## 复制的类型

### MySQL基于SQL语句的主从复制详解

### 1. 概述

基于SQL语句的复制（Statement-Based Replication, SBR）是MySQL中最早实现的复制方式。在这种模式下，主服务器将执行的SQL语句写入二进制日志（binary log），从服务器则读取并重新执行这些SQL语句。

### 2. 工作原理

1. 主服务器执行SQL语句。
2. 主服务器将SQL语句写入二进制日志。
3. 从服务器的I/O线程读取二进制日志中的SQL语句。
4. 从服务器将SQL语句写入中继日志（relay log）。
5. 从服务器的SQL线程读取中继日志中的SQL语句并执行。

### 3. 优点

1. **日志量小**：只记录SQL语句，而不是具体的数据变化，因此二进制日志的大小通常较小。
2. **易于理解和调试**：可以直接查看二进制日志中的SQL语句。
3. **支持所有存储引擎**：不依赖于特定的存储引擎实现。

### 4. 缺点

1. **可能导致主从不一致**：某些函数（如RAND()、UUID()）在主从服务器上可能产生不同的结果。
2. **不支持不确定的语句**：例如使用LIMIT的语句在没有ORDER BY的情况下可能导致不一致。
3. **对于大量行的DML语句，可能产生较大的日志量**。

### 5. 适用场景

- 主要执行确定性的SQL语句的应用。
- 需要复制存储过程、触发器、自定义函数等的场景。
- 对二进制日志大小敏感的环境。

### 6. 配置步骤

#### 主服务器配置

1. 编辑my.cnf文件：

```ini
[mysqld]
server-id = 1
log-bin = mysql-bin
binlog-format = STATEMENT
```

2. 重启MySQL服务。

3. 创建复制用户：

```sql
CREATE USER 'repl'@'%' IDENTIFIED BY 'password';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
```

#### 从服务器配置

1. 编辑my.cnf文件：

```ini
[mysqld]
server-id = 2
relay-log = mysql-relay-bin
```

2. 重启MySQL服务。

3. 设置复制：

```sql
CHANGE MASTER TO
  MASTER_HOST='主服务器IP',
  MASTER_USER='repl',
  MASTER_PASSWORD='password',
  MASTER_LOG_FILE='mysql-bin.000001',
  MASTER_LOG_POS=0;

START SLAVE;
```

## 7. 注意事项

1. **确保主从服务器的初始数据一致**。
2. **避免使用不确定的函数或语句**，如RAND()、UUID()等。
3. **使用--skip-slave-start选项启动从服务器**，以便在启动复制前进行必要的配置。
4. **定期检查复制状态**：

```sql
SHOW SLAVE STATUS\G
```

5. **设置适当的复制过滤器**，以避免不必要的数据复制。

## 8. 故障排除

1. **复制延迟**：检查网络连接、主服务器负载、从服务器性能等。
2. **主从不一致**：使用pt-table-checksum等工具定期检查数据一致性。
3. **复制错误**：查看从服务器错误日志，解决SQL执行错误。

## 9. 最佳实践

1. 在测试环境中验证复制设置。
2. 使用semi-synchronous replication提高数据安全性。
3. 监控复制延迟和错误。
4. 定期备份从服务器。
5. 考虑使用GTID（全局事务标识符）简化复制管理（MySQL 5.6+）。

## 结论

基于SQL语句的复制是MySQL中一种重要的复制方式，适用于许多场景。虽然它有一些局限性，但在正确使用和配置的情况下，可以提供高效和可靠的数据复制。在选择使用SBR时，需要充分考虑应用程序的特性和数据一致性需求。

#### MySQL基于行的主从复制详解

## 1. 概述

基于行的复制（Row-Based Replication, RBR）是MySQL 5.1版本引入的一种复制方式。在这种模式下，主服务器记录每行数据的变化，而不是记录SQL语句。

## 2. 工作原理

1. 主服务器执行修改数据的操作。
2. 主服务器将受影响的行的变化写入二进制日志。
3. 从服务器的I/O线程读取二进制日志中的行变化。
4. 从服务器将这些变化写入中继日志（relay log）。
5. 从服务器的SQL线程读取中继日志中的行变化并应用。

## 3. 优点

1. **更高的数据一致性**：直接复制数据变化，避免了SQL语句执行可能导致的不一致。
2. **支持所有SQL语句**：不受特定SQL语句限制，如不确定函数（RAND(), UUID()等）。
3. **更少的锁定**：对于大型表的修改，只锁定实际变化的行。
4. **更易于进行点对点复制**：因为记录的是数据变化而不是SQL语句。

## 4. 缺点

1. **二进制日志可能变得很大**：特别是在大量行被修改的情况下。
2. **无法直接查看执行的SQL语句**：调试可能变得更困难。
3. **复制某些操作可能需要更多网络带宽**：因为记录的是完整的行数据。

## 5. 适用场景

* 需要高度数据一致性的应用。
* 使用了大量不确定函数或复杂SQL的场景。
* 执行大量的DML操作但只影响少量行的应用。
* 对数据安全性要求较高的环境。

## 6. 配置步骤

#### 主服务器配置

1. 编辑my.cnf文件：

```ini
[mysqld]
server-id = 1
log-bin = mysql-bin
binlog-format = ROW
```

2. 重启MySQL服务。

3. 创建复制用户：

```sql
CREATE USER 'repl'@'%' IDENTIFIED BY 'password';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
```

#### 从服务器配置

1. 编辑my.cnf文件：

```ini
[mysqld]
server-id = 2
relay-log = mysql-relay-bin
```

2. 重启MySQL服务。

3. 设置复制：

```sql
CHANGE MASTER TO
  MASTER_HOST='主服务器IP',
  MASTER_USER='repl',
  MASTER_PASSWORD='password',
  MASTER_LOG_FILE='mysql-bin.000001',
  MASTER_LOG_POS=0;

START SLAVE;
```

## 7. 注意事项

1. **监控二进制日志大小**：RBR可能产生大量日志，需要适当管理磁盘空间。
2. **网络带宽考虑**：确保网络能够支持可能增加的数据传输量。
3. **使用 `binlog_row_image` 参数优化**：可以设置为 'minimal' 减少日志大小。
4. **考虑使用压缩**：如果网络带宽是瓶颈，可以启用复制压缩（MySQL 5.6+）。

## 8. 故障排除

1. **复制延迟**：检查网络带宽、磁盘I/O性能、从服务器负载等。
2. **数据不一致**：虽然概率较小，但仍需定期进行一致性检查。
3. **日志空间不足**：监控并及时清理旧的二进制日志。

## 9. 最佳实践

1. 使用 `mysqlbinlog` 工具查看二进制日志内容进行调试。
2. 定期进行主从一致性检查，可以使用工具如 pt-table-checksum。
3. 配置适当的复制过滤器，避免复制不必要的数据。
4. 考虑使用延迟复制作为数据恢复的安全网。
5. 在高写入负载的环境中，考虑使用多线程复制（MySQL 5.6+）。

## 10. 与其他复制模式的比较

1. **vs 基于语句的复制（SBR）**：
   * RBR提供更好的一致性，但可能产生更大的日志量。
   * RBR支持所有SQL操作，而SBR对某些操作可能导致不一致。

2. **vs 混合复制（MBR）**：
   * MBR尝试结合RBR和SBR的优点，动态选择复制模式。
   * RBR提供更一致的行为和更简单的配置。

## 结论

基于行的复制为MySQL提供了更高的数据一致性和复制可靠性。虽然它可能在某些情况下增加存储和网络带宽的使用，但对于需要严格数据完整性的应用来说，这通常是一个很好的选择。在选择使用RBR时，需要权衡数据一致性需求与系统资源使用。

**3. 混合复制**

## 复制模式

## 基于GTID复制
MySQL 基于 GTID 的复制是一种高级的复制方式，相比传统的基于二进制日志位置的复制，它提供了更多的优势。以下是 MySQL 基于 GTID 复制的关键点：

1. 工作原理：
   - 每个事务被赋予一个全局唯一的标识符（GTID）
   - 复制时，从服务器请求主服务器上尚未执行的事务

2. 配置步骤：
   a. 在主从服务器的 my.cnf 中启用 GTID：
      ```
      gtid_mode=ON
      enforce_gtid_consistency=ON
      ```
   b. 重启 MySQL 服务
   c. 在从服务器上配置复制：
      ```sql
      CHANGE MASTER TO 
      MASTER_HOST='主服务器IP',
      MASTER_USER='复制用户',
      MASTER_PASSWORD='密码',
      MASTER_AUTO_POSITION=1;
      ```

3. 优势：
   - 简化复制配置和故障转移
   - 提高数据一致性
   - 易于进行点对点复制和多源复制

4. 注意事项：
   - 所有服务器必须启用 GTID
   - 某些操作在 GTID 模式下受限

5. 监控和管理：
   - 使用 `SHOW MASTER STATUS` 和 `SHOW SLAVE STATUS` 查看 GTID 信息
   - `RESET MASTER` 和 `RESET SLAVE` 命令会影响 GTID 执行状态