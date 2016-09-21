#!/usr/bin/env python3
from pexpect import spawn
from sys import argv

def execute_commands_at(user, ip, pw, commands):
	print('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '+user+'@'+ip)
	child_shell = spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '+user+'@'+ip, timeout=None)
	child_shell.expect(user+"@"+ip+"'s password:")
	child_shell.sendline(pw)
	for command in commands:
		child_shell.sendline(command)
	for line in child_shell:
		pass

def scale_out_vm():
	commands = ['source mehran-admin-nova',\
	'cd anti_affinity_demo/AntiAffinityClusterSpawner/',\
	'python vm_spawner.py 2',\
	'exit']
	print('Scaling out VMs...')
	execute_commands_at('node1', '192.168.205.42', 'magic123', commands)

if __name__ == '__main__':
	scale_out_vm()
	#if argv[1:]:
