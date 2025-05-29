#!/bin/bash
# -*- encoding: utf-8 -*-

#白名单服务器地址以及办公室ip,JUMPSERVER_IP你的zabbix_server
JUMPSERVER_IP='192.168.0.10'
ZABBIXSERVER_IP='192.168.0.11'
# VPN_IP=35.241.110.170
VPN_IP="192.168.0.12"
OLD_VPN_IP="192.168.0.13"
WHITE_IP=($VPN_IP $OLD_VPN_IP $JUMPSERVER_IP $ZABBIXSERVER_IP)
SSH_PORT='22'
HOST_NAME='test-123'
INSTALL_PATH='/data'
# nodejs
NODE_VERSION="20"
# mongodb
MONGO_VERSION="6.0"
# 系统信息
OS_VERSION=$(lsb_release -r | awk '{print $2}')
OS_CODENAME=$(lsb_release -c | awk '{print $2}')
# zabbix
ZABBIX_MAIN_VERSION="6.0"
ZBX_VERSION="6.0-4"
# redis
REDIS_VERSION="7.0.6"
REDIS_PORT=6689
# 时间同步服务器
NTP_SERVER="time.windows.com"

function INIT() {
    echo -e "\033[31m 安装基础库和工具... \033[0m"
    apt update && apt install -y make cmake gcc g++ perl bison libaio-dev libncurses5 libncurses5-dev libnuma-dev pkg-config ntpdate cron

    echo -e "\033[31m 时间同步... \033[0m"
    rm -rf /etc/localtime && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
    timedatectl
    cat <<EOF >/var/spool/cron/crontabs/root
*/5 * * * * ntpdate $NTP_SERVER &>/dev/null
EOF
    echo -e "\033[31m 调整系统限制... \033[0m"
    #init ulimit
    cat <<EOF >>/etc/sysctl.conf
fs.file-max = 6553560
EOF
    cat <<EOF >/etc/security/limits.conf
* soft nproc 65535
* hard nproc 65535
* soft nofile 65535
* hard nofile 65535
* hard memlock unlimited
* soft memlock unlimited
EOF
    cat <<EOF >>/etc/profile
ulimit -SHn 65535
ulimit -u 10000
ulimit -d unlimited
ulimit -m unlimited
ulimit -s unlimited
ulimit -t unlimited
ulimit -v unlimited
EOF
    sysctl -p
}

function SET_USER() {
    echo -e "\033[31m 配置wind用户... \033[0m"
    INSTALL_PATH='/data'
    useradd -d /home/wind -m -s /bin/bash wind
    password=$(cat /dev/urandom | tr -dc A-Za-z0-9 | head -c 16)
    echo $password >$INSTALL_PATH/windpasswodfile
    echo wind:$password | chpasswd
    su wind -c 'mkdir -p  /home/wind/.ssh && chmod 700 /home/wind/.ssh'
    chmod 600 /home/wind/.ssh/authorized_keys && chown wind.wind /home/wind/.ssh/authorized_keys
    if [[ ! -d "/root/.ssh" ]]; then
        mkdir -p /root/.ssh && chmod 700 /root/.ssh
    fi
    cat <<EOF >/root/.ssh/authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAAD... jenkins@0ebe56273da3
EOF
    chmod 600 /root/.ssh/authorized_keys

}

function SET_ROOT() {
    echo -e "\033[31m 配置root用户... \033[0m"
    sed -i -e "s/\(PermitRootLogin \).*/\1without-password/g" -e "s/^#\(PasswordAuthentication \).*/\1no/g" -e "s/^#\(Port \).*/\1$SSH_PORT/g" -e "s/^#\(MaxAuthTries \).*/\13/g" /etc/ssh/sshd_config
    for i in ${WHITE_IP[*]}; do
        echo "AllowUsers *@${i%:*}" >>/etc/ssh/sshd_config
    done
    /etc/init.d/ssh restart
}

function SET_ENV() {
    echo -e "\033[31m 环境设置... \033[0m"
    for i in ${WHITE_IP[*]}; do echo "sshd:${i%:*}:allow" >>/etc/hosts.allow; done
    echo "sshd:ALL" >>/etc/hosts.deny
    cat <<EOF >>/etc/profile
#umask 027
HISTFILESIZE=4000
HISTSIZE=4000
USER_IP=who -u am i 2>/dev/null| awk '{print \$NF}'|sed -e 's/[()]//g' #取得登录客户端的IP
if [ -z \$USER_IP ]
then
USER_IP=hostname
fi
HISTTIMEFORMAT="%F %T \$USER_IP:$(whoami) "     #设置新的显示history的格式
export HISTTIMEFORMAT
EOF
    source /etc/profile
    sed -i -e "s/preserve_hostname:.*/preserve_hostname: true/g" /etc/cloud/cloud.cfg
    # sed -i "21i\wind    ALL=(ALL) NOPASSWD: ALL" /etc/sudoers
    sudo apt update
    sudo apt install make gcc ntpdate vim net-tools nload iftop -y

    curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.12.2-amd64.deb
    sudo dpkg -i filebeat-8.12.2-amd64.deb
    apt update && apt install filebeat
    systemctl enable filebeat.service

}

#sudo说明
#user1 ALL=(ALL)  ALL
#我们来说一下这一行的配置的意思
#user1 表示该用户user1可以使用sudo命令，第一个ALL指的是网络中的主机（可以是主机名也可以是ip地址），它指明user1用户可以在此主机上执行后面命令；第二个括号里的ALL是指目标用户，也就是以谁的身份去执行命令。最后一个ALL是指命令路径。
#user1 localhost=(root)  /bin/kill
#表示user1用户可以在本地以root的身份去执行kill命令

#获取外网卡名称
function GET_NET() {
    NIC=($(ls /sys/class/net/ | grep ^e))
    for i in ${NIC[*]}; do
        IP=$(ifconfig $i | grep "inet " | sed -e 's#^ .* ##g')
        if [[ $IP =~ ^192.* ]]; then
            continue
        else
            NETCARD=$i
        fi
    done
}

function SET_IPTABLE() {
    echo -e "\033[31m iptables设置... \033[0m"
    iptables -F
    iptables -X
    iptables -P INPUT DROP
    iptables -P OUTPUT ACCEPT
    iptables -P FORWARD DROP
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A INPUT -p icmp -j ACCEPT
    iptables -A INPUT -p tcp -m tcp --dport 9909 -j ACCEPT
    iptables -A INPUT -p udp -m udp --dport 123 -j ACCEPT
    iptables -A INPUT -s $ZABBIXSERVER_IP -p tcp -m tcp --dport 10050 -j ACCEPT
    iptables -A INPUT -s $JUMPSERVER_IP/32 -j ACCEPT
    iptables -A INPUT -s $VPN_IP/32 -j ACCEPT
    iptables -A INPUT -s $OLD_VPN_IP/32 -j ACCEPT
    iptables -A INPUT -m state --state NEW -p tcp -m multiport --dport $SSH_PORT,22 -j ACCEPT
    iptables -A INPUT -p all -m state --state RELATED,ESTABLISHED -j ACCEPT
    iptables -A INPUT -m state --state INVALID -j DROP
    iptables -A OUTPUT -m state --state INVALID -j DROP

    echo -e "\033[31m 设置开机启动... \033[0m"
    iptables-save >/etc/network/iptables.up.rules
    cat <<EOF >/etc/rc.local
    iptables-restore < /etc/network/iptables.up.rules
EOF
    chmod 755 /etc/rc.local

    cat <<EOF >/lib/systemd/system/rc.local.service
[Unit]
Description=rc.local.service
After=network.target network-online.target syslog.target
Wants=network.target network-online.target

[Service]
Type=simple

#启动服务的命令（命令必须写绝对路径）
ExecStart=bash /etc/rc.local

[Install]
WantedBy=multi-user.target
EOF

    systemctl enable rc.local.service
}

#使用wind用户sudo是NOPASSWORD或者root用户
function INSTALL_NODEJS() {
    echo -e "\033[31m 开始安装nodejs... \033[0m"
    sudo apt-get remove nodejs -y
    sudo apt-get autoremove

    sudo curl -sL https://deb.nodesource.com/setup_$NODE_VERSION.x | sudo -E bash -
    sudo apt-get update && sudo apt-get install -y nodejs && sudo npm i pm2 -g
    sudo chown -R $USER:$(id -gn $USER) /home/$USER/.config
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    node --version
    npm --version
    pm2 --version
    su wind -c 'pm2 install pm2-logrotate && pm2 install pm2-intercom'
    sed -i 's#max_size.*#max_size":"2G",#g' /home/wind/.pm2/module_conf.json
    su wind -c 'pm2 restart pm2-logrotate && pm2 restart pm2-intercom'

}

function INSTALL_MONGO() {
    echo -e "\033[31m 开始安装mongo... \033[0m"
    sudo apt-get remove nodejs -y && sudo autoremove
    wget -qO - https://www.mongodb.org/static/pgp/server-$MONGO_VERSION.asc | sudo apt-key add - &
    sudo echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu $OS_CODENAME/mongodb-org/$MONGO_VERSION multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-$MONGO_VERSION.list &&
        sudo apt-get update && sudo apt-get install -y mongodb-org &&
        sudo echo "mongodb-org hold" | sudo dpkg --set-selections &&
        sudo echo "mongodb-org-server hold" | sudo dpkg --set-selections &&
        sudo echo "mongodb-org-shell hold" | sudo dpkg --set-selections &&
        sudo echo "mongodb-org-mongos hold" | sudo dpkg --set-selections &&
        sudo echo "mongodb-org-tools hold" | sudo dpkg --set-selections
}

function INSTALL_REDIS() {
    echo -e "\033[31m 开始安装redis... \033[0m"
    cd $INSTALL_PATH
    wget http://download.redis.io/releases/redis-$REDIS_VERSION.tar.gz
    sudo tar xzf redis-$REDIS_VERSION.tar.gz
    cd $INSTALL_PATH/redis-$REDIS_VERSION
    sudo make -j 4 # make MALLOC=libc
    sudo cp $INSTALL_PATH/redis-$REDIS_VERSION/src/{redis-server,redis-sentinel,redis-cli} /usr/bin/
    mkdir -p /data/conf/{redis,pm2}
    mkdir -p /data/redis/{logs,redis${REDIS_PORT},run}

    cat <<EOF >/data/conf/redis/redis$REDIS_PORT.conf
bind 0.0.0.0
protected-mode no
port $REDIS_PORT
tcp-backlog 511
unixsocket "/tmp/redis$REDIS_PORT.sock"
unixsocketperm 700
timeout 0
tcp-keepalive 300
################################# GENERAL #####################################
daemonize yes
supervised no
pidfile "/data/redis/run/redis_$REDIS_PORT.pid"
loglevel notice
logfile "/data/redis/logs/redis$REDIS_PORT.log"
databases 16
always-show-logo yes
################################ SNAPSHOTTING  ################################
save ""

stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename "dump$REDIS_PORT.rdb"
dir "/data/redis/redis$REDIS_PORT"
################################# REPLICATION #################################
#从服务器取消下行注释
###slaveof 192.168.12.2 $REDIS_PORT
#masterauth "s3IHoolQTphKdalf"
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-disable-tcp-nodelay no
################################## SECURITY ###################################
requirepass "77s3IHoolQTphKdalf"
#rename-command CONFIG "b840fc02d524045429941cc15f59e41cb7bf6c52"
################################### CLIENTS ####################################
maxclients 10000
############################# LAZY FREEING ####################################
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
############################## APPEND ONLY MODE ###############################
appendonly no
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes
################################ LUA SCRIPTING  ###############################
busy-reply-threshold 5000
############################### 慢日志  ################################
slowlog-log-slower-than 10000
slowlog-max-len 128

############################### 内存使用  ################################
maxmemory 20G
maxmemory-policy allkeys-lru

# Generated by CONFIG REWRITE
latency-tracking-info-percentiles 50 99 99.9


#protected-mode yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes
replica-lazy-flush yes
io-threads-do-reads yes
io-threads 4
zset-max-listpack-entries 128
zset-max-listpack-value 64


############################### 活动碎片整理  ################################
activedefrag no
active-defrag-cycle-min 25
active-defrag-cycle-max 75
active-defrag-ignore-bytes 500mb
active-defrag-threshold-lower 10
EOF

    cat <<EOF >/lib/systemd/system/redis-server.service
[Unit]
Description=Redis server
After=network.target

[Service]
Type=forking
ExecStart=/usr/bin/redis-server /data/conf/redis/redis$REDIS_PORT.conf
ExecStop=/usr/bin/redis-clishutdown
Restart=always
PrivateTmp=true
 
[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl start redis-server.service
    systemctl enable redis-server.service
}

function INSTALL_ZABBIX() {
    echo -e "\033[31m 开始安装zabbix... \033[0m"
    cd $INSTALL_PATH
    wget https://repo.zabbix.com/zabbix/${ZABBIX_MAIN_VERSION}/ubuntu/pool/main/z/zabbix-release/zabbix-release_${ZBX_VERSION}+ubuntu${OS_VERSION}_all.deb
    dpkg -i zabbix-release_${ZBX_VERSION}+ubuntu${OS_VERSION}_all.deb
    apt update && apt install zabbix-agent2 -y

    sudo apt -y install zabbix-agent2
    # sudo sed -i -e 's#^\(Hostname=\).*#\1'"$HOST_NAME"'#g' -e 's#^\(Server=\).*#\1'"$JUMPSERVER_IP"'#g' -e 's#^\(ServerActive=\).*#\1'"$JUMPSERVER_IP"':10051#g' /etc/zabbix/zabbix_agentd.conf
    cat <<EOF >/etc/zabbix/zabbix_agent2.conf
PidFile=/var/run/zabbix/zabbix_agent2.pid
LogFile=/var/log/zabbix/zabbix_agent2.log
LogFileSize=0
Server=$ZABBIXSERVER_IP:10051
ListenPort=10050
ServerActive=$ZABBIXSERVER_IP
Hostname=$(hostname)
Include=/etc/zabbix/zabbix_agent2.d/*.conf
PluginSocket=/run/zabbix/agent.plugin.sock
ControlSocket=/run/zabbix/agent.sock
Include=./zabbix_agent2.d/plugins.d/*.conf
EOF
    sudo systemctl restart zabbix-agent2.service
    sudo systemctl enable zabbix-agent2
}

function WARNING() {
    echo -e "\033[31m 脚本说明... \033[0m"
    echo -e "\033[31m ini初始化用root执行，安装软件就可以用任何用户... \033[0m"
    echo -e "\033[31m ini初始化执行一次就行了请勿重复执行... \033[0m"
    echo -e "\033[31m ini(系统初始化用户设置环境优化防火墙),install-all(安装nodejs,mongo,redis,zabbix)... \033[0m"
    echo -e "\033[31m Usage: $0 ini|reset-wind|reset-root|install-all|nodejs|mongo|redis|zabbix  \033[0m"
    exit 1
}

function main() {
    [ "$#" -ne 1 ] && WARNING
    [ ! -d "$INSTALL_PATH" ] && {
        sudo mkdir $INSTALL_PATH
        sudo chmod o+rwx $INSTALL_PATH
    }
    case $1 in
    "ini")
        INIT
        SET_USER
        SET_ROOT
        SET_ENV
        SET_IPTABLE
        ;;
    "reset-wind")
        echo -e "\033[31m 重置wind用户... \033[0m"
        SET_USER
        ;;
    "reset-root")
        echo -e "\033[31m 重置root用户... \033[0m"
        SET_ROOT
        ;;
    "install-all")
        echo -e "\033[31m 安装常用服务应用... \033[0m"
        INSTALL_NODEJS
        INSTALL_MONGO
        INSTALL_REDIS
        INSTALL_ZABBIX
        ;;
    "nodejs")
        INSTALL_NODEJS
        ;;
    "mongo")
        INSTALL_MONGO
        ;;
    "redis")
        INSTALL_REDIS
        ;;
    "zabbix")
        INSTALL_ZABBIX
        ;;
    *)
        WARNING
        ;;
    esac
}
main $1
