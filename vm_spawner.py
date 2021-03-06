from pexpect import spawn, exceptions as pexpect_excepts
from subprocess import Popen, PIPE, call
from threading import Thread
import sys, time, json, os, re, glob, random


class VMSpawner():
	def __init__(self, floatingIpPool):
		self.floatingIpPool = floatingIpPool

	def is_active_after_boot(self, vmname):
		command = Popen(['nova','list'], stdout=PIPE)
		outputList = [line for line in command.stdout]
		for entry in outputList[3:-1]:
			if entry.split('|')[2].strip()==vmname:
				return 'ACTIVE'== entry.split('|')[3].strip()
		return False

	def server_group_exists(self, groupname):
		command = Popen(['nova','server-group-list'], stdout=PIPE)
		outputList = [line for line in command.stdout]
		for entry in outputList[3:-1]:
			if entry.split('|')[2].strip()==groupname:
				return True
		return False

	def get_vm_names(self):
		command = Popen(['nova','list'], stdout=PIPE)
		outputList = [line for line in command.stdout]
		return [entry.split('|')[2].strip() for entry in outputList[3:-1]]

	def get_floating_ip_of(self, vmname):
		vmnames = self.get_vm_names()
		if vmname in vmnames:
			command = Popen(['nova','list'], stdout=PIPE)
			outputList = [line for line in command.stdout]
			entry = outputList[3:-1][vmnames.index(vmname)]
			return entry.split('|')[6].rsplit(',')[1].strip()
		else:
			return None
			
	def boot_with_snapshot(self, aVMConfig, configDumpFile, timeout=300):
		snapshot, vmname, antiAffinityGroupName, flavor, username, pw =\
		 aVMConfig['source_snapshot'], aVMConfig['openStackVMname'], aVMConfig['groupname'], aVMConfig['flavor'], aVMConfig['username'], aVMConfig['password']
		if vmname in self.get_vm_names():
			print('VM %s already exists. Please provide unique VM name to boot.' %(vmname))
			return
		command = Popen(['nova','boot','--flavor',flavor,'--image', snapshot, vmname, '--hint', 'group='+antiAffinityGroupName])
		while timeout>0 and not self.is_active_after_boot(vmname):
			time.sleep(2)
			timeout-=3
		if self.is_active_after_boot(vmname):
			print('%s created successfully' %(vmname))
			floatingIp = self.floatingIpPool.pop(0)
			call(['nova', 'add-floating-ip', vmname, floatingIp])
			updates_failed = True
			while updates_failed:
				try:
					time.sleep(random.randrange(1,5))
					self.push_updates(username, floatingIp, pw, configDumpFile)
					updates_failed = False
				except pexpect_excepts.EOF:
					print('Pushing updates failed for %s' %(vmname))
					updates_failed = True
		else:
			print('%s is taking longer than usual (~5 minutes) to boot; consider troubleshooting. Customization of %s is halted' %(vmname, vmname))

	def send_files(self, user, ip, pw, files):
		for aFile in files:
			print('Sending files...')
			print('scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '+aFile.split('/')[-1]+' '+user+'@'+ip+':'+aFile)
			child_scp = spawn('scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '+aFile.split('/')[-1]+' '+user+'@'+ip+':'+aFile, timeout=None)
			child_scp.expect(user+"@"+ip+"'s password:")
			child_scp.sendline(pw)
			for line in child_scp:
				pass

	def execute_commands_at(self, user, ip, pw, commands):
		print('Logging in remotely...')
		print('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '+user+'@'+ip)
		child_shell = spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '+user+'@'+ip, timeout=None)
		child_shell.expect(user+"@"+ip+"'s password:")
		child_shell.sendline(pw)
		for command in commands:
			child_shell.sendline(command)
		for line in child_shell:
			pass
			
	def push_updates(self, user, ip, pw, configFile):
		self.send_files(user, ip, pw, \
			['/home/node1/updates.py', \
			'/home/node1/'+configFile, \
			'/home/node1/imm_2+2SIs.xml'])
		self.execute_commands_at(user, ip, pw, 
			['echo '+ pw + ' | sudo -S python3 /home/node1/updates.py '+configFile])

	def get_last_spawned_vm_index(self):
		vmConfigFileList = [f for f in os.listdir('.') if re.match( r'vm_config_[0-9]{1}.json', f)]
		return int(vmConfigFileList[-1].rsplit('json')[0][-2])+1 if vmConfigFileList[0:] else -1	

	def spawn_vms(self, num, lastSpawnedVMIndex, vmConfigs):
		finalIndex = lastSpawnedVMIndex+num+1 if lastSpawnedVMIndex+num+1 <= len(vmConfigs) else len(vmConfigs)
		for i in range(lastSpawnedVMIndex+1, finalIndex):
			with open('vm_config_'+ str(i) +'.json', 'w+') as fw: fw.write(json.dumps(vmConfigs[i], indent=4))
			Thread(target=vms.boot_with_snapshot, args=(vmConfigs[i], 'vm_config_'+str(i)+'.json')).start()
			time.sleep(1)

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
		for anAntiAffinityGroup in mainConfig['anti_affinity_groups']:
			if not vms.server_group_exists(anAntiAffinityGroup): 
				call(['nova', 'server-group-create', anAntiAffinityGroup, 'anti-affinity'])
		num = int(sys.argv[1]) if sys.argv[1:] else len(mainConfig['vm_configs'])		
		vms.spawn_vms(num, vms.get_last_spawned_vm_index(), mainConfig['vm_configs'])

