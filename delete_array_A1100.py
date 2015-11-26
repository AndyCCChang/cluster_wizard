#!/usr/bin/env python
import os, sys
import json
import StringIO
#from ConfigParser import SafeConfigParser
from ezs3.defaults import BigTeraDefaultSettings as defaults
import logging
from ezs3.log import EZLog
from ezs3.command import do_cmd
from ezs3.log import EZLog
from ezs3.utils import * #define logger
from local_network_config_class import *
from cluster_wizard import *


#logger = EZLog.get_logger(__name__)
def rescan_multipath():
    sg = do_cmd("lsscsi -g |grep /dev/sg | grep Promise |awk  '{ print $8}' | cut -c6-8")
    host = do_cmd("ls -l /sys/class/fc_host | grep host | awk '{print $9}'")
    #print s
    sg_l = []
    host_l = []
    host_l.append(host.splitlines()[0])
    host_l.append(host.splitlines()[1])
    sg_l.append(sg.splitlines()[0])
    sg_l.append(sg.splitlines()[1])
    print "echo \"1\" > /sys/class/scsi_generic/sgx/device/delete"
    for l in sg_l:
        do_cmd("echo \"1\" > /sys/class/scsi_generic/{}/device/delete".format(l))
    print "echo \"- - -\" > /sys/class/scsi_host/hostx/scan"
    for k in host_l:
       do_cmd("echo \"- - -\" > /sys/class/scsi_host/{}/scan".format(k))

if __name__ == "__main__":
#    print "destroying node"
#    do_cmd("./destroy_node")
#    print "deleting storage volume"
#    do_cmd("echo \"[]\" > /etc/ezs3/storage.conf ")
#    print "deleting license file"
#    do_cmd("rm /etc/ezs3/license")
#    print "destroying node"
    print "destroying RAID"
    do_cmd("multipath -F")
    do_cmd("cliib -u admin -p password -C array -a del -d 0")
    rescan_multipath()
    print "rescan_multipath done"
