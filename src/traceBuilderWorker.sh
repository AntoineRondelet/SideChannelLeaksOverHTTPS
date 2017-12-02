#!/bin/bash

red="\033[0;31m"
yellow="\033[1;33m"
green="\033[1;32m"
reset="\033[0m"

if [ $# -ne 4 ]; then
  echo -e "Use: ./attackTraffic.sh [NumberOfThisNetworkTrace] [AttackerIP] [serverIP] [networkInterface]\n"
  echo -e "Description: 'attackTraffic.sh' launches a given number of network analysis by sniffing the attacker's traffic. This aims to build the database necessary to carry out the attack on a victim"
  exit 1
fi

numberOfTheTraceToBuild=$1
attackerIP=$2
serverIP=$3
interface=$4

pcapFileNamePrefix="./trafficRecords/analysis"
timingFileNamePrefix="./trafficRecords/timing"

pcapFileName=$pcapFileNamePrefix$numberOfTheTraceToBuild".pcap"
timingFileName=$timingFileNamePrefix$numberOfTheTraceToBuild".json"
sudo tcpdump -vv -i $interface -n host $serverIP and host $attackerIP -w $pcapFileName & # Launch TCPDUMP in background to prevent the main thread from being blocked
tcpDumpPID=$!
python apiCaller.py $timingFileName # When this ends we stop TCP dump
sudo kill $tcpDumpPID
exit 0 # Indicate the end of this trace building
