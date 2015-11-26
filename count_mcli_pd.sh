#!/bin/bash

#mcli -l |grep "VD" |awk '{print $1}'|cut -d: -f1
#mcli -t | awk '{ if (NR==4) print $0 }'
mcli -t | grep -o -e "{[^}]*}"
#mcli -l
