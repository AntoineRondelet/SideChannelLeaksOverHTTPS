#!/bin/bash

red="\033[0;31m"
yellow="\033[1;33m"
green="\033[1;32m"
reset="\033[0m"

if [ $# -ne 4 ]; then
  echo -e "Use: ./attackTraffic.sh [NumberOfDesiredNetworkTraces] [AttackerIP] [serverIP] [networkInterface]\n"
  echo -e "Description: 'attackTraffic.sh' launches a given number of network analysis by sniffing the attacker's traffic. This aims to build the database necessary to carry out the attack on a victim"
  exit 1
fi

numberOfNetworkTracesDesired=$1
attackerIP=$2
serverIP=$3
interface=$4
pids=''
results=''

for i in $(seq $numberOfNetworkTracesDesired); do
  ./traceBuilderWorker.sh $i $attackerIP $serverIP $interface # Cannot be launched in parallel otherwise traffic superpose
done

exit 0 # Indicate the end of this trace building
