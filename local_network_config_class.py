#!/usr/bin/env python
#####################
#Version 1.3.1      #
#Add quorum network #
#####################

import os
import json
import StringIO
import textwrap
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
        print ""
        print "Public network:"
        p_net = "The public network connects storage clients to the VSky A-Series system. Port bonding is required for all environments, including HA and non-HA. The default port bonding protocol used is ALB (Advanced Load Balancing) - this method does not require any additional configuration of the network switch. If a different port bonding protocol is used, be sure the network switch is configured to accommodate the bonding protocol."
        print textwrap.dedent(p_net)
        print ""        
    def print_storage_ip_description(self):
        s_net = "The cluster (private) network connects only the nodes in a VSky A-Series cluster. Again, port bonding is required. The default bonding protocol is ALB (Advanced Load Balancing). If you choose a different bonding protocol, make sure the connected network switch is properly configured to accommodate the bonding protocol."
        print ""
        print "Cluster (private) network:"
        print textwrap.dedent(s_net)
        print ""
    def print_ntp_description(self):
        print ""
        print "NTP server address:"
        ntp_net = "NTP must be used for S3, ACL and AD/LDAP to function. Make sure all nodes are using the same NTP server. Enter the IP address of the NTP server if there is no DNS server IP address entered in the public network settings."
        print textwrap.dedent(ntp_net)
        print ""
    def set_ntpserver(self, ntp_server):
        ntp_config = NTPConfig()
        #ntp_config.remove_all_servers()
        if ntp_server:
            ntp_config.add_server(ntp_server)
        ntp_config.save()
        ntp_config.restart_service()
        
    def set_network_quorum(self, storage_ip, netmask_storage_ip, storage_nic):
        TEST198_IP = 0
        TEST35_IP = 0
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
        
        if storage_nic =="bond0":
            file = open(tmp_path, 'w')
    	    file.write("auto lo eth5 eth4 bond0\n")
            if TEST35_IP:
                file.write("auto eth0\n")
            if TEST198_IP:
                file.write("auto eth0\n")
    	    file.write("iface bond0 inet static\n")
    	    file.write("        bond_miimon 100\n")
    	    file.write("        bond_slaves none\n")
    	    file.write("        bond_mode balance-alb\n")
    	    file.write("        address %s \n" % (storage_ip))
    	    file.write("        netmask %s \n" % (netmask_storage_ip))
    	    file.write("iface lo inet loopback\n")
    	    file.write("iface eth5 inet manual\n")
    	    file.write("        bond_master bond0\n")
    	    file.write("iface eth4 inet manual\n")
    	    file.write("        bond_master bond0\n")
            if TEST35_IP:
                 file.write("iface eth0 inet static\n")
                 file.write("        address 192.168.205.35\n")
                 file.write("        netmask 255.255.255.0\n")
                 file.write("        gateway 192.168.205.254\n")
                 file.write("        dns-nameservers 192.168.202.108\n")
            if TEST198_IP:
                 file.write("iface eth0 inet static\n")
                 file.write("        address 192.168.205.198\n")
                 file.write("        netmask 255.255.255.0\n")
                 file.write("        gateway 192.168.205.254\n")
                 file.write("        dns-nameservers 192.168.202.108\n")
    	    file.close()
        elif "eth" in straoge_nic:
            file = open(tmp_path, 'w')
            file.write("auto lo eth7 eth6 %s eth4 eth0 bond1\n" %(straoge_nic))
            file.write("iface lo inet loopback\n")
            file.write("iface %s inet static\n" % (storage_nic))
    	    file.write("        address %s \n" % (storage_ip))
    	    file.write("        netmask %s \n" % (netmask_storage_ip))
            if TEST198_IP:
                 file.write("iface eth0 inet static\n")
                 file.write("        address 192.168.205.198\n")
                 file.write("        netmask 255.255.255.0\n")
                 file.write("        gateway 192.168.205.254\n")
                 file.write("        dns-nameservers 192.168.202.108\n")
            if TEST35_IP:
                 file.write("iface eth0 inet static\n")
                 file.write("        address 192.168.205.35\n")
                 file.write("        netmask 255.255.255.0\n")
                 file.write("        gateway 192.168.205.254\n")
                 file.write("        dns-nameservers 192.168.202.108\n")

            
    	    file.close()

        tmp_network_interface = do_cmd("cat /tmp/network/interfaces")
        etc_network_interface = do_cmd("cat /etc/network/interfaces")
        if tmp_network_interface != etc_network_interface:
            #print ("copy network interfaces")
	    do_cmd("cp /tmp/network/interfaces /etc/network/interfaces")
	    do_cmd("/etc/init.d/networking restart")
    def set_network(self, pub_ip, netmask_pub_ip,gateway_pub_ip,dns_pub_ip, storage_ip, netmask_storage_ip,  productname, A1100_productname):
        TEST198_IP = 0
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
        #if productname == A1100_productname:
        if A1100_productname in productname:
	        #turn off eth0~eth3 to avoid avahi issue
            do_cmd("ifconfig eth0 0.0.0.0; ifconfig eth0 down")
            do_cmd("ifconfig eth1 0.0.0.0; ifconfig eth1 down")
            do_cmd("ifconfig eth2 0.0.0.0; ifconfig eth2 down")
            do_cmd("ifconfig eth3 0.0.0.0; ifconfig eth3 down")
            #print productname
            file = open(tmp_path, 'w')
    	    file.write("auto lo eth7 eth6 eth5 eth4 bond0 bond1\n")
			#if TEST198_IP:
			#    file.write("eth0\n")
    	    file.write("iface bond0 inet static\n")
    	    file.write("        bond_miimon 100\n")
    	    file.write("        bond_slaves none\n")
            if dns_pub_ip:
    	        file.write("        dns-nameservers %s\n" % (dns_pub_ip))
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
            if dns_pub_ip:
    	        file.write("        dns-nameservers %s\n" % (dns_pub_ip))
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
