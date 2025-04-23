from lab_app import *
import errno
import json
from multiprocessing import Process
import os

from random import randrange


def read_setup(setup):
    f = open('networks/'+setup+'.json')
    print(f)
    try:
        data = json.load(f)
        print(data)
        return (data.get("nodes", None),data.get("bridges",None),data.get("files",None))
    except:
        print("Badly formatted configuration file")
        return None

def create_nodes(nodes):
    for node in nodes:
        if not c(node['name']):
            ns_root.register_ns(node['name'],node['image'])
            
def create_bridges(bridges, nodes=[],p4=False):  
    for bridge in bridges:
        # If 2 adjacencies it is basically a link
        adj = bridge['adjacencies']
        adjcount = len(adj)
        bname = bridge['name']
        switch = False
        try:
            if bridge['showswitch']=="yes":
                switch = True
        except:
            pass
        if switch==False:
            rname = adj[0].split(";")[0]
            name = adj[1].split(";")[0]
 #           print("Connecting " +name + " to " + rname)
            nic = c(name).connect(c(rname),bname, bname)
            r('ip netns exec $name ip link set $bname up')
            r('ip netns exec $rname ip link set $bname up')
        else:
            # Create switch
  #          print("Setting up bridge for 3 or more nodes")
            # Check if bridge already defined:
            exists = False
            for node in nodes:
              if node['name']==bname:
                exists=True
            if not exists:
              ns_root.register_ns(bname, '34334:switch','switch')
            if not p4:
              c(bname).enter_ns()
              r('brctl addbr $bname')
              # or r('ip link add name $bname type bridge')
              r('ip link set $bname up')
              r('brctl stp $bname off')
              r('brctl setageing $bname 0')
              r('brctl setfd $bname 0')
              c(bname).exit_ns()
            for node in adj:
                name=node.split(";")[0]
   #             print("Connecting "+bname+" to "+name)
                nic = c(bname).connect(c(name))      
    #            print("Listed nics in " + name + ":")
                for nic in c(name).nics:
                    print(nic)
     #           print("Listed nics in " + bname + ":")
                for nic in c(bname).nics:
                    print(nic)
                r('ip netns exec $bname ip link set $name up')
                r('ip netns exec $name ip link set $bname up') 
                if not p4:
                  r('ip netns exec $bname brctl addif $bname $name')
                
def ip_address(iprange,host):
    prefix = '.'.join(iprange.split('.')[0:3])
    ipaddress = prefix + "." + str(host)
    return ipaddress

def recode_addresses(bridge):
    iprange = bridge.get("network")
    hostid = 1
    addresstable = []
    gw = bridge.get("gateway")
    gwip=''
    for node in bridge["adjacencies"]:
        name = node.split(";")[0]
        try:
            hostid = int(node.split(";")[1])
        except:
            pass
        addr = {"name" : name, "ip" : ip_address(iprange,hostid) }
        if name == gw:
            gwip = addr["ip"]
        addresstable.append(addr)
        hostid = hostid+1
    return (gw, gwip, addresstable)
            
def set_addresses(bridges):
    # Setting addresses based on json. We assume /24 prefixes and use first available value for gateway unless specified
    print("Setting IP addresses")
    for bridge in bridges:
        print(type(bridge))
        if "network" in bridge:
            bridgename = bridge["name"]
            (gw, gwip, adrtable) = recode_addresses(bridge)
            for node in adrtable:
                name = node["name"]
                ip = node["ip"]
                ip_prefix = ip + "/24"
                r('ip netns exec $name ip addr add $ip_prefix dev $bridgename')
                if (ip != gwip) and gw:
                    r('ip netns exec $name ip route add default via $gwip')


def set_internet(inetnode, interface, bridge, ip, gw):
    # Moving external connection to interface in docker config.
    print("Setting up internet via node " + inetnode)
    nic = c(bridge).connect(ns_root)
    
    #ensure network manager doesn't mess with anything
    r('ip netns exec $bridge brctl addif $bridge $nic')
    r('ip netns exec $bridge ip link set $nic up')
    ns_root.enter_ns()

    r('service NetworkManager stop')
    # Connecting root to lab
    print("Connecting localhost to lab")
    r('ip link set $bridge name 34334_lab')
    r('ip link set 34334_lab up')
    r('ip addr add $ip dev 34334_lab')
    # Moving external interface to defined lab node
    r('ip link set $interface netns $inetnode')
    r('ip route add default via $gw')
    
    c(inetnode).enter_ns()
        
    inet_nic = bridge
    r('ip link set $interface up')
    # Setting up NAT as inet node
    r('dhclient $interface')
    r('iptables -t nat -A POSTROUTING -o $interface -j MASQUERADE')
    r('iptables -A FORWARD -i $interface -o $inet_nic -m state --state RELATED,ESTABLISHED -j ACCEPT')
    r('iptables -A FORWARD -i $inet_nic -o $interface -j ACCEPT')
    r('docker exec -ti $inetnode sysctl -w net.ipv4.ip_forward=1')
    # Solving an issue with same MAC addresses. Not nice solution
    try:
        r('ip netns exec server ip link set internal address aa:14:c2:76:80:17')
        r('ip netns exec internet ip link set internal address aa:14:c2:76:80:18')
        r('ip netns exec snort ip link set internal address aa:14:c2:76:80:16')
    except:
        print("Hopefully not relevant")

def copy_files(files):
  print("Copying files to containers")
  print(files)
  path = 'files/'
  cur_folder = os.getcwd()
  print(f"Current folder {cur_folder}")
  for item in files:
    copystring = f"docker cp {path}{item.get('src')} {item.get('name')}:{item.get('dst')}"
    print(copystring)
    r(copystring)

  
            
                
def setup_bmv2(setup):
    try:
        ns_root.shutdown()
    except:
        print('[*] Did not shutdown cleanly, trying again')
        docker_clean()
    finally:
        print("Establishing network " + str(setup))
        docker_clean()
        # Stop IP forwarding on Debian
        r('sysctl -w net.ipv4.ip_forward=0')    
        # Reading network setup
        (nodes,bridges, files) = read_setup(setup)
        # Create containers
        print("Start nodes using docker containers")
        create_nodes(nodes)
        # Connecting all dockers in bridges
        print("Interconnect nodes")
        create_bridges(bridges, nodes=nodes,p4=True)
        print("Applying IP addressing scheme")
        set_addresses(bridges)
        print("Copying files and folders")
        copy_files(files)
        if setup == "l2-reflector":
          r('docker exec -ti BMv2 p4c --target bmv2 --arch v1model --std p4-16 l2-reflector.p4')
          r('docker exec -ti BMv2 sysctl net.ipv4.icmp_echo_ignore_all=1')
        if setup == "l2-forwarding":
          r('docker exec -ti BMv2 p4c --target bmv2 --arch v1model --std p4-16 l2-forwarding.p4')
          r('docker exec -ti BMv2 sysctl net.ipv4.icmp_echo_ignore_all=1')
        
  
        # Connecting to internet via lab. Pretty much hardcoded          
        #set_internet('internet',h_if,'internal','192.168.1.100/24','192.168.1.1')
        #r('docker exec -ti server rc-service nginx start')

def setup_routing(h_if):
    try:
        ns_root.shutdown()
    except:
        print('[*] Did not shutdown cleanly, trying again')
        docker_clean()
    finally:
        docker_clean()
        # Stop IP forwarding on Debian
        r('sysctl -w net.ipv4.ip_forward=0')    
        # Reading network setup
        (nodes,bridges) = read_setup("routing")
        # Create containers
        create_nodes(nodes)
        # Connecting all dockers in bridges
        create_bridges(bridges)
        set_addresses(bridges)  

        # Enable IP forwarding in all routers - yes hardcoding :-(
        for i in range(4):
            k = str(i+1)
            r('docker exec -ti router%s sysctl -w net.ipv4.ip_forward=1' % k)
    
           
        # Select config file and start service in router 1 and 2
        for i in range(2):
            k=str(i+1)
            r('docker exec -ti router%s mv /etc/frr/ripd%s.conf /etc/frr/ripd.conf' % (k,k))
            r('docker exec -ti router%s mv /etc/frr/zebra%s.conf /etc/frr/zebra.conf' % (k,k))
            #r('docker exec -ti router%s mv /etc/frr/daemons34334 /etc/frr/daemons' % k)
            #r('docker exec -ti router%s supervisorctl start frr' % k)
            r('docker exec -ti router%s service frr start' % k)
            


def setup_QoS(h_if):
    try:
        ns_root.shutdown()
    except:
        print('[*] Did not shutdown cleanly, trying again')
        docker_clean()
    #finally:
    #    docker_clean()
        # Stop IP forwarding on Debian
    r('sysctl -w net.ipv4.ip_forward=0')    
    # Reading network setup
    (nodes,bridges) = read_setup("QoS")
    # Create containers
    create_nodes(nodes)
    create_bridges(bridges)
    #Manually connect switches to internal bridges
    r("ip netns exec sw1 brctl addif sw1 sw3")
    r("ip netns exec sw2 brctl addif sw2 sw3")
    
    try:
        r('ip netns exec client1 ip link set sw1 address aa:14:c2:76:80:17')
        r('ip netns exec client2 ip link set sw1 address aa:14:c2:76:80:19')
        r('ip netns exec server ip link set sw2 address aa:14:c2:76:80:16')
        r('ip netns exec internet ip link set sw2 address aa:14:c2:76:80:22')
    except:
        print("Hopefully not relevant")


    
    set_addresses(bridges)  
    set_internet('internet',h_if,'sw1','192.168.1.100/24','192.168.1.1')
    # Set default gateway manually to client1 and client1
    # Very ugly and hardcoded
    r('ip netns exec client1 ip route add default via 192.168.1.1')
    r('ip netns exec client2 ip route add default via 192.168.1.1')
    r('docker exec -ti server service nginx start')

