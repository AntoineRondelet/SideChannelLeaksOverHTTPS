import pyshark

capture = pyshark.FileCapture('./myFirstCapture.cap')
capture.sniff(timeout=50)
capture
for packet in capture.sniff_continuously(packet_count=5):
  print 'Just '

