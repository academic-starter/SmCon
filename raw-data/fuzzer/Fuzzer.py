import re 
import os
import traceback
from hexbytes import HexBytes 
import simplejson 
import argparse 
from utils import Utils, Random

class HexJsonEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        return super().default(obj)
    
class Fuzzer:
    workdir: str 
    accounts: list 
    contract_name: str 
    contract_abi: object 
    contract_bytecode: str 
    def __init__(self, workdir, accounts, contract_name, contract_abi, contract_bytecode) -> None:
        self.workdir = workdir
        self.accounts = accounts
        self.contract_name = contract_name
        self.contract_abi = contract_abi
        self.contract_bytecode = contract_bytecode

        if not os.path.exists(os.path.join(self.workdir, self.contract_name)):
            os.makedirs(os.path.join(self.workdir, self.contract_name))

    def fuzz(self, maxLoop = 100, maxCount=100):
        loop_count = 0
        while loop_count < maxLoop:
            loop_count += 1
            tx_receipts = []
            deploy_account = self.accounts[Random.rand_uint(len(self.accounts))]
            deployer = deploy_account["address"]
            private_key = deploy_account["private_key"]
            try:
                contract, tx_receipt = Utils.deploy(self.contract_abi, self.contract_bytecode, self._fuzz("constructor"), deployer, private_key)
                print("deploy success ", contract.address)
            except:
                traceback.print_exc()
                continue
            tx_receipt = dict(tx_receipt)
            tx_receipt["transactionHash"] = tx_receipt["transactionHash"].hex()
            tx_receipt["blockHash"] = tx_receipt["blockHash"].hex()
            tx_receipt["logsBloom"] = tx_receipt["logsBloom"].hex()
            tx_receipts.append(tx_receipt)
            count = 0
            while count < maxCount:
                count += 1
                func = self.contract_abi[Random.rand_uint(len(self.contract_abi))]
                while "name" not in func or func["stateMutability"] == "view":
                    func = self.contract_abi[Random.rand_uint(len(self.contract_abi))]
                sender_account = self.accounts[Random.rand_uint(len(self.accounts))]
                sender = sender_account["address"]
                private_key = sender_account["private_key"]
                try:
                    tx_receipt = Utils.sendTransaction(contract.functions[func["name"]], self._fuzz_func(func), sender, private_key) 
                    # check transaction receipt to see if transaction succeed or fail.
                    tx_receipt = dict(tx_receipt)
                    tx_receipt["transactionHash"] = tx_receipt["transactionHash"].hex()
                    tx_receipt["blockHash"] = tx_receipt["blockHash"].hex()
                    tx_receipt["logsBloom"] = tx_receipt["logsBloom"].hex()
                    tx_receipts.append(tx_receipt)
                except:
                    continue 
            
            with open(os.path.join(self.workdir, self.contract_name, contract.address+".txs"), "w") as f:
                simplejson.dump(tx_receipts, f, cls=HexJsonEncoder)

    def _fuzz(self, func_name):
        for func in self.contract_abi:
            if func_name == "constructor" and func["type"] == "constructor":
                return self._fuzz_func(func) 
            if "name" in func and func_name == func["name"]:
                return self._fuzz_func(func) 
    
    def _fuzz_func(self, abi_func):
        args = {}
        for param in abi_func["inputs"]:
            param_name = param["name"]
            param_type = param["type"]
            args[param_name] = self._fuzz_type(param_type)
        return args 
    
    def _fuzz_type(self, var_type):
        if var_type in ["uint"] + ["uint"+str(i) for i in range(8, 257, 8)]:
            # unsigned integer 
            if Random.rand_float()>0.5:
                result = Random.rand_uint(Random.UINT_MAX[var_type]) 
                if Random.rand_float()>0.5:
                    return Random.bit_swap(Random.bit_swap(Random.bit_swap(result)))
                else:
                    return result
            else:
                return Random.rand_uint(Random.UINT_MAX["uint8"]) 
        elif var_type in ["int"] + ["int"+str(i) for i in range(8, 257, 8)]:
            # signed integer 
            if Random.rand_float()>0.5:
                result = Random.rand_int(Random.INT_MIN[var_type], Random.INT_MAX[var_type]) 
                if Random.rand_float()>0.5:
                    return Random.bit_swap(Random.bit_swap(Random.bit_swap(result)))
                else:
                    return result
            else:
                return Random.rand_uint(Random.UINT_MAX["uint8"]) 
        elif var_type in ["bool"]:
            if Random.rand_float()>=0.5:
                return True
            else:
                return False
        elif var_type in ["string", "bytes"]:
            return Random.STR_CORPUS[Random.rand_uint(len(Random.STR_CORPUS))]
        elif var_type in ["byte"+str(i) for i in range(1, 33)]:
            index = ["byte"+str(i) for i in range(1, 33)].index(var_type)
            result = Random.rand_uint(Random.UINT_MAX["uint"+str(index*8)])
            return f"{result:#0{index*2+2}x}"
        elif var_type in ["address"]:
            return self.accounts[Random.rand_uint(len(self.accounts))]["address"]
        else:
            # var_type is composite type
            fixed_array_regex = re.compile("^(\w+)\[(\w+)\]$")
            dynamic_array_regex = re.compile("^(\w+)\[\]$")
            if fixed_array_regex.match(var_type):
                m = fixed_array_regex.match(var_type)
                elem_type = m.group(1)
                size = int(m.group(2))
                results = []
                for i in range(size):
                    results.append(self._fuzz_type(elem_type))
                return results
            elif dynamic_array_regex.match(var_type):
                m = dynamic_array_regex.match(var_type)
                elem_type = m.group(1)
                size = Random.rand_uint(5)
                results = []
                for i in range(size):
                    results.append(self._fuzz_type(elem_type))
                return results 
            else:
                assert False, f"{var_type} is currentlly not supported"

def test():
    workdir = "Dapp-Automata-data/fuzzer/testnetdata"
    contract_name = "AssetTransfer"
    contract_abi = simplejson.load(open("./Dapp-Automata-data/RQ1/azure-benchmark/workbench/AssetTransfer/AssetTransfer.abi"))
    contract_bytecode = open("./Dapp-Automata-data/RQ1/azure-benchmark/workbench/AssetTransfer/AssetTransfer.bin").read()
    accounts = simplejson.load(open("./Dapp-Automata-data/fuzzer/account.json"))
    fuzzer = Fuzzer(workdir=workdir, accounts=accounts["accounts"], contract_name=contract_name, contract_abi=contract_abi, contract_bytecode=contract_bytecode)

    # for test_type in ["uint256", "uint256[2]", "bool", "bool[]", "address", "int8", "string"]:
    #     result = fuzzer._fuzz_type(test_type)
    #     print(test_type, result)
    
    fuzzer.fuzz()

def _main(contract_name, contract_abi, contract_bytecode):
    print(contract_name)
    workdir = "Dapp-Automata-data/fuzzer/testnetdata-fix"
    accounts = simplejson.load(open("./Dapp-Automata-data/fuzzer/account.json"))
    fuzzer = Fuzzer(workdir=workdir, accounts=accounts["accounts"], contract_name=contract_name, contract_abi=contract_abi, contract_bytecode=contract_bytecode)

    # for test_type in ["uint256", "uint256[2]", "bool", "bool[]", "address", "int8", "string"]:
    #     result = fuzzer._fuzz_type(test_type)
    #     print(test_type, result)
    
    fuzzer.fuzz()

def main():
    parser = argparse.ArgumentParser(description=\
                                     'Simple Fuzzer to Generate Random Test Transactions')
    parser.add_argument('--contract_name', type=str, required=True)
    parser.add_argument('--contract_abi', type=str, required=True)
    parser.add_argument('--contract_bytecode', type=str, required=True)
    args = parser.parse_args()

   
    contract_name = args.contract_name
    contract_abi = simplejson.load(open(args.contract_abi))
    contract_bytecode = open(args.contract_bytecode).read()
    _main(contract_name, contract_abi, contract_bytecode)


def batch_main():
    # benchmark_dir = "./Dapp-Automata-data/RQ1/azure-benchmark/workbench"
    benchmark_dir = "./Dapp-Automata-data/RQ1/azure-benchmark/workbench-fix"
    for item in os.listdir(benchmark_dir):
        if item != "DefectiveComponentCounter":
            continue
        if os.path.isdir(os.path.join(benchmark_dir, item)):
            try:
                cmd = "cd {0} && solc --bin --abi -o ./ {1}.sol --overwrite".format(os.path.join(benchmark_dir, item), item)
                exitcode = os.system(cmd)
                contract_name = item 
                contract_abi =  simplejson.load(open(os.path.join(benchmark_dir, item, item+".abi")))
                contract_bytecode = open(os.path.join(benchmark_dir, item, item+".bin")).read()
                _main(contract_name, contract_abi, contract_bytecode)
            except: 
                traceback.print_exc()
                print(item, " fail!")

if __name__ == "__main__":
    batch_main()