# KISSHOME Traffic Recorder

`kisshome-traffic-logger` is a software package that is intended for use in the [KISSHOME research project](https://kisshome.de) to collect network traffic from participants.

It uses the traffic capturing feature of AVM FritzBox routers to record network traffic from Smart Home devices in the local network, cache the recorded traffic as PCAP files locally until they have been successfully transmitted to the collection site.


## Installation

On the Raspberry Pi, download and invoke the script [`install.sh`](install.sh) as follows:

```sh
wget -O - https://kisshome-deb.if-is.net/install.sh | bash -
```


## Design

The tool is packaged as a Debian package named [`kisshome-traffic-logger`](kisshome-traffic-logger) intended for Raspberry Pi OS based on Debian 12 Bookworm.
It contains components for

1. recording the traffic via [`kisshome-traffic-logger.sh`](kisshome_traffic_logger/usr/bin/kisshome-traffic-logger.py), and 
2. remote sync [`kisshome-traffic-logger-sync.sh`](kisshome_traffic_logger/usr/bin/kisshome-traffic-logger-sync.sh).

The traffic recorder uses the packet capture functionality of the FritzBox in combination with `tshark`. PCAPs are saved in regular intervals. The recorder is controlled by a [`systemd` service](kisshome_traffic_logger/lib/systemd/system/kisshome-traffic-logger.service), either via the command line `systemctl` or via a minimal web service.

The synchronization is implemented with `rsync` over ssh to provide confidentiality while transmitting the recorded traffic.
The frequency of the synchronization is controlled by a [cron job](kisshome_traffic_logger/etc/cron.d/kisshome-traffic-logger-cron).


## Backend
On the server side, this is done by prepending something like

`command="/usr/bin/rsync -av --server . /home/pi_test_user1/test/"`

to the keys in `authorized_keys` file in the `.ssh` directory.


## Configuration

Configuration is done via a config file named `/etc/kisshome/config.json`, and can be changed via a minimal web interface.

```
{
    // Local IP address of the FritzBox, default `192.168.178.1`
    "fritz_ip": "192.168.188.1",
    // Username and password to access the FritzBox's interface
    // The web interface checks whether the credentials are correct before saving.
    // Invalid credentials typically leed to account suspension on the FritzBox.
    "fritz_username": "admin",
    "fritz_password": "XXX"
}
```

## Web interface

The software comes with a minimal web interface that controls the recording (start, stop, restart) and allows configuring the recorder, e.g., for which devices traffic should be recorded. See the [web interface source](kisshome_traffic_logger/srv/www/kisshome_web/kisshome_web.py) for a description of its functionality and endpoints.

## Internals

```
kisshome_traffic_logger/
├── DEBIAN
│   ├── changelog
│   ├── compat
│   ├── control
│   ├── postinst
│   ├── postrm
│   └── prerm
├── etc
│   ├── cron.d
│   │   └── kisshome-traffic-logger-cron							# cron job to sync pcaps and remove stale/old files
│   ├── kisshome
│   │   └── rsync_dst_hostkey										# SSH key of the server that receives the pcaps
│   ├── sudoers.d
│   │   └── kisshome                                                # Allows the user of the web interface to issue systemctl start/stop/... for the kisshome-traffic-logger.service
│   └── systemd
│       └── system
│           └── var-lib-traffic\x2dlogger-hourly_pcaps.mount.d      # Mounts a RAM disk to store the pcaps in RAM
│               └── override.conf                                   # Specifies the size of the RAM disk and other parameters
├── lib
│   └── systemd
│       └── system
│           ├── kisshome-traffic-logger.service                     # systemd unit for the traffic recorder service
│           ├── kisshome-web-config.service                         # systemd unit for the web interface
│           └── var-lib-traffic\x2dlogger-hourly_pcaps.mount        # systemd mount for the RAM disk
├── srv
│   └── www
│       └── kisshome_web
│           ├── kisshome_web.py                                     # Backend for the web interface
│           └── templates
│               └── index.html                                      # Frontend for the web interface
└── usr
    ├── bin
    │   ├── kisshome-clear-cache.py                                 # Cleanup script to remove old/stale pcaps
    │   ├── kisshome-traffic-logger-sync.sh                         # Script to synchronize the pcaps with the server
    │   └── kisshome-traffic-logger.py                              # Traffic recording logic, interacts with the FritzBox
    └── sbin
        └── kisshome_traffic_loggerconfig                           # Initializes the configuration file /etc/kisshome/config.json
```

## Funding

KISSHOME (KI-gestützte & nutzerzentrierte Sicherheitslösung im Smart Home) is a research project by the Institute for Internet Security at the Westphalian University of Applied Sciences with ARIC Artificial Intelligence Center Hamburg e.V., and the Institut für Innovationsmarketing at the Technische Universität Hamburg. It is funded by the German ministry for research and education (Bundesministerium für Bildung und Forschung) under grant nr. 16KIS1653.
