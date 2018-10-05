#!/bin/sh

red="\033[0;31m"
yellow="\033[1;33m"
green="\033[1;32m"
reset="\033[0m"

if [ $# -ne 5 ]; then
  echo -e "Use: ./attackPreComputation.sh [NumberOfDesiredNetworkTraces] [payloadMaxLength] [AttackerIP] [serverIP] [networkInterface]\n"
  echo -e "Description: 'attackPreComputation.sh' does all the necessary precomputation requiered to carry out the network analysis attack"
  exit 1
fi

numberOfNetworkTracesDesired=$1
payloadMaxLength=$2
attackerIP=$3
serverIP=$4
interface=$5

./traceBuilderManager.sh $numberOfNetworkTracesDesired $payloadMaxLength $attackerIP $serverIP $interface
python dbBuilder.py $numberOfNetworkTracesDesired $attackerIP $serverIP

exit 0
