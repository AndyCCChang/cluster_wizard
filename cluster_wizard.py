#!/usr/bin/env python
import os, sys, parted, argparse
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
class ClusterWizard:
    global A1100_productname
    global A1970_productname
    #A1100_productname = "RS300-E8-RS4"
    def is_connected(self):
        REMOTE_SERVER = "www.google.com"
        try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
            host = socket.gethostbyname(REMOTE_SERVER)
    # connect to the host -- tells us if the host is actually
    # reachable
            s = socket.create_connection((host, 80), 2)
            return True
        except:
            pass
        return False

    def get_productname(self):
        productNamePath = ("/tmp/productname")
        productnameFileExisted = os.path.isfile(productNamePath)
        if productnameFileExisted:
            productname = do_cmd("cat {}".format(productNamePath))
            productname = productname.rstrip()
        else:
            productname = do_cmd("/promise/bin/amidelnx/amidelnx_26_64 /SP | grep SP |grep \"R\"| sed \'s/.*Done   //\'| awk -F\'\"\' \'{print $2}\' ")
            productname = productname.rstrip()
            os.system("echo {} > {}".format(productname, productNamePath))
        return productname
    def set_hostname(self, hostname):
        hostname_path = "/etc/hostname"
        cur_hostname = do_cmd("hostname")
        cur_hostname = cur_hostname.rstrip()
        if hostname:
            if hostname != cur_hostname:
                #set hostname
                do_cmd("hostname {}".format(hostname))
                do_cmd("echo {} > {}".format(hostname, hostname_path))
    def get_hostname(self):
        hostname = do_cmd("hostname")
        hostname = hostname.rstrip()
        return hostname
    def check_trial_license(self):
        licensePath = ("/etc/ezs3/license")
        licenseFileExisted = os.path.isfile(licensePath)
        if licenseFileExisted:
            statinfo = os.stat(licensePath)
            if statinfo.st_size < 5:
                return 0 #license not existed
            else:
                return 1 # license existed
        else:
            return 0 #license not existed
    def activate_trial_license(self):
        is_license = self.check_trial_license()
        if not is_license:
            #print "activate trial0 license"
            do_cmd("activate_license -k CLLT3L-CSKKEY-2B1MWZ-TP2FGO-1BL8ZY-FF0U08-CIWNIA -f trial0")
        else:
            print "License existed"

    def set_RAID(self, productname):	    
        #phdrv_count_A1100 = self.count_phydrv_A1100()
        print "Setting RAID..."
        logger.info("Setting RAID...")
        #if productname == A1100_productname:
        if A1100_productname in productname:
            phdrv_count_A1100 = self.count_phydrv_A1100()
            is_OK_1_array = do_cmd("cliib -u admin -p password -C array -a list |grep -E '0'.*'OK' |  awk '{ print $2}' | head -n 1")
            is_OK_1_spare = do_cmd("cliib -u admin -p password -C spare |grep -E '0'.*'OK' |  awk '{ print $2}' | head -n 1")
            #if is_OK == "OK\n":
            #    print("RAID existed")
            if phdrv_count_A1100 ==16:
                is_OK_1_array = do_cmd("cliib -u admin -p password -C array -a list |grep -E '0'.*'OK' |  awk '{ print $2}' | head -n 1")
                if is_OK_1_array == "OK\n":
                    print("RAID existed")
                else:
                    do_cmd("cliib -u admin -p password -C array -a add -p1~15 -l\\\"raid=5\\\"")
            elif phdrv_count_A1100 ==32:
                if is_OK_1_array == "OK\n":#need to grep and check 2 OK in the future 
                    print("RAID existed")
                else:
                    do_cmd("cliib -u admin -p password -C array -a add -p1~15 -l\\\"raid=5\\\"")                
                    do_cmd("cliib -u admin -p password -C array -a add -p17~31 -l\\\"raid=5\\\"")
            elif  phdrv_count_A1100 ==48:
                if is_OK_1_array == "OK\n":#need to grep and check 3 OK in the future 
                    print("RAID existed")
                else:
                    do_cmd("cliib -u admin -p password -C array -a add -p1~15 -l\\\"raid=5\\\"")                
                    do_cmd("cliib -u admin -p password -C array -a add -p17~31 -l\\\"raid=5\\\"")
                    do_cmd("cliib -u admin -p password -C array -a add -p33~47 -l\\\"raid=5\\\"")
            elif  phdrv_count_A1100 ==64:
                if is_OK_1_array == "OK\n":#need to grep and check 4 OK in the future 
                    print("RAID existed")
                else:
                    do_cmd("cliib -u admin -p password -C array -a add -p1~15 -l\\\"raid=5\\\"")                
                    do_cmd("cliib -u admin -p password -C array -a add -p17~31 -l\\\"raid=5\\\"")
                    do_cmd("cliib -u admin -p password -C array -a add -p33~47 -l\\\"raid=5\\\"")
                    do_cmd("cliib -u admin -p password -C array -a add -p49~63 -l\\\"raid=5\\\"")
            #elif  phdrv_count_A1100 ==13: #test version
            #    if is_OK_1_array == "OK\n":#need to grep and check 4 OK in the future 
            #        print("RAID existed")
            #    else:
            #        do_cmd("cliib -u admin -p password -C array -a add -p5~15 -l\\\"raid=5\\\"")                
            else:
                print("Physical drives are not enough")
                sys.exit(0)
            #spare drive
            if phdrv_count_A1100 ==16:
                is_OK_1_spare = do_cmd("cliib -u admin -p password -C spare |grep -E '0'.*'OK' |  awk '{ print $2}' | head -n 1")
                if is_OK_1_spare == "OK\n":
                    print("Hot spare drive existed")
                else:
                    do_cmd("cliib -u admin -p password -C spare -a add -p 16 -t g -r y")
            elif phdrv_count_A1100 ==32:
                if is_OK_1_spare == "OK\n":#need to grep and check 2 OK in the future
                    print("Hot spare drive existed")
                else:
                    do_cmd("cliib -u admin -p password -C spare -a add -p 16 -t g -r y")
                    do_cmd("cliib -u admin -p password -C spare -a add -p 32 -t g -r y")
            elif phdrv_count_A1100 ==48:
                if is_OK_1_spare == "OK\n":#need to grep and check 3 OK in the future
                    print("Hot spare drive existed")
                else:
                    do_cmd("cliib -u admin -p password -C spare -a add -p 16 -t g -r y")
                    do_cmd("cliib -u admin -p password -C spare -a add -p 32 -t g -r y")
                    do_cmd("cliib -u admin -p password -C spare -a add -p 48 -t g -r y")
            elif phdrv_count_A1100 ==64:
                if is_OK_1_spare == "OK\n":#need to grep and check 4 OK in the future
                    print("Hot spare drive existed")
                else:
                    do_cmd("cliib -u admin -p password -C spare -a add -p 16 -t g -r y")
                    do_cmd("cliib -u admin -p password -C spare -a add -p 32 -t g -r y")
                    do_cmd("cliib -u admin -p password -C spare -a add -p 48 -t g -r y")
                    do_cmd("cliib -u admin -p password -C spare -a add -p 64 -t g -r y")
            #elif phdrv_count_A1100 ==13:#test version
            #    print ("pd = 13")
            #    if is_OK_1_spare == "OK\n":#need to grep and check 4 OK in the future
            #        print("Hot spare drive existed")
            #    else:
            #        do_cmd("cliib -u admin -p password -C spare -a add -p 16 -t g -r y")
            else:
                print("Physical drives are not enough")
                sys.exit(0)
                
        else:#A1970
            is_VD = do_cmd("./check_mcli_array.sh")
            if is_VD == "VD\nVD\nVD\n":
                print("RAID existed")
            else:
                do_cmd("./run_mcli.sh")
        print "Setting RAID done"
        logger.info("Setting RAID done")
    # NO CALLED
    def check_RAID(self, productname):
#        if productname == A1100_productname:
        if A1100_productname in productname:
            is_OK = do_cmd("cliib -u admin -p password -C array -a list |grep -E '0'.*'OK' |  awk '{ print $2}' | head -n 1")
            is_OK2 = do_cmd("cliib -u admin -p password -C spare |grep -E '0'.*'OK' |  awk '{ print $2}' | head -n 1")
            if is_OK == "OK\n" and is_OK2 == "OK\n":
                return 1
            else:
                return 0
        else:#A1970
            is_VD = do_cmd("./check_mcli_array.sh")
            if is_VD == "VD\nVD\nVD\n":
                return 1
            else:
                return 0
#    def set_network(self):
    def create_volume(self):    
        print "creating storage volume..."
        storage_path = "/etc/ezs3/storage.conf"
        storage_path_existed = os.path.isfile(storage_path)
        if not storage_path_existed:
            do_cmd("echo \"[]\" > /etc/ezs3/storage.conf")
        size_storage_file = os.path.getsize('/etc/ezs3/storage.conf')
        #cw = ClusterWizard()#A1100
        #dev_mapper = "222590001553018d6"
        #dev_mapper_path = cw.get_dev_path()
#        if productname == A1100_productname:
        if A1100_productname in productname:
            dev_mapper_path = cw.get_dev_path()
            if (size_storage_file <4):#if /etc/ezs3/storage.conf no storage configuration
                #os.system("/root/cluster_wizard/create_volume -p %s -n %s" %(dev_mapper_path , storage_vol_name))
                i=0
                for dmp in dev_mapper_path:
                    os.system("./create_volume -p {} -n {}{}".format(dmp , storage_vol_name, i))
                    i = i+1
                    print ""
                #os.system("./create_volume -p %s -n %s" %(dev_mapper_path , storage_vol_name))
                #print ""
                print "Creating storage volume done "
            else:
                print "Storage volume exsisted"
        else:#A1970
            dev_mapper_path_A1970 = cw.get_dev_path_A1970()
            if (size_storage_file <4):#if /etc/ezs3/storage.conf no storage configuration
                i=0
                for dmpA in dev_mapper_path_A1970:
                    #do_cmd("/root/cluster_wizard/create_volume -p {} -n {}{}".format(dmpA , storage_vol_name, i))
                    os.system("./create_volume -p {} -n {}{}".format(dmpA , storage_vol_name, i))
                    i = i+1
                    print ""
                print "Creating storage volume done "
            else:
                print "Storage volume exsisted"
    def check_cluster_existed(self):
        enabledRolesFileExisted = os.path.isfile("/etc/ezs3/enabled_roles")
        if enabledRolesFileExisted:
            enabledRoles = do_cmd("cat /etc/ezs3/enabled_roles")
            enabledRoles = enabledRoles.rstrip()
        if enabledRoles == "ezs3 ezgateway" or  enabledRoles == "ezs3":
            return 1
        else: 
            return 0

    def create_cluster(self, cluster_name, replication):
        is_clus_existed = self.check_cluster_existed()
        if is_clus_existed:
            print "Cluster existed"
        else:
            print "Creating a cluster..."
            print "Please wait..."
            #if productname == A1100_productname:
            if A1100_productname in productname:
                os.system("./create_cluster -p bond0 -s bond1 -n {} -r {}".format(cluster_name, replication))
                print ""
            else: #A1970
		os.system("./create_cluster -p bond0 -s bond1 -n {} -r {}".format(cluster_name, replication))
                print ""
                #print "Creating a cluster done"

    def join_cluster(self, join_cluster_name):
        enabledRolesFileExisted = os.path.isfile("/etc/ezs3/enabled_roles")
        if enabledRolesFileExisted:
            enabledRoles = do_cmd("cat /etc/ezs3/enabled_roles")
            enabledRoles = enabledRoles.rstrip()
        if enabledRoles == "ezs3 ezgateway" or  enabledRoles == "ezs3":
            print "cluster existed"
        else:
            print "joining a cluster {}...".format(join_cluster_name)
            #if productname == A1100_productname:
            if A1100_productname in productname:
                #do_cmd("/root/cluster_wizard/join_cluster -p bond0 -s bond1 -n {}").format(join_cluster_name)
                os.system("./join_cluster -p bond0 -s bond1 -n {}".format(join_cluster_name))
                print "joining a cluster {} done".format(join_cluster_name)
            else: #A1970
                os.system("./join_cluster -p bond0 -s bond1 -n {}".format(join_cluster_name))
                print "joining a cluster {} done".format(join_cluster_name)
                print ""
                #print "Creating a cluster done"

    def get_dev_path(self):
        #s = ""
        #for dev in parted.getAllDevices():
        #    name = "{}: {}".format(os.path.basename(dev.path), dev.model)
        #    size = int(dev.getSize())
        #    if size > 30000000:
        #        st = len(dev.path)
        #        if st == 29:
        #            if not s: #get the first one if there are many
        #                s= dev.path
                        #print s
        #return s
        s = []
        for dev in parted.getAllDevices():
            name = "{}: {}".format(os.path.basename(dev.path), dev.model)
            size = int(dev.getSize())
            #print name, size
            if not "multipath" in name:
                continue
            #print dev.path
            s.append(dev.path)
        return s

    def get_dev_path_A1970(self):
        s = []
        for dev in parted.getAllDevices():
            name = "{}: {}".format(os.path.basename(dev.path), dev.model)
            size = int(dev.getSize())
            #print name, size
            if not "multipath" in name:
                continue
            #print dev.path
            s.append(dev.path)
        return s
    def activate_perpetual_lic(self, is_connected):
        if is_connected:
            run_license = ""
            run_license = raw_input("Run perpetual license activation?(yes/no, default: no)\n")
            if not run_license:
                run_license = "no"
                print run_license
            if run_license == "yes" or run_license == "y":
                print "retrieving licenese from CRM..."
                logger.info("retrieving licenese from CRM...")
                do_cmd("clm -a retrievelic -t")
                print "activating license..."
                logger.info("activating license...")
                do_cmd("clm -a activatelic")
        else:
            print "\n------------------------------------------------------------------------------------\n"
            print("No access from outside network, please contact PROMISE Tech. for perpetual license.")
            print "\n------------------------------------------------------------------------------------\n"

    def print_create_cluster_description(self):
        print "--------------------------------------------------------------------------"
        print "If the setup node is the first node of a cluster, choose create a cluster."
        print "The cluster name is a unique name of a cluster in the same network."
        print "It will be used for other nodes to join to the cluster."
        print "Administrator name and password will be used in WebGUI."
        print "User can set replica between 1 to 3."
        print "Because it is a cluster, replica >= 2 is recommended."
        print "However, the capacity efficiency will be RAW capacity divided by replica."
        print "NOTE: replica can be changed in WebGUI as well."
        print "--------------------------------------------------------------------------"
    def validate_all_conf(self, productname, hostname, pub_ip, netmask_pub_ip,gateway_pub_ip, dns_pub_ip, storage_ip, netmask_storage_ip, ntp_server, storage_vol_name, create_or_join, cluster_name, replication):
        print ""
        print "New settings:"
        print "  Hostname: {}".format(hostname)
        print "  Public ip: {}".format(pub_ip)
        print "  Netmask of public network: {}".format(netmask_pub_ip)
        if gateway_pub_ip:
            print "  Gateway of public network: {}".format(gateway_pub_ip)
        if dns_pub_ip:
            print "  Dns of public network: {}".format(dns_pub_ip)
        print "  Storage ip: {}".format(storage_ip)
        print "  Netmask of storage network: {}".format(netmask_storage_ip)
        if ntp_server:
            print "  Ntp server address: {}".format(ntp_server)
        print "  Storage volume name: {}".format(storage_vol_name)
        print "  Create or join cluster: {}".format(create_or_join)
        print "  Cluster name: {}".format(cluster_name)
        if replication:
            print "  Replication number: {}".format(replication)
        print "  Default user name: admin"
        print "  Default password: admin"
        print ""

    def set_timezone(self):
        print "Setting timezone..."
        c_timezone = do_cmd("cat /etc/timezone")
        c_timezone = c_timezone.rstrip()
        print ("----------------------------------------------")
        print ("The current timezone is {}".format(c_timezone))
        print ("----------------------------------------------")
        reset_tz = raw_input("Would you like to set timezone? (yes/no, default: no):\n")
        if reset_tz == "yes" or reset_tz == "y":
            os.system("dpkg-reconfigure tzdata")
            #print "restart cron"
            os.system("service cron restart")
            "Setting timezone done"
        else:
            print "No set timezone"
    def set_timezone_auto(self):# needs to access outside network
        print "Setting timezone automatically..."
        T_Z = do_cmd("wget -O - -q http://geoip.ubuntu.com/lookup | sed -n -e \'s/.*<TimeZone>\\(.*\\)<\\/TimeZone>.*/\\1/p\'")
        T_Z = T_Z.rstrip()
        os.system("cp /usr/share/zoneinfo/{} /etc/localtime".format(T_Z))
        time.strftime('%X %x %Z')
        os.environ['TZ'] = '{}'.format(T_Z)
        time.tzset()
        time.strftime('%X %x %Z')
        #tz = get_localzone()
        #print "tz: {}".format(tz)
        os.system("echo {} >  /etc/timezone".format(T_Z))
        new_time_zone = self.get_timezone()
        print "Your time zone is {}.".format(new_time_zone)
        #_timezone = do_cmd("cat /etc/timezone")
        print "Setting timezone automatically done..."
    def get_timezone(self):
        c_timezone = do_cmd("cat /etc/timezone")
        c_timezone = c_timezone.rstrip()
        return c_timezone
    def count_phydrv_A1100(self):
        phydrv = do_cmd("cliib -u admin -p password -C phydrv")
        #print phydrv
        file_ = open('cnt_drv', 'w')
        file_.write("{}".format(phydrv))
        line_count = 0
        file_.close()
        with open('cnt_drv') as infp:
            for line in infp:
               if line.strip():
                  line_count += 1
        line_count = line_count-3
        return line_count


#logger = EZLog.get_logger(__name__)

if __name__ == "__main__":
    _parser = argparse.ArgumentParser()
    _parser.add_argument('--version', '-v', help='Print version.', action='store_true')
    _args = _parser.parse_args()
    if _args.version:
        print 'Cluster Wizard Version 1.2'
        sys.exit(0)
    A1100_productname = "RS300-E8-RS4"
    A1970_productname = "1970"
    A1970_productname2 = "H3970"
    #print A1100_productname
    cw = ClusterWizard()
    is_clus_existed = cw.check_cluster_existed()
    if is_clus_existed:
        print "Cluster existed"
        print "Exit the wizard"
        sys.exit(0)
    replication = ""
    EZLog.init_handler(
        logging.DEBUG, "/var/log/ezcloudstor/promise.log"
    )
    productname = cw.get_productname()
    print "Running cluster wizard..."
    logger.info("Running cluster wizard...")
    logger.info("Setting Network...")
    lnc = Local_network_config()
    netmask_pub_ip = "255.255.255.0"
    netmask_storage_ip = "255.255.255.0"
    c_pub_ip = do_cmd("/sbin/ifconfig bond0 | grep \'inet addr:\' | cut -d: -f2 | awk \'{ print $1}\'")
    c_pub_ip = c_pub_ip.rstrip()
    current_pub_ip = c_pub_ip.rstrip()
    c_storage_ip = do_cmd("/sbin/ifconfig bond1 | grep \'inet addr:\' | cut -d: -f2 | awk \'{ print $1}\'")
    c_storage_ip = c_storage_ip.rstrip()
    current_storage_ip = c_storage_ip.rstrip()
    hostname = cw.get_hostname()
    new_hostname = raw_input("Please enter a new hostname (e.g., hostname01) or accept the current hostname: {} with Enter.\n".format(hostname))
    if not new_hostname:
        new_hostname = hostname
    lnc.print_pub_ip_description()
    if not current_pub_ip:
        pub_ip = raw_input("Please enter a public IP (e.g., 10.0.0.10):")
    else:
        pub_ip = raw_input("Please enter a new public IP (e.g., 10.0.0.10) or accept the current public ip: {} with Enter:\n".format(current_pub_ip))
        if not pub_ip:
            pub_ip = c_pub_ip
    while not pub_ip:
        pub_ip = raw_input("Please enter a public IP (e.g., 10.0.0.10):")
    netmask_pub_ip = raw_input("Please enter a new netmask of the public network or accept the default: 255.255.255.0 with Enter:\n")
    gateway_pub_ip = raw_input("Please enter a gateway ip of the public network or leave blank with Enter:\n")
    dns_pub_ip = raw_input("Please enter a dns ip of the public network or leave blank with Enter:\n")
    lnc.print_storage_ip_description()
    if not current_storage_ip:
        storage_ip = raw_input("Please enter a storage IP (e.g., 10.10.10.10):\n")
    else:
        storage_ip = raw_input("Please enter a storage IP (e.g., 10.10.10.10) or accept the current storage IP: {} with Enter:\n".format(current_storage_ip))
        if not storage_ip:
            storage_ip = c_storage_ip
    while not storage_ip:
        storage_ip = raw_input("Please enter a storage IP (e.g., 10.10.10.10):\n")
    netmask_storage_ip = raw_input("Please enter a new netmask of the storage network or accept the default: 255.255.255.0 with Enter:\n")
    lnc.print_ntp_description()
    ntp_server = raw_input("Please enter an ntp server address or leave blank with Enter:\n")
    storage_vol_name = raw_input("Please enter a storage volume name (e.g., storage01):\n")
    while not storage_vol_name:
        storage_vol_name = raw_input("Please enter a storage volume name (e.g., storage01):\n")
    cw.print_create_cluster_description()
    create_or_join = ""
    while not create_or_join:
        create_or_join = raw_input("Please enter \"create\" or \"join\" a cluster(e.g., create):\n")
        if create_or_join == "create" or create_or_join == "c":
            cluster_name = raw_input("Please enter a cluster name (e.g., mycluster01):\n")
            while not cluster_name:
                cluster_name = raw_input("Please enter a cluster name (e.g., mycluster01):\n")
            while replication !="1" and replication !="2" and replication !="3":
                replication = raw_input("Please enter a replication number (between 1 to 3) of object data (e.g., 2):\n")
        elif create_or_join == "join" or create_or_join == "j":
            join_cluster_name = raw_input("Please enter a cluster name you want to join.(e.g., mycluster01):\n")
            while not join_cluster_name:
                join_cluster_name = raw_input("Please enter a cluster name you want to join.(e.g., mycluster01):\n")
        else:
            create_or_join = ""

    if not netmask_pub_ip:
        netmask_pub_ip = "255.255.255.0"
    if not netmask_storage_ip:
        netmask_storage_ip = "255.255.255.0"
    if create_or_join == "create" or create_or_join == "c":
        cw.validate_all_conf(productname, new_hostname, pub_ip, netmask_pub_ip,gateway_pub_ip, dns_pub_ip, storage_ip, netmask_storage_ip, ntp_server, storage_vol_name, create_or_join, cluster_name, replication)# create a cluster
    else:
        cw.validate_all_conf(productname, hostname, pub_ip, netmask_pub_ip,gateway_pub_ip, dns_pub_ip, storage_ip, netmask_storage_ip, ntp_server, storage_vol_name, create_or_join, join_cluster_name, replication)
    run_wizard = "no" #default not run
    if create_or_join == "create" or create_or_join == "c":
        run_wizard = raw_input("Would you like to {} a cluster {}? (yes/no or exit the wizard with Enter):\n".format(create_or_join, cluster_name))
    else:
        run_wizard = raw_input("Would you like to {} a cluster {}? (yes/no or exit the wizard with Enter):\n".format(create_or_join, join_cluster_name))
    if not run_wizard:
        run_wizard = "no"
    if run_wizard == "no" or run_wizard == "n":
        print "Exit"
        sys.exit(0)
    # Running all configuration
    # setting RAID
    cw.set_RAID(productname)
    print "Activating trial0 license..."
    logger.info("Activating trial0 license...")#    cw.activate_trial_license()
    cw.activate_trial_license()
    logger.info("Activating trial0 license done")
    # run set network
    print "Setting network..."
    lnc.set_network(pub_ip, netmask_pub_ip,gateway_pub_ip,dns_pub_ip,  storage_ip, netmask_storage_ip, productname, A1100_productname)
    #set ntp server
    lnc.set_ntpserver(ntp_server)
    print "Setting network done"
    #check is conneted to outside network
    is_connected = cw.is_connected()
    #set hostname
    cw.set_hostname(new_hostname)#
    #set timezone
    if is_connected:
        cw.set_timezone_auto()
    else:
        cw.set_timezone()
    #run activate perpetual license
    cw.activate_perpetual_lic(is_connected)
    # create volume
    cw.create_volume()
    if create_or_join == "create" or create_or_join == "c":
        cw.create_cluster(cluster_name, replication)
    else:
        cw.join_cluster(join_cluster_name)
        #print "join cluster"
    print "Run the wizard done."
