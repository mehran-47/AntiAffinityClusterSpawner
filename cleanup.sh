#!/bin/bash
rm vm_config_*
nova delete AF_VM_1
nova delete AF_VM_2
nova delete AF_VM_3
nova server-group-list
echo "nova server-group-delete"

