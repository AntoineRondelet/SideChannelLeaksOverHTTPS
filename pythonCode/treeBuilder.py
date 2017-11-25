import requests
import sys


def apiCall(payload):
  payload = sys.argv[1] # Only for testing: For prod, use the generator module
  url = "https://www.kayak.com/mv/marvel?f=h&where=" + payload + "&s=58&lc_cc=US&lc=en&v=v2&cv=4"
  session = requests.Session()
  session.get(url)
  response = session.get(url)

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
apiCall("")
