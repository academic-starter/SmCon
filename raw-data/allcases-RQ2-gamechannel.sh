#!/bin/bash
# mv all its cached transaction files 
# to a new folder named "targetContracts"

ROOT_DIR=$(git rev-parse --show-toplevel)
cd $ROOT_DIR
benchmark_contracts=(GameChannel GameChannel GameChannel GameChannel GameChannel GameChannel GameChannel GameChannel)
# benchmark_addresses=(0xC95D227a1CF92b6FD156265AA8A3cA7c7DE0F28e 0xbf8b9092e809de87932b28ffaa00d520b04359aa 0x3e07881993c7542a6da9025550b54331474b21dd 0xeb6f4ec38a347110941e86e691c2ca03e271df3b 0x9919d97e50397b7483e9ea61e027e4c4419c8171 0x7e0178e1720e8b3a52086a23187947f35b6f3fc4 0xaec1f783b29aab2727d7c374aa55483fe299fefa 0xa867bF8447eC6f614EA996057e3D769b76a8aa0e)
benchmark_addresses=(0x7e0178e1720e8b3a52086a23187947f35b6f3fc4)
NUM=0
# while [[ $NUM -lt 8 ]]
while [[ $NUM -lt 1 ]]
do
  printf "${benchmark_contracts[NUM]}, ${benchmark_addresses[NUM]} \n"

  out_dir=$ROOT_DIR/Dapp-Automata-data/result/
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
  
  model_out_dir=$out_dir/gamechannel-fix

  if ! [ -e $model_out_dir ]; then
    mkdir $model_out_dir
  else
    if [ -e $model_out_dir/$address ]; then
      rm -rf $model_out_dir/$address
    fi 
  fi 

  python3 -m smcon.ConMiner $model_out_dir $address $contractName $traceInv $config $traceSlice 
  ((++NUM))
done
