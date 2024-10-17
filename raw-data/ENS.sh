#!/bin/bash


echo "analyze ENS(Registrar) 0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef"
python3 -m invconplus.main --address 0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef --maxCount 2000  --configuration ./result/0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef-Registrar-config.json >> Registrar.log 2>&1 



