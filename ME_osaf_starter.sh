#!/bin/bash
cd /home/node1/Downloads/lttngAnalysesForOpenSAF/
echo magic123 | sudo -S python3 -m lttngAnalyses.destroy_and_clean
echo magic123 | sudo -S python3 -m lttngAnalyses.daemon_controller_client 192.168.10.7 6666 &
echo magic123 | sudo -S service opensafd start