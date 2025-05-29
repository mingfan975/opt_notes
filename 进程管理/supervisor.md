
# 1. 使用supervisor管理进程

## 1.1. 简介
supervisor是一个用python编写的进程管理工具，可用于进程的启动、关闭、重启， 可作用于但进程和多进程。

## 1.2. 安装
```bash
# 安装python环境
sudo apt-get install python python-pip
# 安装supervisor
sudo pip install supervisor 或 sudo easy-install supervisor
# Ubuntu系统也可以使用apt-get安装
sudo apt-get install supervisor
```
## 1.3. 启动顺序
```bash
supervisord                                   #默认去找$CWD/supervisord.conf，也就是当前目录
supervisord                                   #默认$CWD/etc/supervisord.conf，也就当前目录下的etc目录
supervisord                                   #默认去找/etc/supervisord.conf的配置文件
supervisord -c /home/supervisord.conf         #到指定路径下去找配置文件
```
## 1.4. supervisor 配置
安装完成之后可以使用echo_supervisord_conf 查看supervisor的默认配置,echo_supervisord_conf 重定向到指定的配置文件位置,如:
```bash
$ echo_supervisord_conf >> /data/config/supervisor/supervisor.conf
```

> cat /data/config/supervisor/supervisor.conf
```conf
; Sample supervisor config file.
;
; For more information on the config file, please see:
; http://supervisord.org/configuration.html
;
; Notes:
;  - Shell expansion ("~" or "$HOME") is not supported.  Environment
;    variables can be expanded using this syntax: "%(ENV_HOME)s".
;  - Quotes around values are not supported, except in the case of
;    the environment= options as shown below.
;  - Comments must have a leading space: "a=b ;comment" not "a=b;comment".
;  - Command will be truncated if it looks like a config file comment, e.g.
;    "command=bash -c 'foo ; bar'" will truncate to "command=bash -c 'foo ".
;
; Warning:
;  Paths throughout this example file use /tmp because it is available on most
;  systems.  You will likely need to change these to locations more appropriate
;  for your system.  Some systems periodically delete older files in /tmp.
;  Notably, if the socket file defined in the [unix_http_server] section below
;  is deleted, supervisorctl will be unable to connect to supervisord.

[unix_http_server]
file=/tmp/supervisor.sock   ; the path to the socket file    UNIX socket 文件 如果不设置的话，supervisorctl也就不能用
;chmod=0700                 ; socket file mode (default 0700) socket文件的权限, 默认是0700
;chown=nobody:nogroup       ; socket file uid:gid owner      socket文件的属组，格式uid:gid
;username=user              ; default is no username (open server) 使用supervisorctl链接的时候, 管理用户名
;password=123               ; default is no password (open server)  使用supervisorctl链接的时候, 管理用户密码

; Security Warning:
;  The inet HTTP server is not enabled by default.  The inet HTTP server is
;  enabled by uncommenting the [inet_http_server] section below.  The inet
;  HTTP server is intended for use within a trusted environment only.  It
;  should only be bound to localhost or only accessible from within an
;  isolated, trusted network.  The inet HTTP server does not support any
;  form of encryption.  The inet HTTP server does not use authentication
;  by default (see the username= and password= options to add authentication).
;  Never expose the inet HTTP server to the public internet.

;[inet_http_server]         ; inet (TCP) server disabled by default   http服务器，提供web管理界面
;port=127.0.0.1:9001        ; ip_address:port specifier, *:port for all iface  web管理后台运行的ip和端口,侦听所有IP用 :9001或*:9001
;username=user              ; default is no username (open server)  登陆管理后台的用户名
;password=123               ; default is no password (open server)  管理后台登陆用户的密码

[supervisord]
logfile=/tmp/supervisord.log ; main log file; default $CWD/supervisord.log   日志文件
logfile_maxbytes=50MB        ; max main logfile bytes b4 rotation; default 50MB  日志文件大小，会生成一个新的日志文件。当设置为0时，表示不限制文件大小默认是50M
logfile_backups=10           ;  of main logfile backups; 0 means none, default 10  日志文件保留备份数量,当设置为0时，表示不限制文件大小; 默认10
loglevel=info                ; log level; default info; others: debug,warn,trace 日志级别，默认 info，其它: debug,warn,trace
pidfile=/tmp/supervisord.pid ; supervisord pidfile; default supervisord.pid pid 文件
nodaemon=false               ; start in foreground if true; default false  是否在前台启动，默认是 false，即以 daemon 的方式启动
minfds=1024                  ; min. avail startup file descriptors; default 1024 这个是最少系统空闲的文件描述符，低于这个值supervisor将不会启动。统的文件描述符在这里设置cat /proc/sys/fs/file-max 默认情况下为1024
minprocs=10022                ; min. avail process descriptors;default 200  最小可用的进程描述符，低于这个值supervisor也将不会正常启动，默认 200; ulimit  -u这个命令，可以查看linux下面用户的最大进程数
;umask=022                   ; process file creation umask; default 022  进程创建文件的掩码 默认是022
;user=supervisord            ; setuid to this UNIX account at startup; recommended if root 程这个参数可以设置一个非root用户
;identifier=supervisor       ; supervisord identifier, default is 'supervisor'    supervisord的标识符，主要是给XML_RPC用的。当你有多个supervisor的时候，而且想调用XML_RPC统一管理，就需要为每个supervisor设置不同的标识符
;directory=/tmp              ; default is not to cd during start 设置这个参数的话，启动 supervisord进程之前，会先切换到这个目录
;nocleanup=true              ; don't clean up tempfiles at start; default false 这个参数当为false的时候，会在supervisord进程启动的时候，把以前子进程 产生的日志文件(路径为AUTO的情况下)清除掉。有时候咱们想要看历史日志，当然不想日志被清除了。所以可以设置为true
;childlogdir=/tmp            ; 'AUTO' child log dir, default $TEMP 当子进程日志路径为AUTO的时候，子进程日志文件的存放路径
;environment=KEY="value"     ; key value pairs to add to environment 这个是用来设置环境变量的，supervisord在linux中启动默认继承了linux的 环境变量，在这里可以设置supervisord进程特有的其他环境变量。
;strip_ansi=false            ; strip ansi escape codes in logs; def. false这个选项如果设置为true，会清除子进程日志中的所有ANSI（\n \t）序列

; The rpcinterface:supervisor section must remain in the config file for
; RPC (supervisorctl/web interface) to work.  Additional interfaces may be
; added by defining them in separate [rpcinterface:x] sections.

[rpcinterface:supervisor] ;这个选项是给XML_RPC用的，当然你如果想使用supervisord或者web server 这个选项必须要开启的
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

; The supervisorctl section configures how supervisorctl will connect to
; supervisord.  configure it match the settings in either the unix_http_server
; or inet_http_server section.

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock ; use a unix:// URL  for a unix socket 这个是supervisorctl本地连接supervisord的时候，本地UNIX socket路径，注意这个是和前面的[unix_http_server]对应的, 默认值就是unix:///tmp/supervisor.sock
;serverurl=http://127.0.0.1:9001 ; use an http:// url to specify an inet socket 这个是supervisorctl远程连接supervisord的时候，用到的TCP socket路径注意这个和前面的[inet_http_server]对应
;username=chris              ; should be same as in [*_http_server] if set 用户名
;password=123                ; should be same as in [*_http_server] if set  密码
;prompt=mysupervisor         ; cmd line prompt (default "supervisor")  输入用户名密码时候的提示符
;history_file=~/.sc_history  ; use readline history if available  这个参数和shell中的history类似，我们可以用上下键来查找前面执行过的命令，默认是no file的

; The sample program section below shows all possible program subsection values.
; Create one or more 'real' program: sections to be able to control them under
; supervisor.

;[program:theprogramname] 管理子进程配置，":"后面的是名字最好和实际跑的程序相关，一个program就是就是一个要被管理的进程
;command=/bin/cat              ; the program (relative uses PATH, can take args) 这个就是我们的要启动进程的命令路径了，可以带参数，注意启动的进程不能是守护进程
;process_name=%(program_name)s ; process_name expr (default %(program_name)s) 进程名，如果下面的numprocs参数为1的话，就不用管这个参数了，默认值就是管理组中设置的进程名字
;numprocs=1                    ; number of processes copies to start (def 1) 启动进程的数目
;directory=/tmp                ; directory to cwd to before exec (def no cwd) 进程运行前，会前切换到这个目录
;umask=022                     ; umask for process (default None) 进程掩码，默认none
;priority=999                  ; the relative start priority (default 999) 子进程启动关闭优先级，优先级低的，最先启动，关闭的时候最后关 默认是999
;autostart=true                ; start at supervisord start (default: true) 如果是true的话，子进程将在supervisord启动后被自动启动
;startsecs=1                   ; # of secs prog must stay up to be running (def. 1) 子进程启动多少秒之后，此时状态如果是running，则我们认为启动成功，默认为1
;startretries=3                ; max # of serial start failures when starting (default 3)   当进程启动失败后，最大尝试启动的次数 默认3
;autorestart=unexpected        ; when to restart if exited after running (def: unexpected) 这个是设置子进程挂掉后自动重启的情况，有三个选项，false,unexpected和true，如果为false的时候，无论什么情况下，都不会被重新启动，如果为unexpected，只有当进程的退出码不在下面的exitcodes里面定义的退 出码的时候，才会被自动重启。当为true的时候，只要子进程挂掉，将会被无条件的重启
;exitcodes=0                   ; 'expected' exit codes used with autorestart (default 0) 和上面的的autorestart=unexpected对应
;stopsignal=QUIT               ; signal used to kill process (default TERM)    进程停止信号，可以为TERM, HUP, INT, QUIT, KILL, USR1, or USR2等信号
;stopwaitsecs=10               ; max num secs to wait b4 SIGKILL (default 10)我们向子进程发送stopsignal信号后，到系统返回信息给supervisord，所等待的最大时间。 超过这个时间，supervisord会向该子进程发送一个强制kill的信号。 默认10
;stopasgroup=false             ; send stop signal to the UNIX process group (default false)supervisord管理的子进程，这个子进程本身还有子进程。那么我们如果仅仅干掉supervisord的子进程的话，子进程的子进程有可能会变成孤儿进程。所以咱们可以设置可个选项，把整个该子进程的整个进程组都干掉。 设置为true的话，一般killasgroup也会被设置为true。需要注意的是，该选项发送的是stop信号
;killasgroup=false             ; SIGKILL the UNIX process group (def false) 和上面的stopasgroup类似，不过发送的是kill信号
;user=chrism                   ; setuid to this UNIX account to run the program 如果supervisord是root启动，我们在这里设置这个非root用户，可以用来管理该program
;redirect_stderr=true          ; redirect proc stderr to stdout (default false) 如果为true，则stderr的日志会被写入stdout日志文件中
;stdout_logfile=/a/path        ; stdout log path, NONE for none; default AUTO 进程的stdout的日志路径，可以指定路径，AUTO，none等三个选项
;stdout_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB) 日志文件最大大小默认50
;stdout_logfile_backups=10     ; # of stdout logfile backups (0 means none, default 10)
;stdout_capture_maxbytes=1MB   ; number of bytes in 'capturemode' (default 0)
;stdout_events_enabled=false   ; emit events on stdout writes (default false)当设置为ture的时候，当子进程由stdout向文件描述符中写日志的时候，将触发supervisord发送PROCESS_LOG_STDOUT类型的event
;stdout_syslog=false           ; send stdout to syslog with process name (default false)设置stderr写的日志路径，当redirect_stderr=true,这个就不用设置了
;stderr_logfile=/a/path        ; stderr log path, NONE for none; default AUTO
;stderr_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
;stderr_logfile_backups=10     ; # of stderr logfile backups (0 means none, default 10)
;stderr_capture_maxbytes=1MB   ; number of bytes in 'capturemode' (default 0)
;stderr_events_enabled=false   ; emit events on stderr writes (default false)
;stderr_syslog=false           ; send stderr to syslog with process name (default false)
;environment=A="1",B="2"       ; process environment additions (def no adds)
;serverurl=AUTO                ; override serverurl computation (childutils)

; The sample eventlistener section below shows all possible eventlistener
; subsection values.  Create one or more 'real' eventlistener: sections to be
; able to handle event notifications sent by supervisord.

;[eventlistener:theeventlistenername]   订阅supervisord发送的event
;command=/bin/eventlistener    ; the program (relative uses PATH, can take args) listener的可执行文件的路径 
;process_name=%(program_name)s ; process_name expr (default %(program_name)s)
;numprocs=1                    ; number of processes copies to start (def 1)
;events=EVENT                  ; event notif. types to subscribe to (req'd) event事件的类型，也就是说，只有写在这个地方的事件类型。才会被发送
;buffer_size=10                ; event buffer queue size (default 10) 这个是event队列缓存大小
;directory=/tmp                ; directory to cwd to before exec (def no cwd)
;umask=022                     ; umask for process (default None)
;priority=-1                   ; the relative start priority (default -1)
;autostart=true                ; start at supervisord start (default: true)
;startsecs=1                   ; # of secs prog must stay up to be running (def. 1)
;startretries=3                ; max # of serial start failures when starting (default 3)
;autorestart=unexpected        ; autorestart if exited after running (def: unexpected)
;exitcodes=0                   ; 'expected' exit codes used with autorestart (default 0)
;stopsignal=QUIT               ; signal used to kill process (default TERM)
;stopwaitsecs=10               ; max num secs to wait b4 SIGKILL (default 10)
;stopasgroup=false             ; send stop signal to the UNIX process group (default false)
;killasgroup=false             ; SIGKILL the UNIX process group (def false)
;user=chrism                   ; setuid to this UNIX account to run the program
;redirect_stderr=false         ; redirect_stderr=true is not allowed for eventlisteners
;stdout_logfile=/a/path        ; stdout log path, NONE for none; default AUTO
;stdout_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
;stdout_logfile_backups=10     ; # of stdout logfile backups (0 means none, default 10)
;stdout_events_enabled=false   ; emit events on stdout writes (default false)
;stdout_syslog=false           ; send stdout to syslog with process name (default false)
;stderr_logfile=/a/path        ; stderr log path, NONE for none; default AUTO
;stderr_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
;stderr_logfile_backups=10     ; # of stderr logfile backups (0 means none, default 10)
;stderr_events_enabled=false   ; emit events on stderr writes (default false)
;stderr_syslog=false           ; send stderr to syslog with process name (default false)
;environment=A="1",B="2"       ; process environment additions
;serverurl=AUTO                ; override serverurl computation (childutils)

; The sample group section below shows all possible group values.  Create one
; or more 'real' group: sections to create "heterogeneous" process groups.

;[group:thegroupname]
;programs=progname1,progname2  ; each refers to 'x' in [program:x] definitions
;priority=999                  ; the relative start priority (default 999)

; The [include] section can just contain the "files" setting.  This
; setting can list multiple files (separated by whitespace or
; newlines).  It can also contain wildcards.  The filenames are
; interpreted as relative to this file.  Included files *cannot*
; include files themselves.

;[include]
;files = relative/directory/*.ini
```
## 1.5. supervisorctl
1. supervisorctl 是supervisor命令行客户端工具，启动时需要指定与 supervisord 使用同一份配置文件，否则与 supervisord 一样按照顺序查找配置文件
2. 常用选项
```shell
supervisorctl status  # 查看程序状态
supervisorctl stop server  # 关闭server程序
supervisorctl start server  # 启动server程序
supervisorctl restart server # 重启server程序
supervisorctl reread   # 读取有更新的配置文件，不会启动新添加的程序
supervisorctl update   # 重启配置文件修改过的程序
```
# 2. 使用supervisor管理seaweedFS
1. 创建weed所需数据目录
```bash
mkdir -p /data/logs/seaweed/  # 创建日志存放目录
mkdir -p /data/weedTest/fileData  # 创建master数据目录
mkdir -p /data/weedTest/{v01,v02,v03,v04}  # 创建volume目录，根据所需要启动的进程数目来创建 我这里启动的是4个进程 supervisor里面拼接的格式为  -dir=/data/weedTest/v%(process_num)02d
```
2. supervisor配置文件
> cat /data/config/supervisor.conf
```conf
[unix_http_server]
file=/tmp/supervisor.sock
chmod=0700
chown=nobody:nogroup


[inet_http_server]
port=202.60.250.205:9991
username=supervisor
password=z7HZ0jDTMCNIhd5RYEsOa0uNjezk

[supervisord]
logfile=/tmp/supervisord.log
logfile_maxbytes=50MB
logfile_backups=10
loglevel=info
pidfile=/tmp/supervisord.pid
nodaemon=false
minfds=65535
minprocs=65535
;umask=022
user=root
;identifier=supervisor
;directory=/tmp
;nocleanup=true
;childlogdir=/tmp
;environment=KEY="value"
;strip_ansi=false


[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface


[supervisorctl]
serverurl=unix:///tmp/supervisor.sock
serverurl=http://202.60.250.205:9991
;username=chris
;password=123
;prompt=mysupervisor
history_file=~/.sc_history

[include]
files = /data/config/supervisor/conf.d/*.conf

```
2. weed配置文件
> cat /data/config/supervisor/conf.d/weed.conf
```conf
; 启动master
[program:weedmaster]
directory = /usr/bin/   ; 程序启动目录
command = weed master -mdir=/data/weedTest/fileData -port=19333 -defaultReplication="001" -ip=202.60.250.205 ; 启动命令,注意这里不能是守护进程
autostart = true     ; 在 supervisord 启动的时候也自动启动
startsecs = 5        ; 启动 5 秒后没有异常退出，就当作已经正常启动了
autorestart = true   ; 程序异常退出后自动重启
startretries = 3     ; 启动失败自动重试次数，默认是 3
user = root         ; 用哪个用户启动
redirect_stderr = true  ; 把 stderr 重定向到 stdout，默认 false
stdout_logfile_maxbytes = 50MB  ; stdout 日志文件大小，默认 50MB
stdout_logfile_backups = 14    ; stdout 日志文件备份数
; stdout 日志文件，需要注意当指定目录不存在时无法正常启动，所以需要手动创建目录（supervisord 会自动创建日志文件）
stdout_logfile = /data/logs/seaweed/weedMaster.log

; 启动volume
[program:weedvolume]
directory = /usr/bin/   ; 程序启动目录
command = weed volume -dir=/data/weedTest/v%(process_num)02d -max=1000 -mserver=202.60.250.205:19333 -port=90%(process_num)02d -ip="202.60.250.205"  ; 启动命令,注意这里不能是守护进程
process_name=%(program_name)s_%(process_num)02d
autostart = true     ; 在 supervisord 启动的时候也自动启动
startsecs = 5        ; 启动 5 秒后没有异常退出，就当作已经正常启动了
autorestart = true   ; 程序异常退出后自动重启
startretries = 3     ; 启动失败自动重试次数，默认是 3
user = root          ; 用哪个用户启动
redirect_stderr = true  ; 把 stderr 重定向到 stdout，默认 false
stdout_logfile_maxbytes = 50MB  ; stdout 日志文件大小，默认 50MB
stdout_logfile_backups = 14    ; stdout 日志文件备份数
; stdout 日志文件，需要注意当指定目录不存在时无法正常启动，所以需要手动创建目录（supervisord 会自动创建日志文件）
stdout_logfile = /data/logs/seaweed/volume%(process_num)02d.log
numprocs=4
numprocs_start=1

; 启动filer
[program:weedfiler]
directory = /usr/bin/   ; 程序启动目录
command =  weed filer -master=202.60.250.205:19333 -port=144%(process_num)02d  2.60.250.205  defaultReplicaPlacement='001' ; 启动命令,注意这里不能是守护进程
process_name=%(program_name)s_%(process_num)02d
autostart = true     ; 在 supervisord 启动的时候也自动启动
startsecs = 5        ; 启动 5 秒后没有异常退出，就当作已经正常启动了
autorestart = true   ; 程序异常退出后自动重启
startretries = 3     ; 启动失败自动重试次数，默认是 3
user = root         ; 用哪个用户启动
redirect_stderr = true  ; 把 stderr 重定向到 stdout，默认 false
stdout_logfile_maxbytes = 50MB  ; stdout 日志文件大小，默认 50MB
stdout_logfile_backups = 14    ; stdout 日志文件备份数
; stdout 日志文件，需要注意当指定目录不存在时无法正常启动，所以需要手动创建目录（supervisord 会自动创建日志文件）
stdout_logfile = /data/logs/seaweed/fileter%(process_num)02d.log
numprocs=4
numprocs_start=1
```
3. 启动
```bash 
$ supervisord -c /data/config/supervisor/supervisor.conf
# 启动成功之后查看状态如下
$ supervisorctl  status
    weedfiler:weedfiler_01           RUNNING   pid 6606, uptime 0:05:19
    weedfiler:weedfiler_02           RUNNING   pid 6607, uptime 0:05:19
    weedfiler:weedfiler_03           RUNNING   pid 6608, uptime 0:05:19
    weedfiler:weedfiler_04           RUNNING   pid 6605, uptime 0:05:19
    weedmaster                       RUNNING   pid 6659, uptime 0:05:19
    weedvolume:weedvolume_01         RUNNING   pid 6698, uptime 0:05:19
    weedvolume:weedvolume_02         RUNNING   pid 6700, uptime 0:05:19
    weedvolume:weedvolume_03         RUNNING   pid 6699, uptime 0:05:19
    weedvolume:weedvolume_04         RUNNING   pid 6701, uptime 0:05:19
```
4. 后期维护操作
```bash
# 重启
$ supervisorctl restart  weedmaster
$ supervisorctl restart weedfiler:weedfiler_01   # 注意这点是多进程方式
$ supervisorctl stop  weedmaster
```
<!--stackedit_data:
eyJoaXN0b3J5IjpbMjU1ODE4NDldfQ==
-->