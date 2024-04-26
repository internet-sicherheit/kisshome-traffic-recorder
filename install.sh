#!/bin/bash
# wget -O - https://kisshome-deb.if-is.net/install.sh | bash -

# Some parts are based on the HACS installation script from https://get.hacs.xyz
RED_COLOR='\033[0;31m'
GREEN_COLOR='\033[0;32m'
GREEN_YELLOW='\033[1;33m'
NO_COLOR='\033[0m'

function info () { echo -e "${GREEN_COLOR}INFO: $1${NO_COLOR}";}
function warn () { echo -e "${GREEN_YELLOW}WARN: $1${NO_COLOR}";}
function error () { echo -e "${RED_COLOR}ERROR: $1${NO_COLOR}"; if [ "$2" != "false" ]; then exit 1;fi; }

function checkRequirement () {
    if [ -z "$(command -v "$1")" ]; then
        error "'$1' is not installed"
    fi
}

#checkRequirement "wget"
checkRequirement "curl"
checkRequirement "apt"
checkRequirement "apt-key"

# Add the PGP key that we use to sign the KISSHOME packages to the local key store
info "Adding the PGP key for KISSHOME packages"
curl https://kisshome-deb.if-is.net/apt-repo/dists/stable/kisshome-repo.gpg | sudo apt-key add -

# Add our repository to the apt sources
info "Adding our Debian package repository"
echo "deb [arch=all] https://kisshome-deb.if-is.net/apt-repo stable main" | sudo tee /etc/apt/sources.list.d/kisshome.list

# Update the package metadata
info "Updating the local package metadata via sudo apt update"
sudo apt update

# Set the choice for "should non-superusers be able to capture packets?" during wireshark installation to false
echo "wireshark-common wireshark-common/install-setuid boolean false" | sudo debconf-set-selections

# Install the KISSHOME package
info "Installing the KISSHOME packages via sudo apt install kisshome-traffic-logger"
sudo apt-get -y install kisshome-traffic-logger
