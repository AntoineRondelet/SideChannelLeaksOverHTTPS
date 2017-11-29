# This file is used by the attacker to sniff the network traffic of the victim and
# Exploit the pre-built tree in order to infer the user input on a page protected
# by encrypted traffic (TLS/SSL)

import sys
import pyshark

if len(sys.argv) < 3:
    print("""Invalid number of arguments
Use: python test.py [interface] [victimIP] [serverIP]""")
    sys.exit(0)

# Defining the environment
interfac = sys.argv[1]
victimIP = sys.argv[2]
serverIP = sys.argv[3] # Obtained after a traceroute

# Build filters: Here we are only interested in capturing the encrypted traffic between the victim machine and the server hosting the webapp
bpFilters = 'host ' + victimIP + ' and host ' + serverIP

capture = pyshark.LiveCapture(interface=interfac, bpf_filter=bpFilters)
for packet in capture.sniff_continuously():
  try:
    print(packet.ssl)
    src = packet.ip.src
    dst = packet.ip.dst
    print("Source: ", src)
    print("Destination: ", dst)
    print("Length: ", packet.length)
    print("Time: ", packet.time)
    print("Frame info: ", dir(packet.frame_info))
    print("Transport Layer: ", dir(packet.transport_layer))
  except AttributeError:
    try:
      print("This packet is not an encrypted packet !")
      if packet.ip.src == victimIP:
        print("Maybe an ACK packet")
        print(packet)
      else:
        print("Probably not an ACK packet...")
    except AttributeError:
      print("This packet is not an IP packet !")


# TODO:
# Here once we manage to exploit the packets, we should be able to:
# 1) Read the source and destination, and infer whether this is a request from the user or a response from the server
# 2) According to the previous result (request/response): if this is a request then --> store the timestamp and use it to catch the packet corresponding to the associated response, if this is a response collect all the packets of the response +  get their size and build the total size of the response
# 3) Using the total size of the response, get the node of the tree we built in the "treeBuilder" --> this tree is a labelled tree, which label is the size of the response from the server -> so by using the size we computed, we could do a lookup and extract the good node.
# Store the value of the node we found and iterate.
