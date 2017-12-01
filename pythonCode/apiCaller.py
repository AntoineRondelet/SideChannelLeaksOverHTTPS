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

def manualGenerate():
	#Manual payload this would come from payloadgenerator
	payloads=['a','b','c','d','e','f','g','h','i']
	s = getSession()
	for pld in payloads:
		print("Press enter to send payload '%s'"%(pld))
		raw_input()
		r = apiCall(s, pld)
		print("Size of response is ",r.headers['Content-Length'])

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
    json.dump(timePayloadMapping, outputFile, indent=4) # Retrieval: d = json.load(open(filePath)
  finally:
    outputFile.close()

# To decomment and TODO:
# import generator
#
# def buildTree():
#   maxLength = 3 --> See after how many characters in the search the suggestion list of kayak returns 1 element --> This would help us doing the right amount of requests (since we will do as many requests as we have payloads, but since payloads are made of letters from the alphabet, we will have 26^n requests. So this grows very very fast..., we should limit it !)
#   payloads = generator.generateStrings(3)
# for payload in range(payloads):
# apiResponse = apiCall(payload)
# --> Now we should implement the tree building !
# Note: For the tree buiding we can use nltk: http://www.nltk.org/_modules/nltk/tree.html

# "main"
if len(sys.argv) < 2:
  print("""Invalid number of arguments
Use: python treeBuilder.py [fileName]""")
  sys.exit(0)

fileNameToMatchPayloadAndTime = sys.argv[1]
generateTraffic(fileNameToMatchPayloadAndTime)
