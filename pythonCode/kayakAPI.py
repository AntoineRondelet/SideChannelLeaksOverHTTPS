import requests
import sys
payload = "https://www.kayak.com/mv/marvel?f=h&where="+sys.argv[1]+"&s=58&lc_cc=US&lc=en&v=v2&cv=4"
s = requests.Session()
s.get(payload)
r = s.get(payload)
