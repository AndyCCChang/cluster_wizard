#!/bin/bash

mcli -l |grep "VD" |awk '{print $1}'|cut -d: -f1
#mcli -l
