#!/bin/bash
# use this script to run for CryptoPunkMarket
# Since it early 2,000 transactions just call setInitialOwners to assign punks to their owners
# We need at least three thousands transactions to make the contract work
#sleep 3600

# echo "analyze Uniswap(Uni) 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
# python3 -m invconplus.main --address 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 --maxCount 2000  --configuration ./result/0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984-Uni-config.json >> ERC20.log 2>&1 

# echo "analyze TetherToken(USDT) 0xdAC17F958D2ee523a2206206994597C13D831ec7"
# python3 -m invconplus.main --address 0xdAC17F958D2ee523a2206206994597C13D831ec7 --maxCount 2000  --configuration ./result/0xdAC17F958D2ee523a2206206994597C13D831ec7-TetherToken-config.json >> ERC20.log 2>&1 

# echo "analyze DAI 0x6B175474E89094C44Da98b954EedeAC495271d0F"
# python3 -m invconplus.main --address 0x6B175474E89094C44Da98b954EedeAC495271d0F --maxCount 2000  --configuration ./result/0x6B175474E89094C44Da98b954EedeAC495271d0F-Dai-config.json >> ERC20.log 2>&1 


echo "mine Uniswap(Uni) automata 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
python3 -m invconplus.core.ConMiner ./result 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 Uni ./result/0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984-Uni.inv.json ./result/0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984-Uni-config.json ./result/0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984-Uni-trace_slices.json >> ERC20.log 2>&1

echo "mine TetherToken(USDT) automata 0xdAC17F958D2ee523a2206206994597C13D831ec7"
python3 -m invconplus.core.ConMiner ./result 0xdAC17F958D2ee523a2206206994597C13D831ec7 TetherToken ./result/0xdAC17F958D2ee523a2206206994597C13D831ec7-TetherToken.inv.json ./result/0xdAC17F958D2ee523a2206206994597C13D831ec7-TetherToken-config.json ./result/0xdAC17F958D2ee523a2206206994597C13D831ec7-TetherToken-trace_slices.json >> ERC20.log 2>&1

echo "mine DAI(Dai) automata 0x6B175474E89094C44Da98b954EedeAC495271d0F"
python3 -m invconplus.core.ConMiner ./result 0x6B175474E89094C44Da98b954EedeAC495271d0F Dai ./result/0x6B175474E89094C44Da98b954EedeAC495271d0F-Dai.inv.json ./result/0x6B175474E89094C44Da98b954EedeAC495271d0F-Dai-config.json ./result/0x6B175474E89094C44Da98b954EedeAC495271d0F-Dai-trace_slices.json >> ERC20.log 2>&1