#!/usr/bin/python

"""
Starts network traffic recording via the AVM FritzBox packet capture functionality. This tool expects a JSON-formatted configuration file at /etc/kisshome/config.json.
"""

import os
import subprocess
import logging
import json

# Initialize the logging system
logging.basicConfig(filename='/var/log/kisshome/fritz_capture.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger()

# Configuration file path
CONFIG_FILE = '/etc/kisshome/config.json'

# Load configuration from the JSON file
try:
    with open(CONFIG_FILE, 'r') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    logger.error("No config.json found.")
    exit(1)


# This is the address of the router
fritzboxip = config.get('fritz_ip', '')

# The interface where traffic should be recorded. The guest network uses "1-guest".
iface = config.get('interface', '1-guest')

# If you use password-only authentication use 'dslf-config' as username.
fritzboxuser = config.get('fritz_username', '') #"fritz0619"
fritzboxpwd = config.get('fritz_password', '') #"FRITZ!Box-Kennwort"

if not fritzboxpwd or not fritzboxuser:
    logger.error(f"Username/Password empty. Usage: {os.path.basename(__file__)} <username> <password>")
    exit(1)

logger.info(f"Trying to login into {fritzboxip} as user {fritzboxuser}")

# Request challenge token from Fritz!Box
challenge_response = subprocess.check_output(['curl', '-k', '-s', fritzboxip + '/login_sid.lua']).decode('utf-8')
CHALLENGE = challenge_response.split("<Challenge>")[1][:8]

# Create an authentication token by hashing challenge token with password
from hashlib import md5
challenge_password = CHALLENGE + '-' + fritzboxpwd
challenge_password = ''.join([char + chr(0) for char in challenge_password])
HASH = md5(challenge_password.encode()).hexdigest()

login_response = subprocess.check_output(['curl', '-k', '-s', fritzboxip + '/login_sid.lua', '-d', 'response=' + CHALLENGE + '-' + HASH, '-d', 'username=' + fritzboxuser]).decode('utf-8')
SID = login_response.split("<SID>")[1][:16]

# Check for successful authentication
if SID == '0000000000000000':
    logger.error("Login failed. Did you create & use explicit Fritz!Box users?")
    exit(1)

logger.info(f"Capturing traffic on FritzBox interface {iface}")

# Get filter expression from the config and build a bpf expression
filtered_macs = config.get('filtered_macs', '')
logger.info(f"Filter config value: {filtered_macs}")
filter_expr = ""
# The web ui should ensure that a correctly formatted list of comma-separated MACs is set when storing the configuration.
if filtered_macs != "":    
    mac_addresses = filtered_macs.split(",")
    # Variant A:
    # Build a filter expression of the form: ether host 12:23:34:..:cd or ether host 23:41:1a:..:fa ...
    # m = ["a", "b", "c"]
    # ' or '.join(f'ether host {e}' for e in m) -> 'ether host a or ether host b or ether host c'
    #filter_expr = ' or '.join(f'ether host {addr}' for addr in mac_addresses)
    #
    # Variant B:
    # Build a filter expression of the form: ether host 12:23:34:..:cd || 23:41:1a:..:fa ...
    # m = ["a", "b", "c"]
    # 'ether host ' + ' || '.join(m) -> 'ether host a || b || c'
    filter_expr = 'ether host ' + ' || '.join(mac_addresses)

logger.info(f"Capturing traffic on FritzBox using filter expression: {filter_expr}")

capture_url = fritzboxip + f'/cgi-bin/capture_notimeout?ifaceorminor={iface}&snaplen=1600&filter={filter_expr}&capture=Start&sid={SID}'
# tshark arguments:
#   -i -    read from stdin
#   -q      quiet, no output
#   -b interval:3600    rotate pcap file every 3600 seconds (once per hour)
#   -b nametimenum:2    make start time part before running number part (e.g. log_20210828164426_00001.pcap)
capture_command = f'wget --no-check-certificate --timeout 90 -qO- "{capture_url}" | tshark -i - -q -b interval:3600 -b nametimenum:2 -w /var/lib/traffic-logger/hourly_pcaps/traffic.pcap'

subprocess.call(capture_command, shell=True)

logger.info("Traffic capture completed")

