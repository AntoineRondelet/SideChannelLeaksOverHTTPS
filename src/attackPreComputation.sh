#!/bin/bash

red="\033[0;31m"
yellow="\033[1;33m"
green="\033[1;32m"
reset="\033[0m"

if [ $# -ne 4 ]; then
  echo -e "Use: ./attackPreComputation.sh [NumberOfDesiredNetworkTraces] [AttackerIP] [serverIP] [networkInterface]\n"
  echo -e "Description: 'attackPreComputation.sh' does all the necessary precomputation requiered to carry out the network analysis attack"
  exit 1
fi

numberOfNetworkTracesDesired=$1
attackerIP=$2
serverIP=$3
interface=$4

./traceBuilderManager.sh $numberOfNetworkTracesDesired $attackerIP $serverIP $interface
python dbBuilder.py $numberOfNetworkTracesDesired $attackerIP $serverIP

exit 0
