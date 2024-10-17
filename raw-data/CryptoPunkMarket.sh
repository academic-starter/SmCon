#!/bin/bash
# use this script to run for CryptoPunkMarket
# Since it early 2,000 transactions just call setInitialOwners to assign punks to their owners
# We need at least three thousands transactions to make the contract work
#sleep 3600

echo "analyze CryptoPunkMarket 0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"
python3 -m invconplus.main --address 0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb --maxCount 4000  --configuration ./result/0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb-CryptoPunksMarket-config.json >> CryptoPunkMarket.log 2>&1 



