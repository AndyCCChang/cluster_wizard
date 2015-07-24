#!/usr/bin/env python
import os
import json
import StringIO
#from ConfigParser import SafeConfigParser
from ezs3.defaults import BigTeraDefaultSettings as defaults
from ezs3.log import EZLog
from ezs3.command import do_cmd
from ezs3.ntpconfig import NTPConfig

#logger = EZLog.get_logger(__name__)
class Local_network_config:
    def __init__(self):
        self.tmp_path = "/tmp/network/interfaces"
	self.net_path= "/etc/network/interfaces"
    def print_pub_ip_description(self):
        print "---------------------------------------------------------------------------------------------------------------"
        print "Public network:"
        print "Public network is the network between clients and VSky A-Series."
        print "No matter for HA (High Availability) consideration or not, bonding is required."
        print "The default bonding mode is ALB (Advanced Load Balancing)."
        print "In general, the mode does not need a switch ports to be set to a special bonding mode."
        print "However, if user likes to choose other bonding mode, please remember to set the bonding mode of switch as well."
        print "---------------------------------------------------------------------------------------------------------------"
    def print_storage_ip_description(self):
        print "--------------------------------------------------------------------------------------------------------------"
        print "Cluster(storage) network:"
        print "Cluster(storage) network is the network between nodes of a VSky A-Series cluster."
        print "The network should be a seperated network from the public network."
        print "No matter for HA (High Availability) consideration or not, bonding is required."
        print "The default bonding mode is ALB (Advanced Load Balancing)."
        print "In general, the mode does not need a switch ports to be set to a special bonding mode."
        print "However, if user likes to choose other bonding mode, please remember to set the bonding mode of switch as well."
        print "--------------------------------------------------------------------------------------------------------------"
    def print_ntp_description(self):
        print "-----------------------------------------------------------------------------------------------------------------------------------"
        print "NTP server address:"
        print "Every node should have the same NTP setting."
        print "Normally, keeping the setting as empty is okay, that is because the cluster will synchronize time to one of the nodes in a cluster."
        print "However, if S3 ACL or AD/LDAP service is used, please remember to synchronize time to NTP server."
        print "Otherwise, the authentication of the service will be failed."
        print "NOTE: One should not use name of NTP if there is no DNS server in public network settings."
        print "-----------------------------------------------------------------------------------------------------------------------------------"
    def set_ntpserver(self, ntp_server):
        ntp_config = NTPConfig()
        #ntp_config.remove_all_servers()
        if ntp_server:
            ntp_config.add_server(ntp_server)
        ntp_config.save()
        ntp_config.restart_service()
        
    def set_network(self, pub_ip, netmask_pub_ip,gateway_pub_ip,dns_pub_ip, storage_ip, netmask_storage_ip,  productname, A1100_productname):
        TEST198_IP = 0 # true
        tmp_path = "/tmp/network/interfaces"
        net_path= "/etc/network/interfaces"
        interfaces_exist= os.path.isfile(tmp_path)
        dir_exist = os.path.isdir("/tmp/network")
        if not dir_exist:
            do_cmd("mkdir /tmp/network/")
	if not interfaces_exist:
            do_cmd("touch /tmp/network/interfaces")        
 #       print "productname = %s" % (productname)
#        print pub_ip
        if productname == A1100_productname:
            #print productname
            file = open(tmp_path, 'w')
    	    file.write("auto lo eth7 eth6 eth5 eth4 eth0 bond0 bond1\n")
    	    file.write("iface bond0 inet static\n")
    	    file.write("        bond_miimon 100\n")
    	    file.write("        bond_slaves none\n")
#    	    file.write("        dns-nameservers 10.0.0.208\n")
    	    file.write("        bond_mode balance-alb\n")
    	    file.write("        address %s \n" % (pub_ip))
    	    file.write("        netmask %s \n" % (netmask_pub_ip))
            if gateway_pub_ip:
                file.write("        gateway %s \n" % (gateway_pub_ip))
    	    file.write("iface bond1 inet static\n")
    	    file.write("        bond_miimon 100\n")
    	    file.write("        bond_slaves none\n")
    	    file.write("        bond_mode balance-alb\n")
    	    file.write("        address %s \n" % (storage_ip))
    	    file.write("        netmask %s \n" % (netmask_storage_ip))
    	    file.write("iface lo inet loopback\n")
    	    file.write("iface eth7 inet manual\n")
    	    file.write("        bond_master bond1\n")
    	    file.write("iface eth6 inet manual\n")
    	    file.write("        bond_master bond1\n")
    	    file.write("iface eth5 inet manual\n")
    	    file.write("        bond_master bond0\n")
    	    file.write("iface eth4 inet manual\n")
    	    file.write("        bond_master bond0\n")
            #if TEST198_IP:
            #     file.write("iface eth0 inet static\n")
            #     file.write("        address 192.168.205.198\n")
            #     file.write("        netmask 255.255.255.0\n")
            #     file.write("        gateway 192.168.205.254\n")
            #     file.write("        dns-nameservers 192.168.202.108\n")
    	    file.close()
        else: #A1970
            file = open(tmp_path, 'w')
            file.write("auto lo eth3 eth2 eth1 eth0 bond0 bond1\n")
            file.write("iface bond0 inet static\n")
            file.write("        bond_miimon 100\n")
            file.write("        bond_slaves none\n")
    #       file.write("        dns-nameservers 10.0.0.208\n")
            file.write("        bond_mode balance-alb\n")
            file.write("        address %s \n" % (pub_ip))
            file.write("        netmask %s \n" % (netmask_pub_ip))
            file.write("iface bond1 inet static\n")
            file.write("        bond_miimon 100\n")
            file.write("        bond_slaves none\n")
            file.write("        bond_mode balance-alb\n")
            file.write("        address %s \n" % (storage_ip))
            file.write("        netmask %s \n" % (netmask_storage_ip))
            file.write("iface lo inet loopback\n")
            file.write("iface eth3 inet manual\n")
            file.write("        bond_master bond1\n")
            file.write("iface eth2 inet manual\n")
            file.write("        bond_master bond1\n")
            file.write("iface eth1 inet manual\n")
            file.write("        bond_master bond0\n")
            file.write("iface eth0 inet manual\n")
            file.write("        bond_master bond0\n")
            file.close()

        tmp_network_interface = do_cmd("cat /tmp/network/interfaces")
        etc_network_interface = do_cmd("cat /etc/network/interfaces")
        if tmp_network_interface != etc_network_interface:
            #print ("copy network interfaces")
	    do_cmd("cp /tmp/network/interfaces /etc/network/interfaces")
	    do_cmd("/etc/init.d/networking restart")
