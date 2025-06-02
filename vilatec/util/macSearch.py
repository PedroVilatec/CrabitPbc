#!/usr/bin/python

import nmap


target_mac = '<Enter MAC Adress>'

nm = nmap.PortScanner()

nm.scan(hosts="192.168.0.1/24", arguments='-sP')

host_list = nm.all_hosts()
for host in host_list:
        print(host)
        if  'mac' in nm[host]['addresses']:
                print(nm[host]['addresses']['mac'])
                if nm[host]['addresses']['mac'] == '98:83:89:5D:86:9D':
                        print(nm[host]['addresses']['mac'])
                        print("ok")
        #if  'mac' in nm[host]['addresses']:
                #print(host+' : '+nm[host]['addresses']['mac'])
                #if target_mac == nm[host]['addresses']['mac']:
                        #print('Target Found')
