#!/usr/bin/env python3
import re, sys, time, netifaces, os, json, random
from subprocess import call

class updates():
	def __init__(self):
		with open('/etc/hostname', 'r') as f: 
			self.oldhostname = f.read().strip()
		self.ip_eth0 = netifaces.ifaddresses('eth0')[2][0]['addr']

	def set_hostname(self, newhostname):
		with open('/etc/hostname.old', 'w+') as fw: fw.write(self.oldhostname)
		with open('/etc/hostname', 'w') as f: f.write(newhostname)
		with open('/etc/hosts', 'r') as f: readlines = f.read()
		with open('/etc/hosts.old', 'w+') as f: f.write(readlines)
		with open('/etc/hosts', 'w') as fw: fw.write(re.sub(self.oldhostname,newhostname,readlines))
		#for opensaf
		with open('/etc/opensaf/node_name', 'w') as fw: fw.write(newhostname)

	def set_slot_id(self, s_id):
		with open('/etc/opensaf/slot_id', 'w') as fw: fw.write(s_id)

	def fix_dtmd(self):
		with open('/etc/opensaf/dtmd.conf','r') as f: readlines = f.readlines()
		regex_compiled = re.compile(r'DTM_NODE_IP=(\d+\.){3}\d+', re.MULTILINE)
		endString = ''
		for line in readlines: 
			endString += regex_compiled.sub('DTM_NODE_IP='+self.ip_eth0, line) if line[-1]=='\n' else regex_compiled.sub(newhostname, line)+'\n'		
		with open('/etc/opensaf/dtmd.conf','w') as fw: fw.write(endString)

	def set_node_type(self, nodetype):
		with open('/etc/opensaf/node_type', 'w') as fw: fw.write(nodetype)

	def append_default_commands(self, commandsList):
		commandsList = ['#!/bin/bash'] + commandsList
		with open('/etc/init.d/default_startups', 'w+') as fw: fw.write('\n'.join(commandsList))
		call('chmod +x /etc/init.d/default_startups'.split(' '))
		call('update-rc.d default_startups defaults 99'.split(' '))

	def replace_imm(self):
		call('mv /etc/opensaf/imm.xml /etc/opensaf/imm.xml.bkp'.split(' '))
		call('cp /home/node1/imm_2+2SIs.xml /etc/opensaf/imm.xml'.split(' '))

def finalize(timeout=3):
	time.sleep(timeout)
	call('reboot')

if __name__ == '__main__':
	if sys.argv[1:]:
		if os.path.exists(os.getcwd()+'/'+sys.argv[1]):
			with open(sys.argv[1], 'r') as f: config = json.loads(f.read())
			up = updates()
			up.set_hostname(config['hostname'])
			up.set_slot_id(config['slot_id'])
			up.append_default_commands(config['default_commands'])
			up.set_node_type(config['node_type'])
			up.fix_dtmd()
			up.replace_imm()
			finalize(random.random()*7)
		else:
			print('Config file %s not found, quitting' %(sys.argv[1]))
	else:
		print('Usage:\nupdate.py <config_file>.json')