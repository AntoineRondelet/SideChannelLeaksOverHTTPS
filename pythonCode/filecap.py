import sys
import pyshark
cap = pyshark.FileCapture(sys.argv[1], only_summaries=True)
print(dir(cap))
for pkt in cap:
	print(pkt)
