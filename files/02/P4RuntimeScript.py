import grpc
import threading
import queue
from p4.v1 import p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc
from p4helper import P4InfoHelper  # Make sure this helper exists and works

# Paths to compiled P4 artifacts
P4INFO_PATH = "p4.info.txt"
DEVICE_CONFIG_PATH = "l2-forwarding.json"

# gRPC target and settings
GRPC_ADDR = "localhost:50051"
DEVICE_ID = 0
ELECTION_ID = p4runtime_pb2.Uint128(high=0, low=1)

# Queue for messages sent via stream
msg_queue = queue.Queue()

def request_generator():
    while True:
        msg = msg_queue.get()
        if msg is None:
            break
        yield msg

# Load P4Info
p4info_helper = P4InfoHelper(P4INFO_PATH)

# Connect to the switch via gRPC
channel = grpc.insecure_channel(GRPC_ADDR)
stub = p4runtime_pb2_grpc.P4RuntimeStub(channel)

# Start the bi-directional stream
stream = stub.StreamChannel(request_generator())

# Start arbitration
arb_req = p4runtime_pb2.StreamMessageRequest()
arb_req.arbitration.device_id = DEVICE_ID
arb_req.arbitration.election_id.CopyFrom(ELECTION_ID)
msg_queue.put(arb_req)

# Handle arbitration response in a background thread
def handle_responses():
    for response in stream:
        if response.HasField("arbitration"):
            if response.arbitration.status.code == 0:
                print("✅ Became master controller")
            else:
                print("⚠️ Not master: code =", response.arbitration.status.code)

threading.Thread(target=handle_responses, daemon=True).start()

# Set the forwarding pipeline
with open(DEVICE_CONFIG_PATH, "rb") as f:
    device_config = f.read()

stub.SetForwardingPipelineConfig(
    p4runtime_pb2.SetForwardingPipelineConfigRequest(
        device_id=DEVICE_ID,
        role_id=0,
        election_id=ELECTION_ID,
        action=p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT,
        config=p4runtime_pb2.ForwardingPipelineConfig(
            p4info=p4info_helper.p4info,
            p4_device_config=device_config
        )
    )
)

print("✅ Forwarding pipeline set successfully")

# Insert example MAC forwarding rule
def insert_mac_entry(mac, port):
    entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.mac",
        match_fields={"hdr.ethernet.dstAddr": mac},
        action_name="MyIngress.forward",
        action_params={"outgoing_port": port}
    )
    try:
        stub.Write(p4runtime_pb2.WriteRequest(
            device_id=DEVICE_ID,
            updates=[p4runtime_pb2.Update(
                type=p4runtime_pb2.Update.INSERT,
                entity=p4runtime_pb2.Entity(table_entry=entry)
            )]
        ))
        print(f"✅ Inserted rule: {mac} → port {port}")
    except grpc.RpcError as e:
        print(f"❌ gRPC Error: {e.code()} - {e.details()}")

# Example MAC forwarding rules
insert_mac_entry("00:00:00:00:01:01", 1)
insert_mac_entry("00:00:00:00:02:02", 2)
