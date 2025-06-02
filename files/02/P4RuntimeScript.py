import grpc
import p4runtime_lib.helper
import p4runtime_lib.bmv2

# Load P4Info file
p4info_helper = p4runtime_lib.helper.P4InfoHelper('path/to/p4info.txt')

# Define the address and port of the switch
address = 'localhost:50051'

# Create a channel and a stub
channel = grpc.insecure_channel(address)
stub = p4runtime_lib.bmv2.Bmv2Stub(channel)

# Define the device ID
device_id = 0

# Define the table entry to add
table_entry = p4info_helper.buildTableEntry(
table_name="MyIngress.my_table",
match_fields={"hdr.ethernet.dstAddr": "00:00:00:00:00:01"},
action_name="MyIngress.my_action",
action_params={"port": 1}
)

# Write the table entry to the switch
request = p4runtime_lib.helper.buildWriteRequest(
device_id=device_id,
updates=[p4runtime_lib.helper.buildUpdate(
entity=p4runtime_lib.helper.buildEntity(table_entry),
type=p4runtime_lib.helper.UpdateType.INSERT
)]
)
response = stub.Write(request)

# Print the response
print(response)

# Define the table entry to remove
table_entry = p4info_helper.buildTableEntry(
table_name="MyIngress.my_table",
match_fields={"hdr.ethernet.dstAddr": "00:00:00:00:00:01"}
)

# Write the table entry to the switch
request = p4runtime_lib.helper.buildWriteRequest(
device_id=device_id,
updates=[p4runtime_lib.helper.buildUpdate(
entity=p4runtime_lib.helper.buildEntity(table_entry),
type=p4runtime_lib.helper.UpdateType.DELETE
)]
)
response = stub.Write(request)

# Print the response
print(response)
