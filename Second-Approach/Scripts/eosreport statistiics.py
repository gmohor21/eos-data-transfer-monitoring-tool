#!/usr/bin/env/ python

import re
import json
import argparse
import fcntl
import time

'''
In the case several processes of that python program are run in parallel,
a lock file is created by this class to prevent multiplue writes to the 
output file
'''
class FileLocker:
    def __init__(self, file_name='/var/tmp/eosreport_statistics.lock'):
        """
        Initialize the FileLocker class.

        Args:
            file_name (str): The name of the lock file. Defaults to '/var/tmp/eosreport_statistics.lock'.
        """
        # Open the lock file in write mode
        self.file_obj = open(file_name, 'w')
    def __enter__(self):
        """
        Acquires an exclusive lock on the file object and returns the FileLocker object.

        Returns:
            FileLocker: The current FileLocker object.
        """
        # Acquire an exclusive lock on the file object
        fcntl.lockf(self.file_obj, fcntl.LOCK_EX)
        
        # Return the current FileLocker object
        return self
    def __exit__(self, type, value, traceback):
        """
        Unlocks the file object and closes it.

        Args:
            type: The type of the exception, if any.
            value: The exception instance, if any.
            traceback: The traceback object, if any.
        """
        # Unlock the file object
        fcntl.lockf(self.file_obj, fcntl.F_UNLCK)
        
        # Close the file object
        self.file_obj.close()
        
        # Return None to indicate that no exception was raised
        return None



def compute_bin_timestamp(timestamp, timestamp_bin):
    """
    Compute the timestamp bin for a given timestamp.

    Args:
        timestamp (int): The timestamp to be computed.
        timestamp_bin (int): The time bin interval in seconds.

    Returns:
        int: The computed timestamp bin.

    """
    # Compute the integer division of the timestamp by the time bin interval
    # and multiply it by the time bin interval
    bin_timestamp = int((timestamp // timestamp_bin)) * timestamp_bin

    # Add the time bin interval minus one to the computed timestamp bin
    # to include the entire bin up to the timestamp
    return bin_timestamp + (timestamp_bin - 1)

def output_kpi_to_file(kpis, eosinstance, mgmhost, outputfile):
    """
    Outputs the KPIs to a file.

    Args:
        kpis (dict): A dictionary containing the KPIs to be outputted.
        eosinstance (str): The EOS instance name.
        mgmhost (str): The management host name.
        outputfile (str): The path to the output file.

    Returns:
        None
    """
    # Use FileLocker to ensure only one process can write to the output file at a time
    with FileLocker() as fileLocker:
        # Open the output file in append mode
        with open(outputfile, 'a') as output_file:
            # Iterate over the KPIs and write them to the output file
            for timestamp, protocol_kpis in kpis.items():
                for protocol, kpis in protocol_kpis.items():
                    # Create a dictionary to store the KPIs to be outputted
                    object_to_output = {
                        'cts_timestamp_bin': timestamp,
                        'protocol': protocol,
                        'eos_instance': eosinstance,
                        'mgmhost': mgmhost
                    }
                    # Add the KPIs to the dictionary
                    for kpi_key, kpi_value in kpis.items():
                        object_to_output[kpi_key] = kpi_value
                    # Write the KPIs to the output file as a JSON object
                    json.dump(object_to_output, output_file) 
                    # Add a newline character after each KPI object
                    output_file.write('\n')
            
'''
Temporary fix for vector read bytes
https://its.cern.ch/jira/browse/EOS-5373
'''
def isCorrectRb(rb):
    """
    Check if the given value for 'rb' is within the expected range.

    Args:
        rb (int): The value of 'rb' to be checked.

    Returns:
        bool: True if the value of 'rb' is less than or equal to 1E16, False otherwise.
    """
    # Check if the given value for 'rb' is within the expected range.
    # The expected range is less than or equal to 1E16.
    # This is a temporary fix for vector read bytes (https://its.cern.ch/jira/browse/EOS-5373).
    return rb <= 1E16

def getCorrectRvbSum(rvbSum):
    """
    Check if the given value for 'rvbSum' is within the expected range.

    Args:
        rvbSum (int): The value of 'rvbSum' to be checked.

    Returns:
        int: If the value of 'rvbSum' is less than or equal to 1E16, it returns the same value.
              Otherwise, it returns 0.

    Temporary fix for vector read bytes (https://its.cern.ch/jira/browse/EOS-5373).
    """
    # Check if the given value for 'rvbSum' is within the expected range.
    # The expected range is less than or equal to 1E16.
    # If the value is greater than 1E16, it returns 0.
    # Otherwise, it returns the same value.
    if(rvbSum > 1E16):
        return 0
    return rvbSum

def isEosReportLineValid(all_key_values):
    """
    Check if the given line from an EOS report is valid.

    Args:
        all_key_values (dict): A dictionary containing the key-value pairs from the line.

    Returns:
        bool: True if the line is valid, False otherwise.
    """
    # Convert 'rvb_sum' and 'rb' to integers
    rvbSum = int(all_key_values['rvb_sum'])
    rb = int(all_key_values['rb'])
    wb = int(all_key_values['wb'])

    # Check if 'rb' and 'rvb_sum' are within the expected range.
    # Also, check if at least one of 'rb', 'wb', or 'rvb_sum' is non-zero.
    # Finally, check if 'log' is not equal to 'unknown'.
    return (isCorrectRb(rb) and isCorrectRb(rvbSum)
            and (rb != 0 or wb != 0 or rvbSum != 0)
            and all_key_values['log'] != 'unknown')

def getProtocol(record):
    """
    Get the protocol from the record.

    Parameters:
        record (dict): A dictionary containing the key-value pairs from the record.

    Returns:
        str: The protocol extracted from the record.
             If the protocol is 'http' or 'https', it returns 'http'.
             Otherwise, it returns the value of 'sec.app'.

    This function extracts the protocol from the record.
    If the protocol is 'http' or 'https', it returns 'http'.
    Otherwise, it returns the value of 'sec.app'.
    """
    # Extract the values for 'sec.prot' and 'sec.app' from the record
    secProt = record['sec.prot']
    secApp = record['sec.app']

    # Check if the protocol is 'http' or 'https'
    if secProt == "http" or secProt == "https":
        # If the protocol is 'http' or 'https', return 'http'
        return "http"
    else:
        # If the protocol is not 'http' or 'https', return the value of 'sec.app'
        return secApp


def main(inputfile, outputfile, measurement_bin, eosinstance, mgmhost):
    """
    Main function to process the input file and generate the output file.

    Parameters:
        inputfile (str): The path to the input file.
        outputfile (str): The path to the output file.
        measurement_bin (int): The measurement bin size.
        eosinstance (str): The EOS instance.
        mgmhost (str): The management host.
    """
    # Regular expression to match the lines of interest
    regex = re.compile(r'rb=\d+.*wb=\d+.*delete_on_close=0')

    # List of keys to extract from each line
    list_keys = ("cts", "rb", "rvb_sum", "wb", "sec.app", "sec.prot")

    # Dictionary to store the key performance indicators (KPIs)
    kpis = {}

    # Open the input file and process each line
    with open(inputfile, encoding='unicode_escape', errors='ignore') as f:
        for line in f:
            # Ignore empty lines or lines that don't match the regular expression
            if line.strip() == '' or re.search(regex, line) is None:
                continue

            try:
                # Extract the key-value pairs from the line
                all_key_values = dict((a.strip(), b.strip()) for a, b in (subString.split("=", 1) for subString in line.split("&")))

                # Check if the line is a valid EOS report line
                if not isEosReportLineValid(all_key_values):
                    continue
            except Exception as exc:
                # Print exception information and continue to the next line
                print('Exception: ', line, exc)
                continue

            # Extract the values for the list of keys and convert them to integers
            try:
                record = dict(((key, int(all_key_values[key])) for key in list_keys[:-2]))
            except Exception as exc:
                # Print exception information and continue to the next line
                print('Exception: ', line, exc)
                continue

            # Set the value of 'sec.app' to 'None' if it is empty, otherwise use the value from 'all_key_values'
            if all_key_values.get('sec.app', "") == '':
                record['sec.app'] = 'None'
            else:
                record['sec.app'] = all_key_values.get('sec.app')

            # Set the value of 'sec.prot' to the value from 'all_key_values'
            record['sec.prot'] = all_key_values.get('sec.prot')

            # Compute the current bin timestamp
            current_bin_timestamp = compute_bin_timestamp(record['cts'], measurement_bin)

            # Get the protocol from the record
            current_protocol = getProtocol(record)

            # Get the correct RvbSum from the record
            current_rvb_sum = getCorrectRvbSum(record['rvb_sum'])

            # Get the values for 'rb', 'wb', and 'total_read_files' from the record
            current_rb = record['rb']
            current_write_files = int(record['wb'] != 0)
            current_read_files = int((current_rb != 0 or current_rvb_sum != 0))

            # Get the KPIs for the current bin timestamp and protocol
            current_timestamp_kpi = kpis.get(current_bin_timestamp, {})
            current_protocol_kpi = current_timestamp_kpi.get(current_protocol, {
                                                             "total_read_bytes": 0, "total_vector_read_bytes": 0, "total_write_bytes": 0, "total_read_files": 0, "total_write_files": 0})

            # Update the KPIs for the current bin timestamp and protocol
            current_protocol_kpi["total_read_bytes"] += current_rb
            current_protocol_kpi["total_vector_read_bytes"] += current_rvb_sum
            current_protocol_kpi["total_write_files"] += current_write_files
            current_protocol_kpi["total_write_bytes"] += record['wb']
            current_protocol_kpi["total_read_files"] += current_read_files

            # Update the KPIs for the current bin timestamp
            current_timestamp_kpi[current_protocol] = current_protocol_kpi
            kpis[current_bin_timestamp] = current_timestamp_kpi

    # Output the KPIs to the output file
    output_kpi_to_file(kpis, eosinstance, mgmhost, outputfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Example')
    parser.add_argument(
        '--inputfile', required=True, metavar='<inputfile>', type=str, 
        help='File to me processed - EOS Report Log')
    parser.add_argument(
        '--outputfile', required=True, metavar='<outputfile>', type=str,
        help="Directs the output to a name of our choice")
    parser.add_argument(
        '--measurement_bin', default=86400, metavar='<bin_time_interval>', type=int,
        help="The time interval to be entered in seconds")
    parser.add_argument(
        '--instance', required=True, metavar='<eos_instance_without_eos_prefix>', type=str, help="The EOS instance"
    )
    parser.add_argument(
        '--mgmhost', required=True, metavar='MGM FQDN', type=str, help="The EOS MGM FQDN"
    )
    args = parser.parse_args()
    main(args.inputfile, args.outputfile, args.measurement_bin, args.instance, args.mgmhost)
   

