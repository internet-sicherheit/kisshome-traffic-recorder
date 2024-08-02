#!/bin/bash

# Set the path to your SSH key
SSH_KEY="/etc/kisshome/kisshomekey"

# Transfer pcaps
/usr/bin/rsync -avr -e "ssh -o UserKnownHostsFile=/etc/kisshome/rsync_dst_hostkey -i $SSH_KEY" --timeout=60 /var/lib/traffic-logger/hourly_pcaps/ pcaprecv@kisshome-experiments.if-is.net:/path/to/remote/files/
