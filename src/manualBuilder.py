#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from multiprocessing import Process, Queue
import json
import utils

# main #########
if len(sys.argv) < 2:
  print("""Use: python manualBuilder.py [numberOfTracesToUse]""")
  exit(1)

numberOfTracesToUse = int(sys.argv[1])
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

# We did the sum of all our network traces. Now we need to divide it to have a mean
computedPayloadMapping = []
for payload, weights in resultDB.iteritems():
  resultRequestWeight = weights.request/numberOfTracesToUse # Here we want to keep integer packet number
  resultResponseWeight = weights.response/numberOfTracesToUse # Here we want to keep integer packet number
  dataRow = {payload: {'requestWeight': resultRequestWeight, 'responseWeight': resultResponseWeight}}
  computedPayloadMapping.append(dataRow)

resultFileName = "./trafficRecords/results/database.json"
outputFile = open(resultFileName,'w+')
try:
  json.dump(computedPayloadMapping, outputFile, indent=4)
finally:
  outputFile.close()

print(" ======= [SUCCESS] Precomputation done: Database ready to use ======= ")
