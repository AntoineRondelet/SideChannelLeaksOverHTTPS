#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This module reads and analyses all the traffic records generated by attackTraffic and does a mean for each paylaod and maps every payload with the computed traffic weight. The next step would be to tak ethe output of this module and use it along with the network analyser to actually infer the user input
import pyshark
import json
import utils
import sys


def tracePayloadMapper(capture, analysisNumber):
  fileName = './trafficRecords/timing' + str(analysisNumber) + '.json'
  timingFile = open(fileName,'r')

  # Extract the content of the timing file into a variable
  timingInfo = json.load(timingFile)

  lenCapture = 0
  for i in capture:
    lenCapture += 1

  indexBegin = 0
  indexEnd = indexBegin
  trafficMapping = dict()

# Iterate over the timingInfo list to map the traffic weight to the payload
  for info in timingInfo:
    for key in info:
      payload = key
      requestTime = info[key]["requestTime"]
      responseTime = info[key]["responseTime"]
      packet = capture[indexBegin]

      # Find the packets that interest us (we do it to go through the network trace only once and have better perfs)
      while packet.sniff_time.isoformat() <= requestTime and indexBegin < (lenCapture - 1):
        indexBegin = indexBegin + 1
        packet = capture[indexBegin]

      indexEnd = indexBegin
      while packet.sniff_time.isoformat() <= responseTime and indexEnd < (lenCapture - 1):
        indexEnd = indexEnd + 1
        packet = capture[indexEnd]

      interval = utils.PacketInterval()
      interval.firstPacket = indexBegin
      interval.lastPacket = indexEnd - 1
      trafficMapping[payload] = interval

      indexBegin = indexEnd

  # The output of this function is a dictionnary in the form {PAYLOAD: packetInterval}
  # The idea is that we want to have: "Payload: m, Network traffic interval[154, 157]" which means
  # That packets number 154 to 157 of the network trace represent the traffic (request and response)
  # Generated when the user pressed the keytroke "m"
  return trafficMapping


## Returns the packets that have sniffed between specific times
def computeRequestResponseWeightForSpecificPayload(victimIP, serverIP, analysisNumber):
  pcapFileName = './trafficRecords/analysis' + str(analysisNumber) + '.pcap'
  capture = pyshark.FileCapture(pcapFileName)

  resultMapping = tracePayloadMapper(capture, analysisNumber)
  requestPackets = 0
  responsePackets = 0

  resultTrafficWeight = dict()

  for payload, interval in resultMapping.iteritems():
    packetBegin = interval.firstPacket
    packetEnd = interval.lastPacket
    packetsMappedToPayload = []
    for i in range(packetBegin, packetEnd + 1): # We do packet end + 1, in order to include packetEnd index in the range
      packet = capture[i]
      try:
        src = packet.ip.src
        dst = packet.ip.dst
      except AttributeError, e:
        print("[dbBuilder.py -> findRequestResponse: ERROR]: Not a IP packet (%s)" % str(e))
        continue
      if src == victimIP and dst == serverIP: # REQUEST
        try:
          if packet.ssl.record_content_type == '23':
            requestPackets += int(packet.ssl.record_length)
        except AttributeError, e:
          print("[dbBuilder.py -> findRequestResponse: ERROR]: Request is not a TLS packet (%s)" % str(e))
          continue
      elif src == serverIP and dst == victimIP: # RESPONSE
        try:
          if packet.ssl.record_content_type == '23':
            responsePackets += int(packet.ssl.record_length)
        except AttributeError, e:
          print("[dbBuilder.py -> findRequestResponse: ERROR]: Response is not a TLS packet (%s)" % str(e))
          continue

    weight = utils.TrafficWeight()
    weight.request = requestPackets
    weight.response = responsePackets
    resultTrafficWeight[payload] = weight

    requestPackets = 0
    responsePackets = 0
  return resultTrafficWeight # Maps every payload to the corresponding traffic weight


## MAIN #########################
def work(traceToAnalyze, attackerIP, serverIP, queue):
  result = computeRequestResponseWeightForSpecificPayload(attackerIP, serverIP, traceToAnalyze)
  weightPayloadMapping = []
  for payload, weights in result.iteritems():
    dataRow = {payload: {'requestWeight': weights.request, 'responseWeight': weights.response}}
    weightPayloadMapping.append(dataRow)

  resultFileName = "./trafficRecords/results/resultTrace" + str(traceToAnalyze) + ".json"
  outputFile = open(resultFileName,'w+')
  try:
    json.dump(weightPayloadMapping, outputFile, indent=4)
  except:
    queue.put(1)
  finally:
    outputFile.close()
  queue.put(0)
