#!/bin/bash
rm vm_config_* 
nova delete AF_VM_8
nova delete AF_VM_7
nova delete AF_VM_6
nova delete AF_VM_5
nova delete AF_VM_4
nova delete AF_VM_3
nova delete AF_VM_2
nova delete AF_VM_1
nova server-group-list
echo "nova server-group-delete"

