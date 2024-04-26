#!/bin/bash

# Set the path to your SSH key
SSH_KEY="/etc/ssh/kisshomekey"

# Transfer pcaps
/usr/bin/rsync -avr -e "ssh -o UserKnownHostsFile=/etc/ssh/kisshome_known_hosts -i $SSH_KEY" /var/lib/traffic-logger/hourly_pcaps/ pcaps1@kisshome-experiments.if-is.net:/path/to/remote/files/ 2>&1 >> /tmp/kisshome-sync.log
