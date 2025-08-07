#1/bin/bash
echo Installing dependencies
export DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC
apt-get update
apt-get -y upgrade
apt-get install -y curl gpg make nano procps tzdata

sync
