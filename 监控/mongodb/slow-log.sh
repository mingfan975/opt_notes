#!/bin/bash
# 获取数据库慢查询日志

# log file name
filename="mongod37120.log"# path
path="/var/log/mongodb"

# log file
file=${path}"/"${filename}

# offset file
offset='/tmp/OffSet.txt'

# 上次最后一行
old_line_num=$(cat ${offset})

# 本次最后一行
new_line_num=$(cat $file | wc -l)

# 覆盖offset文件
echo $new_line_num > $offset

record=$(sed -n "$old_line_num,${new_line_num}p" $file|awk '/COMMAND/{print $NF" "$0}' |awk -F"ms" '$1>6000{print $0}'|sort  -nrk1)

if test -z "${record}"
   then
        code=0
        msg1="$日志正常"

   else
        code=1
        msg1="$日志异常 ${record}"

fi
echo "{\"value\" : $code, \"info\" : \"$msg1\"}"
exit 0