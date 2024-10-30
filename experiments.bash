#!/bin/bash

# check if an input file has been provided
if [ -z "$1" ]; then
    echo "Error: specify input file where the experiments are stored."
    echo "Usage: $0 <commands_file>"
    exit 1
fi

input_file="$1"
log_file="experiments_results.log"

# check if input file exists
if [ ! -f "$input_file" ]; then
    echo "Error: the file $input_file does not exist."
    exit 1
fi

# iterate over each line of the input file (each line corresponds to a command)
while IFS= read -r command; do
    # skip empty lines
    if [ -z "$command" ]; then
        continue
    fi

    if [[ "$command" == echo* ]]; then
        $command >> "$log_file"
        continue
    fi

    if [[ "$command" != time* ]]; then
        echo "$command" >> "$log_file"
        continue
    fi

    # record start time
    start_time=$(date +%s.%3N)

    # execute command
    ../runlim/runlim -t 3600 -r 3600 $command

    # save end time
    end_time=$(date +%s.%3N)

    # compute execution time
    execution_time=$(echo "$end_time - $start_time" | bc)

    timeout_reached=false

    # if execution time is equal to or greater than 3600 seconds, there have been a timeout
    if (( $(echo "$execution_time >= 3599" | bc -l) )); then
        timeout_reached=true
    fi

    # save results in log file
    echo "Command: $command" >> "$log_file"
    echo "Execution time: ${execution_time} seconds" >> "$log_file"

    # Save even if there has been a timeout
    if [ "$timeout_reached" = true ]; then
        echo "Experiment timeouted" >> "$log_file"
    fi

    echo "--------------------------" >> "$log_file"

done < "$input_file"

# Conferma la registrazione dei tempi di esecuzione
echo "Execution times of the experiments saved in $log_file"
