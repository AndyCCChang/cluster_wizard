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



#logger = EZLog.get_logger(__name__)

if __name__ == "__main__":
    print "destroying node"
    do_cmd("./destroy_node")
    print "deleting storage volume"
    do_cmd("echo \"[]\" > /etc/ezs3/storage.conf ")
    print "deleting license file"
    do_cmd("rm /etc/ezs3/license")
    print "destroying node"
    print "destroying RAID"
    do_cmd("cliib -u admin -p password -C array -a del -d 0")
