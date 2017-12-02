import requests
import sys

def getSession():
  session = requests.Session()
  session.get("https://www.kayak.com/flights")
  return session

def apiCall(session, payload):
  url = 'https://www.kayak.com/mv/marvel?f=h&where=' + payload + '&s=58&lc_cc=US&lc=en&v=v2&cv=4'
  print("Send request to: ", url)
  r = session.get(url)
  r.raise_for_status()
  return r

def manualGenerate():
	#Manual payload this would come from payloadgenerator
  payloads = generator.generateStrings(1)
  session = getSession()
  for payload in payloads:
    print("Press enter to send payload '%s'" % payload)
    raw_input()
    response = apiCall(session, payload)
    print("Size of response is ", response.headers['Content-Length'])

## Main ########
manualGenerate()
