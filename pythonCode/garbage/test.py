#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pyshark

# Data structure used to store the traffic weight
# Associated to a request and a response
class trafficWeight:
  def __init__(self):
    self.request = 0
    self.response = 0

# Function applied on each packet
def packetProcessing(packet):
  print("CATCH ONE PACKET")

def calculateTrafficWeight(interfac, victimIP, serverIP):
  bpFilters = 'host ' + victimIP + ' and host ' + serverIP

  capture = pyshark.LiveCapture(interface=interfac, bpf_filter=bpFilters)
  capture.apply_on_packets(packetProcessing)


## Main ############
if len(sys.argv) < 3:
    print("""Invalid number of arguments
Use: python test.py [interface] [victimIP] [serverIP]""")
    sys.exit(0)

interfac = sys.argv[1]
victimIP = sys.argv[2]
serverIP = sys.argv[3]

calculateTrafficWeight(interfac, victimIP, serverIP)

# TODO:
# Here once we manage to exploit the packets, we should be able to:
# 2) According to the previous result (request/response): if this is a request then --> store the timestamp and use it to catch the packet corresponding to the associated response, if this is a response collect all the packets of the response +  get their size and build the total size of the response
# 3) Using the total size of the response, get the node of the tree we built in the "treeBuilder" --> this tree is a labelled tree, which label is the size of the response from the server -> so by using the size we computed, we could do a lookup and extract the good node.
# Store the value of the node we found and iterate.
