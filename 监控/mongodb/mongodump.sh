#! /bin/bash
# 导数据脚本

user=admin
password="adminHjrvBFoFMXxl"
host="127.0.0.1:27117"
mongoPath=$(which mongo)
# 昨天
yesterday=$(date +"%Y-%m-%d" -d "-1 days")
# 前天
thedaybefore=$(date +"%Y-%m-%d" -d "-2 days")
# 14天前
deleteDay=$(date +"%Y-%m-%d" -d "-14 days")

# 导出条件
condition="{logDate: {\$gte: ISODate(\"${thedaybefore}T16:00:00.399+0000\"),\$lte: ISODate(\"${yesterday}T16:00:00.399+0000\")}}"
# 删除条件
delCondition="{logDate: {\$lt: ISODate(\"${deleteDay}T16:00:00.399+0000\")}}"

# ------------------------------------ 一部
firstM="mongodump --host 61.14.254.82:13327  -u mongoexport -p u6DMzAgXPiDSKSIRadfkCGD -d log -c"
firstR="mongorestore --host 127.0.0.1:27117 -u admin  -p adminHjrvBFoFMXxl --authenticationDatabase admin -d log1 -c"
# ------------------------------------ 二部
secondM="mongodump --host 103.41.107.155:27017 -u mongoexport -p 6DMzAgXPiwRiDgqo14kC9 -d log -c"
secondR="mongorestore --host 127.0.0.1:27117 -u admin -p adminHjrvBFoFMXxl --authenticationDatabase admin -d log2 -c"
# ------------------------------------ 三部
thirdM="mongodump --host 203.95.192.102:37117 -u mongoexport  -p FSJSierkeMzAgXPiwRiDg -d log -c"
thirdR="mongorestore --host 127.0.0.1:27117 -u admin -p adminHjrvBFoFMXxl --authenticationDatabase admin -d log3 -c"


# 表名
tables=(
    'game'
    'recharge'
    'transfer'
    'moneyChange'
    'withdraw'
)
# 部门
platform=(
    'firstM firstR'
    'secondM secondR'
    'thirdM thirdR'
)
logname=""
platname=""

echo "" > /tmp/export.log
 echo -e "\033[31m ********** 导出时间: $(date)  \033[0m" 

for p in ${!platform[*]}
do
    eval pm="$(echo ${platform[p]} | awk '{print $1}')"
    eval pr="$(echo ${platform[p]} | awk '{print $2}')"
    case $pr in 
    firstR)
        logname="log1"
        platname="first"
        ;;
    secondR)
        logname="log2"
        platname="second"
        ;;
    thirdR)
        logname="log3"
        platname="third"
        ;;
    esac
    for t in ${tables[@]}
    do
        eval a=$(echo \$$pm)
        eval b=$(echo \$$pr)
        backDir=${yesterday}_$pm
        mkdir ${backDir}
        # 备份数据
        echo -e "\033[32m -------- 导出数据 \033[0m" 
        echo -e "\033[35m 部门:${platname} 表名:$t   \033[0m"
        echo -e "\033[35m 导出语句: $a $t -q '${condition}' -o ${backDir}   \033[0m"
        $a $t -q "${condition}" -o ${backDir}
        # 备份还原到临时数据库
        echo -e "\033[32m -------- 导入数据 \033[0m" 
        echo -e "\033[35m 部门:${platname} 库名称: ${logname} 表名:$t   \033[0m"
        echo -e "\033[35m 导入语句: $b $t ${backDir}/log/$t.bson   \033[0m"
        $b $t ${backDir}/log/$t.bson
        # 删除指定日期数据(14天前)
        # sql="db.getSiblingDB(\"$logname\").getCollection(\"$t\").remove(${delCondition})"
        # echo -e "\033[35m 删除14天前的数据: " $sql  "\033[0m"
        # echo $sql | ${mongoPath} --host $host -u $user -p "$password" --shell
         rm -r ${backDir}
    done
done