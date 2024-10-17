from itertools import repeat
import os
import copy 
import glob 
from subprocess import PIPE, Popen 
import simplejson as json
from dataclasses import asdict
from multiprocessing import Pool

from slither import Slither

from utils.TraceParsing import Simulator
from utils.Utils import get_transaction_info,get_transaction_receipt, get_contract, get_constructor_abi

import model.model as MODEL 
from model.Reader import StorageModelReader
from model.ComputeLayout import computeStorageLayout, fetchAbi

# benchmark_dir = "./Dapp-Automata-data/RQ1/azure-benchmark/workbench"
# workdir = "./Dapp-Automata-data/fuzzer/testnetdata"
# output_dir = "./Dapp-Automata-data/fuzzer/testnetdata-transactiontraces"
# trace_dir="Dapp-Automata-data/fuzzer/testnetdata-traces"
benchmark_dir = "./Dapp-Automata-data/RQ1/azure-benchmark/workbench-fix"
workdir = "./Dapp-Automata-data/fuzzer/testnetdata-fix"
output_dir = "./Dapp-Automata-data/fuzzer/testnetdata-transactiontraces-fix"
trace_dir="Dapp-Automata-data/fuzzer/testnetdata-traces-fix"

from web3_input_decoder import decode_constructor

def my_decode_constructor(contract_abi, tx_input, bytecode):
    result = decode_constructor(abi=contract_abi, tx_input=tx_input, bytecode=bytecode)
    result_dict = dict()
    for item in result:
       variable = item[1]
       value = item[2]
       result_dict[variable] = value 
    return result_dict

def get_tx_trace(tx_hash, output_file):
    cmd = """curl -H 'Content-Type: application/json' --data '{{"jsonrpc":"2.0", "id": 1, "method": "debug_traceTransaction", "params": [ "{0}", ["vmTrace", "trace", "stateDiff"] ] }}' http://localhost:8545 -o {1} """.format(tx_hash, output_file)
    print(cmd)
    exitcode = os.system(cmd)
    assert exitcode != -1, "error getting transaction trace"

def get_tx_traces(project):
    for address_item in os.listdir(os.path.join(workdir, project)):
            address = address_item.split(".txs")[0].strip() 
            if not os.path.exists(os.path.join(output_dir, project, address)):
                os.makedirs(os.path.join(output_dir, project, address))
            tx_receipts = json.load(open(os.path.join(workdir, project, address_item)))
            for tx in tx_receipts:
                tx_hash = tx["transactionHash"]
                get_tx_trace(tx_hash, os.path.join(output_dir, project, address, tx_hash+".json"))
def get_all_tx_traces():
    projects = list(os.listdir(workdir))
    projects = ["DefectiveComponentCounter"]
    print(projects)

    with Pool(11) as pool:
        pool.map(get_tx_traces, projects)

def get_tx_infos(project, abi, bytecode):
    for address_item in os.listdir(os.path.join(workdir, project)):
            address = address_item.split(".txs")[0].strip() 
            contract = get_contract(contract_address=address, contract_abi=abi)
            print(address)
            if not os.path.exists(os.path.join(output_dir, project, address)):
                os.makedirs(os.path.join(output_dir, project, address))
            try:
                tx_receipts = json.load(open(os.path.join(workdir, project, address_item)))
            except:
                tx_hashes = [item.split(".json")[0].strip() for item \
                             in os.listdir(os.path.join(output_dir, project, address))]
                tx_receipts = []
                for tx_hash in tx_hashes:
                    tx_receipt = get_transaction_receipt(tx_hash)
                    tx_receipts.append(tx_receipt)
                tx_receipts = sorted(tx_receipts, key=lambda tx_receipt: tx_receipt["blockNumber"])

            for i in range(len(tx_receipts)):
                tx = tx_receipts[i]
                tx_hash = tx["transactionHash"]
                print(tx_hash)
                tx_input, tx_gas, tx_gasPrice, tx_value, tx_nonce = get_transaction_info(tx_hash)
                tx["input"] = tx_input 
                if i != 0:
                    decode = contract.decode_function_input(tx_input)
                    decode = (decode[0].abi, decode[1])
                else:
                    decode_input = my_decode_constructor(abi, tx_input, bytecode)
                    decode = (get_constructor_abi(contract_abi=abi), decode_input)
                tx["decode"] = decode
                tx["gas"] = tx_gas
                tx["gasPrice"] = tx_gasPrice
                tx["value"] = tx_value
                tx["nonce"] =tx_nonce
            
            json.dump(tx_receipts, open(os.path.join(workdir, project, address_item), "w"), indent=4)

def get_all_tx_infos():
    projects = []
    abis = []
    bins = []
    for project in os.listdir(workdir):
        if project!="DefectiveComponentCounter":
            continue
        print(project)
        abi = json.load(open(os.path.join(benchmark_dir, project, project+".abi")))
        bytecode = open(os.path.join(benchmark_dir, project, project+".bin")).read()
        projects.append(project)
        abis.append(abi)
        bins.append(bytecode)
    
    with Pool(11) as pool:
        pool.starmap(get_tx_infos, zip(projects, abis, bins))
               
def create_storage_model(contract_name):
    contract_file = os.path.join(benchmark_dir, contract_name, contract_name+".sol")
    versions = Popen(["solc-select", "versions"], stdout=PIPE).communicate()[0]
    versions = versions.decode().split("\n")[:-2] 

    slither = Slither(contract_file, solc_solcs_select=",".join(versions))
    storageLayout = computeStorageLayout(slither=slither, contractName=contract_name)
    model = StorageModelReader(storageLayout)
    # print(model.getModel())
    return model

def decode(contract_name, address):
    print(contract_name, address)
    model = create_storage_model(contract_name=contract_name)
    tx_receipts = json.load(open(os.path.join(workdir, contract_name, address + ".txs")))
    for tx in tx_receipts:
        tx_hash = tx["transactionHash"]
        simulator = Simulator(output_dir, contract_name, address, tx_hash)
        simulator.loadAndexec()
        state_diff = simulator.get_state_diff()
        contract_state_diff = state_diff[address.lower()] if address.lower() in state_diff else dict()
        missing_slots = []
        for slot in contract_state_diff:
            oldval, newval = contract_state_diff[slot]
            if not model.read(slot, oldval, newval):
                missing_slots.append(slot)
            else:
                pass

        maxTimes = 2
        cnt = 0
        while cnt < maxTimes and len(missing_slots)>0:
            cnt += 1
            for slot in copy.copy(missing_slots):
                oldval, newval = contract_state_diff[slot]
                MODEL.GLOBAL_INNER_KEYS = simulator.query(slot)
                if model.read(slot, oldval, newval):
                    missing_slots.remove(slot)
        
        if len(missing_slots) > 0:
            print("Error in processing state update")
        
        post_contract_state = json.loads(json.dumps(asdict(model.getModel())))
        tx["post_contract_state"] = post_contract_state
        tx["stateDiff"] = state_diff
    
    json.dump(tx_receipts, open(os.path.join(workdir, contract_name, address + ".txs_contract_state"), "w"), indent=4)

def decode_all():
    for project in os.listdir(workdir):
        if project!="DefectiveComponentCounter":
            continue
        addresses = []
        for address_item in os.listdir(os.path.join(workdir, project)):
            address = address_item.split(".txs")[0].strip() 
            # decode(project, address)
            addresses.append(address)

        with Pool(10) as pool:
            pool.starmap(decode, zip(repeat(project), addresses))

def produce_event_trace(tx):
    tx_decode = tx["decode"][0]
    post_contract_state = tx["post_contract_state"]
    short_func_name = tx_decode["name"] if "name" in tx_decode else "constructor" if tx_decode["type"] == "constructor" else None
    assert short_func_name is not None 
    full_func_name = short_func_name + "(" + ",".join([ p["name"] for p in tx_decode["inputs"]]) + ")"
    varaibles = post_contract_state["variables"]
    primtive_state_vars = []
    for varaible in varaibles:
        name = varaible["varName"]
        value = varaible["varValue"]
        vartype = varaible["varType"]
        if isinstance(value, int) or isinstance(value, str):
            primtive_state_vars.append(dict(name=name, value=value, vartype=vartype))
        else:
            continue
    return full_func_name, primtive_state_vars


def produce_event_traces(trace_dir, project):
    print(project)
    address_items = glob.glob(os.path.join(workdir, project, "*.txs_contract_state"))
    trace_slices = []
    for address_item in address_items:
            address = os.path.basename(address_item).split(".txs_contract_state")[0].strip() 
            full_tx_contract_states = json.load(open(address_item))

            event_trace = []
            state_trace = []
            for tx in full_tx_contract_states:
                full_func_name, primitive_state_vars = produce_event_trace(tx)
                event_trace.append(dict(methodName=full_func_name, parameters=[]))
                state_trace.append(primitive_state_vars)
            trace_slice = dict(parameterBindings=dict(), event_trace=event_trace, state_trace=state_trace)
            trace_slices.append(trace_slice)
        
    json.dump(trace_slices, open(os.path.join(trace_dir, project+".traces.json"), "w"), indent=4)


def produce_event_trace_all(trace_dir):
    if not os.path.exists(trace_dir):
        os.mkdir(trace_dir)
    projects = os.listdir(workdir)
    projects = ["DefectiveComponentCounter"]
    with Pool(11) as pool:
        pool.starmap(produce_event_traces, zip(repeat(trace_dir), projects))

get_all_tx_traces()

get_all_tx_infos()

decode_all()

produce_event_trace_all(trace_dir=trace_dir)

