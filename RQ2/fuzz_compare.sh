#!/bin/bash
for i in {1..5}
do 
echo "$i round..."
# solc-select use 0.4.25
# timeout 1h python ./fuzz_compare.py --contract-name RpsGame --random ./contracts/RpsGame.sol > ./random_myth_RpsGame.log 2>&1
# timeout 1h python ./fuzz_compare.py --contract-name CryptoPunksMarket --random ./contracts/CryptoPunksMarket.sol > ./random_myth_CryptoPunksMarket.log 2>&1
# timeout 1h python ./fuzz_compare.py --contract-name MoonCatRescue --random ./contracts/MoonCatRescue.sol > ./random_myth_MoonCatRescue.log 2>&1
# timeout 1h python ./fuzz_compare.py --contract-name SaleClockAuction --random ./contracts/SaleClockAuction.sol > ./random_myth_SaleClockAuction.log 2>&1
# timeout 1h python ./fuzz_compare.py --contract-name SupeRare --random ./contracts/SupeRare.sol > ./random_myth_SupeRare.log 2>&1
# solc-select use 0.5.0
# timeout 1h python ./fuzz_compare.py --contract-name GameChannel --random ./contracts/GameChannel.sol > ./random_myth_GameChannel.log 2>&1

# solc-select use 0.4.25
# timeout 1h python ./fuzz_compare.py --contract-name RpsGame --model-file ../result/model-fix/0xa8f9c7ff9f605f401bde6659fd18d9a0d0a802c5/RpsGame/FSM-4.json --mbt ./contracts/RpsGame.sol > ./mbt_myth_RpsGame.log 2>&1
# timeout 1h python ./fuzz_compare.py --contract-name CryptoPunksMarket --model-file ../result/model-fix/0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb/CryptoPunksMarket/FSM-21.json --mbt ./contracts/CryptoPunksMarket.sol > ./mbt_myth_CryptoPunksMarket.log 2>&1
# timeout 1h python ./fuzz_compare.py --contract-name MoonCatRescue --model-file ../result/model-fix/0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6/MoonCatRescue/FSM-14.json --mbt ./contracts/MoonCatRescue.sol > ./mbt_myth_MoonCatRescue.log 2>&1
# timeout 1h python ./fuzz_compare.py --contract-name SaleClockAuction --model-file ../result/model-fix/0x1f52b87c3503e537853e160adbf7e330ea0be7c4/SaleClockAuction/FSM-3.json --mbt ./contracts/SaleClockAuction.sol > ./mbt_myth_SaleClockAuction.log 2>&1
# timeout 1h python ./fuzz_compare.py --contract-name SupeRare --model-file ../result/model-fix/0x41a322b28d0ff354040e2cbc676f0320d8c8850d/SupeRare/FSM-17.json --mbt ./contracts/SupeRare.sol > ./mbt_myth_SupeRare.log 2>&1
# solc-select use 0.5.0
# timeout 1h python ./fuzz_compare.py --contract-name GameChannel --model-file ../result/gamechannel-fix/0xaec1f783b29aab2727d7c374aa55483fe299fefa/GameChannel/FSM-8.json --mbt ./contracts/GameChannel.sol > ./mbt_myth_GameChannel.log 2>&1

solc-select use 0.4.25
timeout 1h python ./fuzz_compare.py --contract-name RpsGame --model-file ../result/model-fix/0xa8f9c7ff9f605f401bde6659fd18d9a0d0a802c5/RpsGame/FSM-4.json --mbt ./contracts/RpsGame_instrument_index.sol > ./parametric_myth_RpsGame.log 2>&1
timeout 1h python ./fuzz_compare.py --contract-name CryptoPunksMarket --model-file ../result/model-fix/0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb/CryptoPunksMarket/FSM-21.json --mbt ./contracts/CryptoPunksMarket_instrument_index.sol > ./parametric_myth_CryptoPunksMarket.log 2>&1
timeout 1h python ./fuzz_compare.py --contract-name MoonCatRescue --model-file ../result/model-fix/0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6/MoonCatRescue/FSM-14.json --mbt ./contracts/MoonCatRescue_instrument_index.sol > ./parametric_myth_MoonCatRescue.log 2>&1
timeout 1h python ./fuzz_compare.py --contract-name SaleClockAuction --model-file ../result/model-fix/0x1f52b87c3503e537853e160adbf7e330ea0be7c4/SaleClockAuction/FSM-3.json --mbt ./contracts/SaleClockAuction_instrument_index.sol > ./parametric_myth_SaleClockAuction.log 2>&1
timeout 1h python ./fuzz_compare.py --contract-name SupeRare --model-file ../result/model-fix/0x41a322b28d0ff354040e2cbc676f0320d8c8850d/SupeRare/FSM-17.json --mbt ./contracts/SupeRare_instrument_index.sol > ./parametric_myth_SupeRare.log 2>&1
solc-select use 0.5.0
timeout 1h python ./fuzz_compare.py --contract-name GameChannel --model-file ../result/gamechannel-fix/0xaec1f783b29aab2727d7c374aa55483fe299fefa/GameChannel/FSM-8.json --mbt ./contracts/GameChannel_instrument_index.sol > ./parametric_myth_GameChannel.log 2>&1

python coverage_count.py 
tar -czvf parametric_trial-$i.tar.gz *.log 
done 

#for i in {1..5}
#do 
#echo "$i round..."
#myth -v 2 analyze ./contracts/RpsGame.sol:RpsGame --transaction-sequences "[[0xfe1f6a0b], [0xca6649c5], [0x0aebeb4e]]" --parallel-solving >> ./mbt_index_myth_RpsGame.log 2>&1
#myth -v 2 analyze ./contracts/RpsGame_instrument_index.sol:RpsGame --transaction-sequences "[[0xfe1f6a0b], [0xca6649c5], [0x0aebeb4e]]" --parallel-solving >> ./mbt_index_myth_RpsGame.log 2>&1
#done 

echo "done!"
