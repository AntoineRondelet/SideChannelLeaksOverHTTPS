#!/bin/bash

red="\033[0;31m"
yellow="\033[1;33m"
green="\033[1;32m"
reset="\033[0m"

if [ $# -ne 1 ]; then
  echo -e "Use: ./attackTraffic.sh [NumberOfNetworkAnalysisToLaunch]\n"
  echo -e "Description: 'attackTraffic.sh' launches a given number of network analysis by sniffing the attacker's traffic. This aims to build the database necessary to carry out the attack on a victim"
  exit 1
fi

numberIterations=$1
serverIP="151.101.72.231"
attackerIP="110.76.118.16"
interface="en0"

pcapFileNamePrefix="./trafficRecords/analysis"
timingFileNamePrefix="./trafficRecords/timing"
for i in $(seq $numberIterations); do
  pcapFileName=$pcapFileNamePrefix$i".pcap"
  timingFileName=$timingFileNamePrefix$i".json"
  sudo tcpdump -vv -i $interface -n host $serverIP and host $attackerIP -w $pcapFileName & # Launch TCPDUMP in background to prevent the main thread from being blocked
  tcpDumpPID=$!
  python apiCaller.py $timingFileName # When this ends we stop TCP dump
  sudo kill $tcpDumpPID
done
