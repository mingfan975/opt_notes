#!/bin/sh
logs=$(find /data/docker/containers/ -name *-json.log)
for log in $logs
do
    echo "clean logs : $log"
    cat /dev/null > $log
done