import glob
from itertools import repeat 
import os 
from subprocess import PIPE, Popen 
import logging
from multiprocessing import Pool
import simplejson as json 
from slither import Slither

from invconplus.ppt import PptTopLevel, PptType
from invconplus.model.Tx import Transaction, TxType
from invconplus.model.model import VarInfo, VarType, loadDataModel
from invconplus.derivation.unary.Original import Original

from .model.model import DataModel
from .model.Reader import StorageModelReader
from .model.ComputeLayout import computeStorageLayout, fetchAbi

# benchmark_dir = "./Dapp-Automata-data/RQ1/azure-benchmark/workbench"
benchmark_dir = "./Dapp-Automata-data/RQ1/azure-benchmark/workbench-fix"

def create_storage_model(contract_name):
    contract_file = os.path.join(benchmark_dir, contract_name, contract_name+".sol")
    versions = Popen(["solc-select", "versions"], stdout=PIPE).communicate()[0]
    versions = versions.decode().split("\n")[:-2] 

    slither = Slither(contract_file, solc_solcs_select=",".join(versions))
    storageLayout = computeStorageLayout(slither=slither, contractName=contract_name)
    model = StorageModelReader(storageLayout).getModel()
    # print(model.getModel())
    return model

class ContractInvariantGnerator:
    
    def __init__(self, workdir, contract_name, output_dir) -> None:
        self.workdir = workdir 
        self.contract_name = contract_name
     
        self.all_ppts: list = []

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        self.inv_file = os.path.join(output_dir, contract_name+".inv.json")
    
    def reset(self):
        self.init_contract_state: DataModel = create_storage_model(self.contract_name)
        self.previous_contract_state = self.init_contract_state

    def get_tx_object(self, tx):
        tx_hash = tx["transactionHash"]
        tx_input_decode = tx["decode"]
        msgsender = tx["from"].lower()
        msgvalue = tx["value"]
        short_func_name = tx_input_decode[0]["name"] if "name" in tx_input_decode[0] else "constructor" if tx_input_decode[0]["type"] == "constructor" else None 
        assert short_func_name is not None
        parameters = tx_input_decode[0]["inputs"]
        values = tx_input_decode[1]
        env_data: list[dict] = []
        for name in values:
            env_data.append(dict(name=name, value = values[name]))

        env_data.append(dict(name="msg.sender", value=msgsender))
        env_data.append(dict(name="msg.value", value=msgvalue))

        post_state = tx["post_contract_state"]
        post_contract_state = loadDataModel(post_state)
        # print(tx_hash)

        tx_object = Transaction(tx_hash=tx_hash, pre_state=self.previous_contract_state, post_state=post_contract_state, envs= env_data, contract=self.contract_name, func=short_func_name, tx_type=TxType.NORMAL) 
        self.previous_contract_state = post_contract_state
        return short_func_name, parameters, tx_object 
    
    def createOrGetPPT(self, short_func_name, func_parameters):
        new_funcName =  short_func_name + "(" + ",".join([ param["name"] for param in  func_parameters] ) + ")"
        if any(map(lambda ppt: ppt.func == new_funcName , self.all_ppts)):
            return list(filter(lambda ppt: ppt.func == new_funcName , self.all_ppts))[0]
            
        state_varInfos = [ VarInfo(name = item.varName, type= item.varType, vartype= VarType.STATEVAR, derivation=None) for item in self.init_contract_state.variables]

        def generateVarInfosForAbiFunc(): 
            results =  list()
            for item in func_parameters:
                varInfo = VarInfo(name=item["name"], type=item["type"], vartype= VarType.TXVAR, derivation= None)
                results.append(varInfo)
            
            results.append(VarInfo(name="msg.sender", type="address", vartype=VarType.TXVAR, derivation=None))
            results.append(VarInfo(name="msg.value", type="uint256", vartype=VarType.TXVAR, derivation=None)) 
            return results  
         
        funcVarInfos = generateVarInfosForAbiFunc() 

        ppt = PptTopLevel(contract= self.contract_name, func= new_funcName, type= PptType.EXIT, executionType= TxType.NORMAL, vars= state_varInfos + funcVarInfos)
        self.all_ppts.append(ppt)
            
        original_varInfos =  []
        for varInfo in state_varInfos:
                original_varInfos.extend(Original(varInfos=[varInfo], ppt_slice=ppt).derive())
        ppt.vars += original_varInfos 

        ppt.createSlices()
        for myslice in ppt.all_slices:
            myslice.instantiate_invariants()
        return ppt 
    
    def save_invariants(self):
        json_results = list()
        for ppt in self.all_ppts:
                    results = list()
                    _results =  ppt.getAllInvariants()
                   
                    results = _results  
                    logging.warning("\n")
                    logging.warning(ppt.func)
                    logging.warning(ppt.type)
                    logging.warning(ppt.executionType)
                    logging.warning("\n".join([ inv.__str__() for inv in results if inv.verified and not inv.falsify and inv.__str__()!="" ])) 
                    posts = list() 
                    pres = list() 
                    # falsified invariants that hold for some txs
                    falsified_pres = list()
                    falsified_posts = list()
                    LIMIT = 3

                    for inv in results:
                        if inv.verified:
                            if not inv.falsify:
                                if inv.isPostCondition():
                                    if inv.__str__() not in posts and inv.__str__() != "":
                                        posts.append(inv.__str__())
                                else:
                                    if inv.__str__() not in pres and inv.__str__() != "":
                                        pres.append(inv.__str__())
                        
                    json_results.append(dict(func=ppt.func, type=str(ppt.type), executionType=str(ppt.executionType), preconditions=pres, postconditions=posts, falsified_preconditions=falsified_pres, falsified_postconditions=falsified_posts))
        json.dump(json_results, open(self.inv_file, "w"), indent=4)

    def invariant_detect(self):
        items = glob.glob(os.path.join(self.workdir, self.contract_name, "*.txs_contract_state"))
        if len(items)>0:
            for item in items:
                self.reset()
                address = os.path.basename(item).split(".txs_contract_state")[0].strip()
                print(address)
                txs = json.load(open(item))
                for tx in txs:
                    short_func_name, func_parameters, tx_object =  self.get_tx_object(tx)
                    ppt = self.createOrGetPPT(short_func_name=short_func_name, func_parameters=func_parameters)
                    ppt.load(tx=tx_object)
            self.save_invariants()

def main(workdir, contract_name, output_dir):
        # contract_name = "DefectiveComponentCounter"
        print(contract_name)
        generator = ContractInvariantGnerator(workdir=workdir, contract_name=contract_name, output_dir=output_dir)
        generator.invariant_detect()
if __name__ == "__main__":
    workdir = "./Dapp-Automata-data/fuzzer/testnetdata-fix"
    output_dir = "./Dapp-Automata-data/fuzzer/testnetdata-inv-fix"
    projects = os.listdir(workdir)
    projects = ["DefectiveComponentCounter"]
    with Pool(11) as pool:
        pool.starmap(main, zip(repeat(workdir), projects, repeat(output_dir)))
    
