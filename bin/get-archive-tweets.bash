#!/usr/bin/env bash

# usage (assumes project structure from collectorSetup.bash):
# [project-dir]$ nohup nice bash util/get-archive-tweets.bash > log/nohup.out & 


# fail fast!
set -e
set -u

# vars
HERE=${PWD}
DATADIR=${HERE}/data
RDATADIR=${HERE}/rdata
LOGDIR=${HERE}/log

# => update this as needed 
DATAPATH=/path/to/archive/2016/11/

# 0.0001 sampling ratio
SAMPLE=10000

# get waitForNProcs (~ "process-level xargs") 
. util/util.bash

echo "$(date +%Y-%m-%d\ %H:%M:%S) -- started running $0"

for file in $(find ${DATAPATH} -type f); do
    # waitfornprocs vars
    procName=gzip
    SLEEPTIME=5
    MAXPROCS=25

    # get the file name 
    filename=$(echo ${file} | awk -F'/' '{print $NF}')
    echo "$(date +%Y-%m-%d\ %H:%M:%S) -- reading ${filename}"

    nice gzip -cd ${file} | \
        # randomly sample down  
        nice bash /path/to/random_sampler.bash ${SAMPLE} | \
 
        # select only those tweets with media, write to disk
        nice jq 'select(.twitter_entities.media)' -c >> ${DATADIR}/tweets.json 

    # ramp up slowly 
    sleep 1
    # the loop abides 
    waitForNProcs 
done

wait
echo "$(date +%Y-%m-%d\ %H:%M:%S) -- finished running $0"

