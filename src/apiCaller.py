import requests
import sys
import generator
import time
import datetime
import json

def getSession():
  	session = requests.Session()
 	session.get("https://www.kayak.com/flights")
	return session

def apiCall(session, payload):
  	url = "https://www.kayak.com/mv/marvel?f=h&where=" + payload + "&s=58&lc_cc=US&lc=en&v=v2&cv=4"
 	r = session.get(url)
	r.raise_for_status()
	return r

def generateTraffic(fileName):
  timePayloadMapping = []
  # Only airports IDs
  payloads = generator.generateStrings(1)
  session = getSession()
  for payload in payloads:
    requestTime = datetime.datetime.now().isoformat()
    response = apiCall(session, payload)
    responseTime = datetime.datetime.now().isoformat()
    responseLength = response.headers['Content-Length']
    dataRow = {payload: {'requestTime': requestTime, 'responseLength': responseLength, 'responseTime': responseTime}}
    timePayloadMapping.append(dataRow)
    print("[INFO]: Request sent for payload %s, response length: %s" % (payload, responseLength))
    time.sleep(0.50)
  outputFile = open(fileName,'w+')
  try:
    json.dump(timePayloadMapping, outputFile, indent=4)
  finally:
    outputFile.close()

## Main ###################################
if len(sys.argv) < 2:
  print("""Invalid number of arguments
Use: python treeBuilder.py [fileName]""")
  sys.exit(0)

fileNameToMatchPayloadAndTime = sys.argv[1]
generateTraffic(fileNameToMatchPayloadAndTime)
