ip link add veth251 type veth peer name veth250
ip link set veth250 up 
ip link set veth251 up
./pcapInt.bin veth251 22709 127.0.0.1 22710 127.0.0.1
