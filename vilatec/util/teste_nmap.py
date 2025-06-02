import nmap
import config

nm = nmap.PortScanner()
a=nm.scan(hosts='192.168.0.*', arguments='-sP')
#print(a)
number_thread = 1
for k,v in a['scan'].items():
    if str(v['status']['state']) == 'up':
         number_thread += 1
         #print (v)
         try:

                endereco_mac = itens.split(" ")[0]
                endereco_ip = itens.split(" ")[1]
                print(endereco_ip)
                print(endereco_mac)
                # for k, v in self.LedsWifi.items():

                #     if self.LedsWifi[k]['MAC'] in endereco_mac:
                #         self.LedsWifi[k]['IP'] = endereco_ip
                #         self.LedsWifi[k]['COUNTER'] = 0
                #     print (v['addresses']['ipv4'] + ' => ' + str(v['addresses']['mac'].replace(':',"")))
         except:
             print (v['addresses']['ipv4'])
print("done")
"""return {ip:product}, which port is open from ip's netmask"""
#~ print('Scaning')
#~ port = "1883"
#~ return_value = {}
#~ nm = nmap.PortScanner()
#~ nm.scan(hosts='%s/%s' % ("192.168.0.1", "24"), ports=port, arguments='')
#~ print(nm.command_line())
#~ print(nm.all_hosts())
#~ hosts_list = [(x, nm[x]['tcp'][int(port)]['product']) for x in nm.all_hosts()]
#~ print("Len of hosts_list: %s" % len(hosts_list))
#~ for i in hosts_list:
    #~ if 1:
        #~ return_value[i[0]] = i[1]
    #~ else:
        #~ print("I pass")
#~ print(return_value)
