## eos-datatransfer-monitoring

First Approach(Fluent-bit_first_config_file -> Influxdb -> Grafana)
This branch contains the first fluent bit configuration file.

## Description
This file has four filters to drop log lines containing '''delete_on_close=1''', '''log=unknown''', both '''rb=0''' and '''wb=0''' and where '''fxid''' is present.

## Installation

## Usage
Initialize environment variables:
export MY_INPUT_FILE_PATH='your_input_file_path'
