#!/bin/bash
# sleep one hour to avoid conflict with batch.sh 
#sleep 3600
missed_address=(0xdAC17F958D2ee523a2206206994597C13D831ec7 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d)
for address in ${missed_address[@]};
do 
    echo "python3 -m invconplus.main --address" $address
    python3 -m invconplus.main --address $address --maxCount 10 >> batch.log 2>&1 
done 
