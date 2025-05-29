#!/bin/bash
#this script is used to get tcp and udp connetion status
#tcp status
# zabbix监控TCP状态监控脚本
# 用法 UserParameter=tcp.status[*],/usr/local/zabbix-agent/scripts/tcp_conn_status.sh $1
# 版本 1 
metric=$1
tmp_file=
/tmp/tcp_status.txt
/bin/netstat -an|awk '/^tcp/{++S[$NF]}END{for(a in S) print a,S[a]}' > $tmp_file

case $metric in
    closed)
        output=$(awk '/CLOSED/{print $2}' $tmp_file)
        if [ "$output" == "" ];then
            echo 0
        else
            echo $output
        fi
    ;;
    listen)
        output=$(awk '/LISTEN/{print $2}' $tmp_file)
        if [ "$output" == "" ];then
            echo 0
        else
            echo $output
        fi
    ;;
    synrecv)
        output=$(awk '/SYN_RECV/{print $2}' $tmp_file)
        if [ "$output" == "" ];then
            echo 0
        else
            echo $output
        fi
    ;;
    synsent)
        output=$(awk '/SYN_SENT/{print $2}' $tmp_file)
        if [ "$output" == "" ];then
            echo 0
        else
            echo $output
        fi
    ;;
    established)
        output=$(awk '/ESTABLISHED/{print $2}' $tmp_file)
        if [ "$output" == "" ];then
            echo 0
        else
            echo $output
        fi
    ;;
    timewait)
        output=$(awk '/TIME_WAIT/{print $2}' $tmp_file)
        if [ "$output" == "" ];then
            echo 0
        else
            echo $output
        fi
    ;;
    closing)
        output=$(awk '/CLOSING/{print $2}' $tmp_file)
        if [ "$output" == "" ];then
            echo 0
        else
            echo $output
        fi
    ;;
    closewait)
        output=$(awk '/CLOSE_WAIT/{print $2}' $tmp_file)
        if [ "$output" == "" ];then
            echo 0
        else
            echo $output
        fi
    ;;
    lastack)
        output=$(awk '/LAST_ACK/{print $2}' $tmp_file)
        if [ "$output" == "" ];then
            echo 0
        else
            echo $output
        fi
    ;;
    finwait1)
        output=$(awk '/FIN_WAIT1/{print $2}' $tmp_file)
        if [ "$output" == "" ];then
            echo 0
        else
            echo $output
        fi
    ;;
    finwait2)
        output=$(awk '/FIN_WAIT2/{print $2}' $tmp_file)
        if [ "$output" == "" ];then
            echo 0
        else
            echo $output
        fi
    ;;
    *)
        echo -e "\e[033mUsage: bash $0 [closed|closing|closewait|synrecv|synsent|finwait1|finwait2|listen|established|lastack|timewait]\e[0m" 
esac


# #!/bin/bash
# #scripts for tcp status 
# # 版本 2 
# function SYNRECV { 
# /usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'SYN-RECV' | awk '{print $2}'
# } 
# function ESTAB { 
# /usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'ESTAB' | awk '{print $2}'
# } 
# function FINWAIT1 { 
# /usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'FIN-WAIT-1' | awk '{print $2}'
# } 
# function FINWAIT2 { 
# /usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'FIN-WAIT-2' | awk '{print $2}'
# } 
# function TIMEWAIT { 
# /usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'TIME-WAIT' | awk '{print $2}'
# } 
# function LASTACK { 
# /usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'LAST-ACK' | awk '{print $2}'
# } 
# function LISTEN { 
# /usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'LISTEN' | awk '{print $2}'
# } 
# function CLOSED { 
# /usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'CLOSED' | awk '{print $2}'
# } 
# function SYN_SENT { 
# /usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'SYN_SENT' | awk '{print $2}'
# } 
# function CLOSE_WAIT { 
# /usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'CLOSE_WAIT' | awk '{print $2}'
# } 
# function CLOSING { 
# /usr/sbin/ss -ant | awk '{++s[$1]} END {for(k in s) print k,s[k]}' | grep 'CLOSING' | awk '{print $2}'
# } 
# case $1 in
#    SYNRECV)
#           SYNRECV
#         ;;
#   ESTAB)
#          ESTAB
#         ;;
#   FINWAIT1)
#           FINWAIT1
#         ;;
#   FINWAIT2)
#           FINWAIT2
#         ;;
#   TIMEWAIT)
#           TIMEWAIT
#         ;;
#   LASTACK)
#           LASTACK
#         ;;
#   LISTEN)
#          LISTEN
#         ;;
#   CLOSED)
#          CLOSED
#         ;;
#   SYN_SENT)
#          SYN_SENT
#         ;;
#   CLOSE_WAIT)
#          CLOSE_WAIT
#         ;;
#   CLOSING)
#          CLOSING
#         ;;
#        *)
#           exit 1
#         ;;
# esac