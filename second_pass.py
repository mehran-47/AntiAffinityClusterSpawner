#!/usr/bin/env python
from vm_spawner import VMSpawner
import glob, json

def second_pass(vms):
	for configPath in glob.glob('./vm_config_*'):
		with open(configPath, 'r') as f: aVMConfig = json.loads(f.read())
		vms.execute_commands_at( \
			aVMConfig['username'], \
			vms.get_floating_ip_of(aVMConfig['openStackVMname']), \
			aVMConfig['password'], \
			['echo ' + aVMConfig['password'] + ' | sudo -S service default_startups start', 'exit'] )

if __name__=='__main__':
	if os.path.exists(os.getcwd()+'/config.json'):
		with open('config.json', 'r') as f:
			mainConfig = json.loads(f.read())	
		vms = VMSpawner(mainConfig['floating_ip_pool'])	
		second_pass(vms)