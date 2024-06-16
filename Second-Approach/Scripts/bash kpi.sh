#!/bin/bash

POSITIONAL_ARGS=()
#instance=eoslhcb

YEAR=\*
MONTH=\*
DAY=\*

while [[ $# -gt 0 ]]; do
  case $1 in
    -usr|--username)
      USERNAME="$2"
      shift # past argument
      shift # past value
      ;;
    -keyt|--keytab)
      KEYTAB="$2"
      shift # past argument
      shift # past value
      ;;  
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
      echo "usage: ./replay_history.sh --username <username> --keytab <keytab> -–instance <instance> –-year 2022 -–month 1 -–day 4"
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

kinit ${USERNAME}@CERN.CH -kt /etc/eos.${KEYTAB}  

files=$(find /eosproject/project/e/eos/Report/"${INSTANCE}"/ -type f -name "${YEAR}${MONTH}${DAY}.eosreport.gz" | sort -t'/' -k 10)
echo "We are going to process from: $(head -n1 <<< """${files}""") to $(tail -n1 <<< """${files}""")"
for file in $files 
do
    kinit ${USERNAME}@CERN.CH -kt /etc/eos.${KEYTAB}  

    filename=$(basename "$file")
    #mkdir -p /var/tmp/eos-datatransfer-history-replay/"${INSTANCE}"/
    cp -v $file /var/tmp/eos-datatransfer-history-replay/"${INSTANCE}"/
    gzip -dv /var/tmp/eos-datatransfer-history-replay/"${INSTANCE}"/${filename}
    time python3 py_script.py --inputfile /var/tmp/eos-datatransfer-history-replay/"${INSTANCE}"/${filename%.gz} --outputfile /var/tmp/eos-datatransfer-history-replay/"${INSTANCE}"/eosreports_statistics.txt
    rm -v /var/tmp/eos-datatransfer-history-replay/"${INSTANCE}"/${filename%.gz}
done

if [[ -n $1 ]]; then
    echo "Date of eosreport recieved:"
    tail -1 "$1"
fi

