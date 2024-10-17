from itertools import repeat
import json
import os
from multiprocessing import Pool
from smcon.specAutomata import *
from smcon.invariantslice import InvariantSlice
from smcon.PrefixTree import PrefixTree, DataPrefixTree
from smcon.Ktail import KTail
from smcon.SEKT_Ktail import SEKT_TAIL
from smcon.ContractorPlus import ContractorPlus
from smcon.SMCon import SMCon
import time

MDL_ON = False


class ConMiner:
    def __init__(self, workdir, contractName) -> None:
        self.contractName = contractName
        self.workdir = os.path.join(workdir, contractName)
        self.ignores = []
        self.usefullName = False

        if not os.path.exists(self.workdir):
            os.mkdir(self.workdir)

    def enableFullName(self):
        self.usefullName = True

    def readPreProcessedSliceInvariant(self, invariant):
        predicates = []
        pre_invariants = {}
        post_invariants = {}
        for method in invariant:
            for variant in invariant[method]:
                # remove ori label
                new_pre = []
                # this is caused by the lack of detected invariant since no relevant methods have been called in the history
                if "slice_pre" not in variant:
                    continue
                for item in variant["slice_pre"]:
                    m = re.match(r"^ori\((.*)\)", item)
                    if m is None:
                        # this is a precondition about input parameter
                        # FIXME: how to handle this
                        continue
                    assert m is not None
                    pure_item = m.group(1)
                    if item.find("Sum") == -1 and item.find("elem of") == -1 and item.find("[...]") == -1:
                        new_pre.append(item.replace(
                            f"ori({pure_item})", pure_item).replace("$", "_"))

                new_post = []
                for item in variant["slice_post"]:
                    if item.find("Sum") == -1 and item.find("elem of") == -1 and item.find("[...]") == -1:
                        # if item.find("Sum") == -1 and item.find("elem of") == -1 and item.find("[...]") == -1 and item.find("[") == -1:
                        new_post.append(item.replace("$", "_"))

                # add dummyState
                # if method == "constructor" or method == "createGame":
                #     new_pre.append("dummyState == 0")
                # else:
                #     new_pre.append("dummyState != 0")
                # new_post.append("dummyState != 0")

                predicates += new_pre
                pre_invariants[method+"@" +
                               "@".join(variant["parameterBinding"])] = new_pre

                predicates += new_post
                post_invariants[method+"@" +
                                "@".join(variant["parameterBinding"])] = new_post
        self.predicates = list(set(predicates))
        self.pre_invariants = pre_invariants
        self.post_invariants = post_invariants
        self.fieldPredMapping = getFieldPredicates(self.predicates)

        json.dump(self.pre_invariants, open(os.path.join(
            self.workdir, self.contractName+".pre_inv"), "w"), indent=4)
        json.dump(self.post_invariants, open(os.path.join(
            self.workdir, self.contractName+".post_inv"), "w"), indent=4)

    def getFieldPredMapping(self):
        return self.fieldPredMapping

    def setInitialState(self, initialState):
        self.initialState = initialState

    def enableZeroIntialState(self):
        # self.fieldPredMapping["dummyState"]=["dummyState == 0", "dummyState != 0"]

        initialState = list()
        for field in self.fieldPredMapping:
            initialState.append(f"{field} == 0")
        initialState = translate2Z3exprFromPredSet(initialState)
        self.initialState = initialState

        return self.initialState

    @property
    def fields(self):
        return list(self.fieldPredMapping.keys())

    def addTraces(self, trace_slice_file, percentage: float = None):
        self.traces = list()
        trace_slices = json.load(open(trace_slice_file, "r"))
        if percentage is not None:
            assert isinstance(
                percentage, float) and percentage > 0 and percentage < 1.0
            trace_slices = trace_slices[:int(percentage*len(trace_slices))]
        for trace_slice in trace_slices:
            trace = list()
            for index in range(len(trace_slice["event_trace"])):
                event = trace_slice["event_trace"][index]
                if len(trace_slice["state_trace"]) == len(trace_slice["event_trace"]):
                    state = trace_slice["state_trace"][index]
                else:
                    assert len(trace_slice["state_trace"]) == len(
                        trace_slice["event_trace"]) + 1
                    state = trace_slice["state_trace"][index+1]
                event_name = event["methodName"].split(
                    "(")[0]+"@"+"@".join([param["name"] for param in event["parameters"]])
                state_predicates = []
                for item in state:
                    field = item["name"]
                    value = item["value"]
                    field = re.sub(r'ori\((.*)\)', r'\1', field)
                    new_field = field.replace("$", "_")
                    new_value = "\"\"" if value == "" else value if value is not None else 0
                    state_predicates.append(f"{new_field} == {new_value}")
                trace.append([event_name, state_predicates])
            self.traces.append(trace)

    def getTraces(self):
        return self.traces

    def createBlueFringeMDL(self):
        method_traces = [[method_post[0]
                          for method_post in trace] for trace in self.traces]
        all_methods = set()
        [all_methods.update(method_trace) for method_trace in method_traces]
        with open(os.path.join(self.workdir, self.contractName+".method-traces.txt"), "w") as f:
            f.write("alphabet" + os.linesep)
            f.write(os.linesep.join(all_methods) + os.linesep)
            f.write("---------------------"+os.linesep)
            f.write("positive examples"+os.linesep)
            # for method_trace in method_traces:
            f.write(os.linesep.join([" ".join(method_trace)
                    for method_trace in method_traces]))
        cmd = f"bash ~/Project/InvConPlus/Dapp-Automata-data/offlineLearn.sh {self.workdir} {self.contractName}"
        os.system(cmd)

    def Ktail(self, k: int):
        tree = PrefixTree()
        ktail = KTail(tree=tree)
        for trace in self.traces:
            trace = [item[0] for item in trace]
            ktail.add(trace)
        try:
            ktail.k_tails(k)
        except:
            traceback.print_exc()
            assert False
        ktail.visualize(k, self.workdir)

    def sekt(self, k: int):
        ktail = SEKT_TAIL(self.fieldPredMapping)
        for trace in self.traces:
            ktail.add(trace)
        try:
            ktail.k_tails(k)
        except:
            traceback.print_exc()
            assert False
        ktail.visualize(k, self.workdir)

    def contractorplus(self):
        contractor = ContractorPlus(
            list(self.fieldPredMapping.keys()), self.pre_invariants, self.post_invariants)
        contractor.contractor()
        output_file = os.path.join(self.workdir, "contractorplus")
        contractor.visualize(output_file)

    def smcon(self):
        algo = SMCon(self.workdir, self.initialState, self.fields,
                     self.pre_invariants, self.post_invariants, self.traces)
        fsm = algo.smcon()
        return fsm


def _main(workdir, contract_name, slice_invariant_file, slice_configuration_file, trace_slice_file):
    if not os.path.exists(workdir):
        os.mkdir(workdir)
    training_percentage = 0.7
    slicer = InvariantSlice(
        slice_configuration=slice_configuration_file, invariant_file=slice_invariant_file)
    invariants = slicer.get_invariant_slice()
    json.dump(invariants, open(os.path.join(workdir, contract_name +
              "." + "invariant-preprocessed.json"), "w"), indent=4)

    miner = ConMiner(workdir=workdir, contractName=contract_name)
    miner.readPreProcessedSliceInvariant(invariants)
    miner.addTraces(trace_slice_file, percentage=training_percentage)

    # # RPNI

    # start = time.time()
    # miner.createBlueFringeMDL()
    # logging.warning("".join(["**"]*10))
    # logging.warning("RPNI")
    # logging.warning("Time spent {} seconds".format(time.time()-start))

    # SMCON

    start = time.time()
    miner.enableZeroIntialState()
    miner.smcon()
    logging.warning("".join(["**"]*10))
    logging.warning("SMCON ")
    logging.warning("Time spent {} seconds".format(time.time()-start))

    # ContractorPlus
    start = time.time()
    miner.contractorplus()
    logging.warning("".join(["**"]*10))
    logging.warning("ContractorPlus")
    logging.warning("Time spent {} seconds".format(time.time()-start))

    # Ktail
    start = time.time()
    miner.Ktail(1)
    logging.warning("".join(["**"]*10))
    logging.warning("K-Tail (1)")
    logging.warning("Time spent {} seconds".format(time.time()-start))

    start = time.time()
    miner.Ktail(2)
    logging.warning("".join(["**"]*10))
    logging.warning("K-Tail (2)")
    logging.warning("Time spent {} seconds".format(time.time()-start))

    # SEKtail
    start = time.time()
    miner.sekt(1)
    logging.warning("".join(["**"]*10))
    logging.warning("sekt_tail (1)")
    logging.warning("Time spent {} seconds".format(time.time()-start))

    start = time.time()
    miner.sekt(2)
    logging.warning("".join(["**"]*10))
    logging.warning("sekt_tail (2)")
    logging.warning("Time spent {} seconds".format(time.time()-start))

    return True


def test_project(workdir, project, invariant_dir, trace_dir):
    contract_name = project
    print(contract_name)
    try:
        invariant_file = os.path.join(invariant_dir, contract_name+".inv.json")
        trace_file = os.path.join(trace_dir, contract_name+".traces.json")
        _main(workdir=workdir, contract_name=contract_name,
              slice_invariant_file=invariant_file, slice_configuration_file=None,
              trace_slice_file=trace_file)
    except:
        traceback.print_exc()
        pass


def test():
    # workdir = "Dapp-Automata-data/fuzzer/testnetdata-model-rq1"
    # benchmark_dir = "Dapp-Automata-data/RQ1/azure-benchmark/workbench"
    # invariant_dir = "Dapp-Automata-data/fuzzer/testnetdata-inv"
    # trace_dir = "Dapp-Automata-data/fuzzer/testnetdata-traces"

    workdir = "Dapp-Automata-data/fuzzer/testnetdata-model-rq1-fix"
    benchmark_dir = "Dapp-Automata-data/RQ1/azure-benchmark/workbench-fix"
    invariant_dir = "Dapp-Automata-data/fuzzer/testnetdata-inv-fix"
    trace_dir = "Dapp-Automata-data/fuzzer/testnetdata-traces-fix"

    # test_project(workdir=workdir, project="DefectiveComponentCounter", invariant_dir=invariant_dir, trace_dir=trace_dir)

    projects = []
    for project in os.listdir(benchmark_dir):
        if not os.path.isdir(os.path.join(benchmark_dir, project)):
            continue
        projects.append(project)
    # with Pool(11) as pool:
    #     pool.starmap(test_project, zip(repeat(workdir), projects, repeat(invariant_dir), repeat(trace_dir)))
        test_project(workdir=workdir, project=project,
                     invariant_dir=invariant_dir, trace_dir=trace_dir)


def main(workdir, address, contractName, invariant_file, slice_configuration_file, trace_slice_file):
    if not os.path.exists(os.path.join(workdir, address)):
        os.mkdir(os.path.join(workdir, address))

    slicer = InvariantSlice(
        slice_configuration=slice_configuration_file, invariant_file=invariant_file)
    invariant = slicer.get_invariant_slice()
    json.dump(invariant, open(os.path.join(workdir, address+"-" +
              contractName+"_" + "invariant-preprocessed.json"), "w"), indent=4)

    miner = ConMiner(workdir=os.path.join(
        workdir, address), contractName=contractName)
    miner.readPreProcessedSliceInvariant(invariant)
    miner.addTraces(trace_slice_file)

    # miner.Ktail(0)
    # miner.Ktail(1)
    # miner.Ktail(2)
    # miner.createBlueFringeMDL()

    miner.enableZeroIntialState()
    fsm = miner.smcon()
    return True


if __name__ == "__main__":
    if len(sys.argv) == 1:
        test()
    else:
        workdir = sys.argv[1]
        address = sys.argv[2]
        contractName = sys.argv[3]
        invariant_file = sys.argv[4]
        slice_configuration_file = sys.argv[5]
        trace_slice_file = sys.argv[6]
        main(workdir, address, contractName, invariant_file,
             slice_configuration_file, trace_slice_file)
