#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceAnalyzer
import sys
from multiprocessing import Process, Queue
import json
import utils

# main #########
if len(sys.argv) < 4:
  print("""Use: python dbBuilder.py [numberOfTracesToUse] [attackerIP] [serverIP]""")
  exit(1)

numberOfTracesToUse = int(sys.argv[1])
attackerIP = sys.argv[2]
serverIP = sys.argv[3]

# Retrieve the return value of the threads
queue = Queue()

threads = []
# Create the good number of threads
for traceNumber in range(numberOfTracesToUse):
  # We do traceNumber+1 because range(n) goes from 0 to n-1
  thread = Process(target=traceAnalyzer.work, args=(traceNumber+1, attackerIP, serverIP, queue))
  threads.append(thread)

# Launch the threads
for j in threads:
  j.start()

# Stop the threads
for k in threads:
  k.join()

# Verify that our threads finished smoothly
for l in range(numberOfTracesToUse):
  threadRes = queue.get()
  if threadRes != 0:
    print("[ERROR]: Something went wrong in one thread")
    sys.exit(1) # Exit with error

# Build the final file matching all payloads with the mean of their traffic in the different traces
resultFilesPrefix = './trafficRecords/results/resultTrace'
resultDB = dict()

# This for loop will take a while since it processes lots of data
for traceNumber in range(numberOfTracesToUse):
  fileName = './trafficRecords/results/resultTrace' + str(traceNumber+1) + '.json'
  resultFile = open(fileName,'r')
  resultInfo = json.load(resultFile)
  for info in resultInfo:
    for key in info:
      payload = key
      requestWeight = info[key]["requestWeight"]
      responseWeight = info[key]["responseWeight"]
      if payload in resultDB:
        weight = resultDB[payload]
        weight.request += requestWeight
        weight.response += responseWeight
        resultDB[payload] = weight
      else:
        weight = utils.TrafficWeight()
        weight.request = requestWeight
        weight.response = responseWeight
        resultDB[payload] = weight

computedPayloadMapping = []
for payload, weights in resultDB.iteritems():
  dataRow = {payload: {'requestWeight': weights.request, 'responseWeight': weights.response}}
  computedPayloadMapping.append(dataRow)

resultFileName = "./trafficRecords/results/database.json"
outputFile = open(resultFileName,'w+')
try:
  json.dump(computedPayloadMapping, outputFile, indent=4)
finally:
  outputFile.close()

print("Database ready to use")
