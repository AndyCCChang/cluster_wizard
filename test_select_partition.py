#!/usr/bin/env python
import os, sys, parted, argparse
import textwrap
import json
import StringIO
from ezs3.defaults import BigTeraDefaultSettings as defaults
import logging
from ezs3.log import EZLog
from ezs3.command import do_cmd
from ezs3.log import EZLog
from ezs3.utils import * #define logger
from local_network_config_class import *
import socket
from ezs3.searcher import ClusterSearcher
import subprocess
import commands
from ezs3.storage import StorageVolumeManager

class testsp:
    def load_setting(self):
        self.conf = Ezs3CephConfig()
        self.sv_mgr = StorageVolumeManager()
        self.cname = self.conf.get_cluster_name()
        if self.conf.has_option('ezs3', 'partitions json'):
            self._upgrade_cs51_setting()
    def is_invalid_device(self, model):
        logger.debug("device model: {}".format(model))
        # valid device ex: 2226b0001556a79b4: Linux device-mapper (multipath)
        if model.find("device-mapper") == -1:
            return True
        if model.find("multipath") == -1:
            return True

        return False

    def get_dev_path(self):
        s = []
        for dev in parted.getAllDevices():
            name = "{}: {}".format(os.path.basename(dev.path), dev.model)
            size = int(dev.getSize())
            print name, size
            #if not "multipath" in name:
            #    continue
            #print dev.path
            s.append(dev.path)
        return s
    # get all path of dev
    def get_all_dev_path(self):
        self.load_setting()
        choices = []
        hide_device = True
        try:
            do_cmd("dpkg -l|grep multipath")
        except:
            hide_device = False
        #print hide_device
        for dev in parted.getAllDevices():
            if hide_device and self.is_invalid_device(dev.model):
                continue
            if self.sv_mgr.dev_in_use(dev):
                continue
            if hide_device:
                name = "{}: {}".format(dev.path, dev.model);
            else:
                name = "{}: {}".format(dev.path, dev.model)[:30];
            size = "{} MB".format(int(dev.getSize()))
            txt = "{:<28}{:>16}".format(name, size)
            choices.append((txt, dev.path))
            #print partition if has it
            try:
                disk = parted.Disk(dev)
                for p in disk.partitions:
                    if self.sv_mgr.dev_in_use(p):
                        continue
                    if p.type not in [parted.PARTITION_NORMAL,
                                      parted.PARTITION_LOGICAL]:
                        continue

                    name = "    partition {}".format(p.number)
                    size = "{} MB".format(int(p.getSize()))
                    txt = "{:<29}{:>16}".format(name, size)
                    choices.append((txt, dev.path))
            except:
                pass
        return choices
    def main(self):
        self.load_setting()
        storage_vol_name = "s1"
        all_dev_path = self.get_all_dev_path()
        dev_path_list = []
        for p, s in all_dev_path:
            print p
            dev_path_list.append(s)
        print "yy", dev_path_list
        dev_path = raw_input("Please enter a partition for storage volume {}. (e.g., /dev/sdb, or cancel)\n")
        while dev_path not in dev_path_list or not dev_path:
            all_dev_path = self.get_all_dev_path()
            dev_path = raw_input("Please enter a valid partition for storage volume {}. (e.g., /dev/sdb or cancel)\n".format(storage_vol_name))
        #################coninue
            if dev_path == "cancel":
                continue
        print dev_path

if __name__ == "__main__":
    tsp = testsp()
    tsp.main()
