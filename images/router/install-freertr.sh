mkdir /p4/freertr
cd /p4
wget http://www.freertr.org/rtr.jar
wget http://www.freertr.org/rtr-$(uname -m).tgz -O rtr.tgz
tar -xvf rtr.tgz -C /p4/freertr
rm rtr.tgz
#Rapt-get install -y build-essential libpcap-dev --autoremove
