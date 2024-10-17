#!/bin/bash
# mv all its cached transaction files 
# to a new folder named "targetContracts"

ROOT_DIR=$(git rev-parse --show-toplevel)
cd $ROOT_DIR
benchmark_contracts=(MoonCatRescue RpsGame SupeRare SaleClockAuction CryptoPunksMarket)
benchmark_addresses=(0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6 0xa8f9c7ff9f605f401bde6659fd18d9a0d0a802c5 0x41a322b28d0ff354040e2cbc676f0320d8c8850d 0x1f52b87c3503e537853e160adbf7e330ea0be7c4 0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb)

# benchmark_contracts=(CryptoPunksMarket)
# benchmark_addresses=(0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb)

NUM=0
while [[ $NUM -lt 5 ]]
do
  printf "${benchmark_contracts[NUM]}, ${benchmark_addresses[NUM]} \n"

  out_dir=$ROOT_DIR/Dapp-Automata-data/result
  address=${benchmark_addresses[NUM]}
  contractName=${benchmark_contracts[NUM]}
  config=$ROOT_DIR/Dapp-Automata-data/result/${benchmark_addresses[NUM]}-${benchmark_contracts[NUM]}-config.json
  traceInv=$out_dir/${benchmark_addresses[NUM]}-${benchmark_contracts[NUM]}-trace.inv.json
  traceSlice=$out_dir/${benchmark_addresses[NUM]}-${benchmark_contracts[NUM]}-trace_slices.json
  
  printf ">>invariant detection\n"
  # if [[ -f $traceInv ]]; then 
  #   printf "$traceInv exists\n"
  # else 
    python3 -m invconplus.main --address $address --configuration $config --maxCount 10000 --output_dir $out_dir
  # fi 

  printf ">>automata mining\n"
  
  model_out_dir=$out_dir/model-fix

  if ! [ -e $model_out_dir ]; then
    mkdir $model_out_dir
  # else
  #   if [ -e $model_out_dir ]; then
  #     rm -rf $model_out_dir/$address
  #   fi
  fi 

  python3 -m smcon.ConMiner $model_out_dir $address $contractName $traceInv $config $traceSlice 
  ((++NUM))
done
