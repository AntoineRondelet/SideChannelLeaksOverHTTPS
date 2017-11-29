import requests
import sys
import generator
import time

def getSession():
  	session = requests.Session()
 	session.get("https://www.kayak.com/flights")
	return session

def apiCall(session, payload):
	proxies = {'https': '143.248.241.215:8888',}
  	url = "https://www.kayak.com/mv/marvel?f=h&where=" + payload + "&s=58&lc_cc=US&lc=en&v=v2&cv=4"
 	# r = session.get(url,proxies=proxies,verify=False)
 	r = session.get(url,verify=False)
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
def autoSingleGenerate():
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

def alphabetGenerate():
	payloads = generator.generateStrings(int(sys.argv[1]))
	time_array=[]
	s = getSession()
	for i, pld in enumerate(payloads):
		ms = time.time()*1000.0
		r=apiCall(s, pld)
		time_array.append(ms)
		sys.stdout.write('\r')
		sys.stdout.write('{:d}%'.format(i*100/len(payloads)))
		sys.stdout.flush()
	total=0
	for i in range(len(time_array)-1):
		total+=time_array[i+1]-time_array[i]
	print(total/len(time_array)-1)

# USAGE :
# 1) python apiCaller.py --> Sending payload manually
# 2) python apiCaller.py <n> --> sending all possible words of length <n> and measuring average time between requests
# 3) python apiCaller.py <string> <n> --> sending the strings <string> <n> times in a row
if len(sys.argv)==3:
	autoSingleGenerate()
elif len(sys.argv)==2:
	alphabetGenerate()
else:
	manualGenerate()
