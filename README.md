# AntiAffinityClusterSpawner
Usage:
./vm_spawner 
creates all VMs specified in the configuration
./vm_spawner <an integer>
creates the number of specified VMs since the last VM created according to the specification. E.g. If the configuration as 4 VM specifications in total, './vm_spawner 2' will create the first two './vm_spawner 4' will create the last two. (The argument 4 is not a mistake. Any number greater than 1 will create 2 VMs since only 4 VMs in total has been specified in the configuration ).