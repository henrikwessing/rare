#!/bin/bash
set -e

# Build RARE P4 program for BMv2
cd /rare-bmv2/02-PE-labs/p4src
# Adjust path if necessary (this example uses a P4 lab or main RARE .p4 file)



#p4c --target bmv2 --arch v1model --std p4-16 router.p4 

# Run BMv2 with RARE JSON and enable P4Runtime gRPC
simple_switch_grpc router.json --device-id 0 --log-console -- --grpc-server-addr 0.0.0.0:50051 &
#  --device-id 0 \
#  router.json  \
#  --log-console \
#  --no-p4 \
#  --grpc-server-addr 0.0.0.0:50051 \

sleep 3

bash

# Launch FreeRtr as the control plane
cd /freertr
java -Xmx512m -jar rtr.jar router #/p4/freertr.cfg
