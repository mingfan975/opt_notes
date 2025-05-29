#! /bin/bash 
#es-index-clear
LAST_DATE=$(date -d "-7 days" "+%Y.%m.%d")
curl -u 'elastic':'qKToUfYdhVvoxYJOXmwS'  -XDELETE 'http://localhost:9200/*-'${LAST_DATE}'*'