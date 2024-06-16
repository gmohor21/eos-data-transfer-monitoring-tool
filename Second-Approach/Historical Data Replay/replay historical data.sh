#!/bin/bash

POSITIONAL_ARGS=()

YEAR=\*
MONTH=\*
DAY=\*

while [[ $# -gt 0 ]]; do
  case $1 in
    -i|--instance)
      INSTANCE="$2"
      shift # past argument
      shift # past value
      ;;
    -y|--year)
      YEAR="$2"
      shift # past argument
      shift # past value
      ;;
    -m|--month)
      MONTH="$2"
      shift # past argument
      shift # past value
      ;;
    -d|--day)
      DAY="$2"
      shift # past argument
      shift # past value
      ;;
    --default)
      DEFAULT=YES
      shift # past argument
      ;;
    -h|--help)
      echo "usage: ./replay_history.sh -–instance <instance_without_eos_prefix> –-year 2022 -–month 1 -–day 4"
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

find /eosproject/Report/eos"${INSTANCE}"/ -type f -name "${YEAR}${MONTH}${DAY}.eosreport.gz" -type f -print0 | xargs -P20 -0 -I{} ./launch_kpi_statistics.sh --instance $INSTANCE --eosreport {}

if [[ -n $1 ]]; then
    echo "Date of eosreport recieved:"
    tail -1 "$1"
fi

