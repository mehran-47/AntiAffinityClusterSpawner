from vm_spawner import VMSpawner
from threading import Thread
import glob, json, os

def second_pass(vms):
	for configPath in sorted(glob.glob('./vm_config_*')):
		with open(configPath, 'r') as f: aVMConfig = json.loads(f.read())
		Thread(target= vms.execute_commands_at, args=( \
			aVMConfig['username'], \
			vms.get_floating_ip_of(aVMConfig['openStackVMname']), \
			aVMConfig['password'], \
			['echo ' + aVMConfig['password'] + ' | sudo -S service default_startups start'] )
		).start()
		'''
		vms.execute_commands_at( \
			aVMConfig['username'], \
			vms.get_floating_ip_of(aVMConfig['openStackVMname']), \
			aVMConfig['password'], \
			['echo ' + aVMConfig['password'] + ' | sudo -S service default_startups start'] )
		'''

if __name__=='__main__':
	if os.path.exists(os.getcwd()+'/config.json'):
		with open('config.json', 'r') as f:
			mainConfig = json.loads(f.read())	
		vms = VMSpawner(mainConfig['floating_ip_pool'])	
		second_pass(vms)