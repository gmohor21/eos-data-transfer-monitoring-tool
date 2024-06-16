#!/bin/bash

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -i|--instance)
      INSTANCE="$2"
      shift # past argument
      shift # past value
      ;;
    -e|--eosreport)
        EOSREPORTFILE="$2"
        shift
        shift
        ;;
    -h|--help)
      echo "usage: ./launch_kpi_statistics.sh -–instance <instance_without_eos_prefix> –-eosreport <full_path_eosreport>"
      exit 0
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

mgmhost=`echo $EOSREPORTFILE | tr '/' '\n' | grep 'cern.ch'`
if [ ! -z $mgmhost ]
then 
  zcat $EOSREPORTFILE 2>> ./historical_statistics/failed_read_eosreports.txt | python3 ../scripts/eosreport_statistics.py --inputfile /dev/stdin --outputfile ./historical_statistics/eosreport_statistics.txt --instance $INSTANCE --mgmhost $mgmhost --measurement_bin 3600
else
  echo "$EOSREPORTFILE: Unable to get the MGM host from the eosreport file path"
fi

