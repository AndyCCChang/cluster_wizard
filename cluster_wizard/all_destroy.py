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
    do_cmd("/root/cluster_wizard/destroy_node")
    print "deleting storage volume"
    do_cmd("echo \"[]\" > /etc/ezs3/storage.conf ")
    print "destroying node"