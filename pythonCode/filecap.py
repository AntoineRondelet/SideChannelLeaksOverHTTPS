import sys
import pyshark
kayakIP='151.101.72.231'
victimIP='110.76.119.38'
cap = pyshark.FileCapture(sys.argv[1])
for i,pkt in enumerate(cap):
	if pkt.ip.src==kayakIP and pkt.ip.dst==victimIP and 'SSL' in pkt:
		dir(pkt)
		try:
			print(pkt.ssl.record_length)
		except AttributeError as e:
			pass
# print(dir(cap[63].ssl.record_length))
