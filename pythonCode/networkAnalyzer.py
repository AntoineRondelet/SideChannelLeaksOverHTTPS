#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pyshark
import requests
import time
import multiprocessing

GLOBAL_VICTIM_IP = ''
GLOBAL_SERVER_IP = ''

class trafficWeight:
  def __init__(self):
    self.request = 0
    self.response = 0

def packetProcessing(packet):
  try:
    # Verify the different layers information of the packet we manipulate
    layersName = []
    for i in range(len(packet.layers)):
      layersName.append(packet.layers[i]._layer_name)

    # Get the packet number
    packetNumber = int(packet.number)

    # Check whether the packet has information of the 4 network layers ETH, IP, TCP, SSL
    if len(set(['eth', 'ip', 'tcp', 'ssl']).intersection(layersName)) == 4:
      src = packet.ip.src
      dst = packet.ip.dst
      if src == GLOBAL_VICTIM_IP:
        print("[FRAME: %d] === REQUEST (From %s, To: %s) ==== \t\t OUT =========>" % (packetNumber, src, dst))
        print(" -- Encrypted Data Length: %s " % packet.ssl.record_length)
        print(" -- Time of sniffing: %s" % packet.sniff_time)
        print("=====================================================================\n")

      elif src == GLOBAL_SERVER_IP:
        print("[FRAME: %d] === RESPONSE (From %s, To: %s) ==== \t\t IN <=========" % (packetNumber, src, dst))
        print(" -- Encrypted Data Length: %s" % packet.ssl.record_length)
        print(" -- Time of sniffing: %s" % packet.sniff_time)
        print("======================================================================\n")
    elif len(set(['eth', 'ip', 'tcp', 'ssl']).intersection(layersName)) == 3 and 'ssl' not in layersName: # No SSL packet
      if packet.ip.src == GLOBAL_VICTIM_IP:
        # tcp.analysis_acks_frame returns "[This is an ACK to the segment in frame: 3]", so it returns the segments for which this segment is a ACK
        print("[FRAME: %d] === CLIENT ACK: This is a ACK to the segment in frame: %s \t\t [CLIENT ACK]" % (packetNumber, packet.tcp.analysis_acks_frame))
        #traffic.request = requestSize
        #traffic.response = responseSize
        # When the client ACK, we have the entire response, so we can have the total weight
        #return traffic
      elif packet.ip.src == GLOBAL_SERVER_IP:
        print("[FRAME: %d] === SERVER ACK: This is a ACK to the segment in frame: %s \t\t [SERVER ACK]" % (packetNumber, packet.tcp.analysis_acks_frame))
      else:
        print("[FRAME: %d] == unhandled TCP packet (%s)" % (packetNumber, packet.pretty_print))
    elif len(set(['eth', 'ip', 'tcp', 'ssl']).intersection(layersName)) == 2 and 'tcp' not in layersName and 'ssl' not in layersName:
      # Note: The checks "and 'tcp' not in layersName and 'ssl' not in layersName" are useless since if TCP is not in the packet
      # then SSL is obviously not either. So, if the length of the intersection of the 2 sets provides enough information
      # If the intersection is 2, it cannot be TCP and SSL alone, since these layers are on top of IP and ETH, the latter should be included
      print("[FRAME: %d] == This packet is not a TCP packet ! (%s)" % (packetNumber, packet.pretty_print))
    elif len(set(['eth', 'ip', 'tcp', 'ssl']).intersection(layersName)) == 1:
      print("[FRAME: %d] == This packet is not an IP packet ! (%s)" % (packetNumber, packet.pretty_print))
  except AttributeError, e:
    print("[Handled error] ==> ", str(e))

def calculateTrafficWeight(interfac, victimIP, serverIP):
  bpFilters = 'host ' + victimIP + ' and host ' + serverIP

  traffic = trafficWeight()
  requestSize = 0
  responseSize = 0

  capture = pyshark.LiveCapture(interface=interfac, bpf_filter=bpFilters)
  capture.apply_on_packets(packetProcessing)


## main ##############@
if len(sys.argv) < 3:
    print("""Invalid number of arguments
Use: python test.py [interface] [victimIP] [serverIP]""")
    sys.exit(0)

# Defining the environment
interfac = sys.argv[1]
victimIP = sys.argv[2]
serverIP = sys.argv[3] # Obtained after a traceroute

GLOBAL_VICTIM_IP = victimIP
GLOBAL_SERVER_IP = serverIP

calculateTrafficWeight(interfac, victimIP, serverIP)

# TODO:
# Here once we manage to exploit the packets, we should be able to:
# 2) According to the previous result (request/response): if this is a request then --> store the timestamp and use it to catch the packet corresponding to the associated response, if this is a response collect all the packets of the response +  get their size and build the total size of the response
# 3) Using the total size of the response, get the node of the tree we built in the "treeBuilder" --> this tree is a labelled tree, which label is the size of the response from the server -> so by using the size we computed, we could do a lookup and extract the good node.
# Store the value of the node we found and iterate.
