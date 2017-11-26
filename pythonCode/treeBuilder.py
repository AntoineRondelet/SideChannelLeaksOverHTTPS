import requests
import sys

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

#usage : 1st arg=payload, 2nd arg=number of iterations
#iterating same API calls over and over to see if size constant
def autoGenerate():
	size_array=[]
	s = getSession()
	for i in range(0,int(sys.argv[2])):
		r = apiCall(s, sys.argv[1])
		size_array.append(r.headers['Content-Length'])
		sys.stdout.write('\r')
		sys.stdout.write('{:d}%'.format(i*100/int(sys.argv[2])))
		sys.stdout.flush()
	print(size_array)
	print("All values identical : ")
	print(size_array.count(size_array[0]) == len(size_array))

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
if len(sys.argv)==3:
	autoGenerate()
else:
	manualGenerate()
