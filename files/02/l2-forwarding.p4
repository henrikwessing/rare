#include <core.p4>
#include <v1model.p4>

// Define type for mac address as used more than twice

typedef bit<48> t_macAddr;

// Define packet formats and headers

header ethernet_t {
  t_macAddr dstAddr;
  t_macAddr srcAddr;
  bit<16> etherType;
}

struct headers {
  ethernet_t ethernet;
}

// Define any metadata

struct metadata {
  // User-defined metadata
}

// Input parser

parser MyParser(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
  state start {
    transition parse_ethernet;
  }

  state parse_ethernet {
    packet.extract(hdr.ethernet);
    transition accept;
  }
}

// Checksum verification

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
  apply {  }
}

// Ingress processing
// This is where the current changes are 

control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
  action drop() {
    mark_to_drop(standard_metadata);
  }

  action forward(bit<9> outgoing_port) {
    standard_metadata.egress_spec = outgoing_port;
  }

  action broadcast(bit<16> mgrp) {
	standard_metadata.mcast_grp = mgrp;
  }


  table mac {
    key = {
      hdr.ethernet.dstAddr: exact;
    }

    actions = {forward; drop;broadcast;}
    size = 16;
    default_action = drop;
  }
  
  apply {
    mac.apply();
  }	
}

// Egress processing

control MyEgress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    apply {
    }
}

// Checksum calculation

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply {
    }
}

// Deparser - headers have to be parsed to teh original frame

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
    }
}

// Compiling the switch 

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
