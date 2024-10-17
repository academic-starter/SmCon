import os 
import glob 

import simplejson as json 
from graph import Graph 
from azurespecification_graph import SpecificationGraph 
from manualspecification_graph import ManualSpecificationGraph
from dotgraph import DotGraph 

class GraphDiff:
    left: Graph 
    right: Graph 
    def __init__(self, left, right):
        # left is the ground truth model while the right is evaluted model
        self.left = left
        self.right = right
    
    def diff(self):
        results = []
        groundtruth_transition_number = sum([sum([ len(self.left.transitions[node_id][label]) for label in self.left.transitions[node_id]] ) for node_id in self.left.transitions])
        groundtruth_state_number = len(self.left.nodes)
        print("ground truth state numbder: {}".format(groundtruth_state_number))
        print("ground truth transition numbder: {}".format(groundtruth_transition_number))

        right_transition_number = sum([sum([ len(self.right.transitions[node_id][label]) for label in self.right.transitions[node_id]] ) for node_id in self.right.transitions])
        right_state_number = len(self.right.nodes)
        print("model state numbder: {}".format(right_state_number))
        print("model transition numbder: {}".format(right_transition_number))
        
        
        strings = self.left.strings(groundtruth_transition_number=groundtruth_transition_number) 
        for string in strings:
            if self.right.accept(string):
                results.append(string)
        leftbase_righttest = len(results)/len(strings)
        print("recall = {}".format(leftbase_righttest))

        failed_results = []
        results = []
        strings = self.right.strings(groundtruth_transition_number=groundtruth_transition_number) 
        for string in strings:
            if self.left.accept(string):
                results.append(string)
            else:
                failed_results.append(string)
        rightbase_lefttest = len(results)/len(strings)
        print("precision = {}".format(rightbase_lefttest))

        # json.dump(failed_results, open("./failed_traces.json", "w"), indent = 4)

        return groundtruth_state_number, groundtruth_transition_number, right_state_number, right_transition_number, leftbase_righttest, rightbase_lefttest
    
    def diff_testing_traces(self, test_traces_file):
        training_percentage = 0.7
        test_traces = json.load(open(test_traces_file))
        test_event_traces = [test_trace["event_trace"] for test_trace in  test_traces[int(training_percentage*len(test_traces)):]]
        test_strings = []
        for test_even_trace in test_event_traces:
            test_string = [item["methodName"].split("(")[0] for item in test_even_trace]
            test_strings.extend([ test_string[:i] for i in range(1, len(test_string))])
        results = [] 
        assert self.left is None
        for string in test_strings:
            if self.right.accept(string):
                results.append(string)
        test_case_accuracy = len(results)/len(test_strings)
        print("test_case_accuracy = {}".format(test_case_accuracy))
        return test_case_accuracy

def compute_result():

    # test_traces_dir = "Dapp-Automata-data/fuzzer/testnetdata-traces"
    # workdir = "Dapp-Automata-data/fuzzer/testnetdata-model-rq1"
    # benchmark_dir = "Dapp-Automata-data/RQ1/azure-benchmark/workbench"
    

    test_traces_dir = "Dapp-Automata-data/fuzzer/testnetdata-traces-fix"
    workdir = "Dapp-Automata-data/fuzzer/testnetdata-model-rq1-fix"
    benchmark_dir = "Dapp-Automata-data/RQ1/azure-benchmark/workbench-fix"
    
   
    # with open("./Dapp-Automata-data/rq1-result.csv", "w")  as f:
    with open("./Dapp-Automata-data/rq1-result-fix.csv", "w")  as f:
            f.write("{}, {}, {}, {}, {}, {}, {}, {}, {}\n".format("project", "ground truth state", "ground truth transition",  "result", "result state", "result transition",  "recall", "precision", "test_case_accuracy"))
            
    for project in os.listdir(benchmark_dir):
            if not os.path.isdir(os.path.join(benchmark_dir, project)):
                continue 
            spec_json_file = os.path.join(benchmark_dir, project, project+".json")
            test_traces_file = os.path.join(test_traces_dir, project+".traces.json")
            if not os.path.exists(spec_json_file):
                print(spec_json_file + " not exists!")
            else:
                print(project)
                spec_graph = SpecificationGraph()
                spec_graph.loadSpecification(spec_json_file=spec_json_file, contract_name=project)
                
                project_result_dir = os.path.join(workdir, project)
                files_grabbed = [glob.glob(e) for e in [project_result_dir+"/*.dot", project_result_dir+"/*.gv"]]
                for files in files_grabbed:
                    for file in files:
                        targetFile = file + ".json"
                        cmd = "dot -Txdot_json -o{0} {1}".format(targetFile, file)
                        os.system(cmd + " >/dev/null 2>&1")
                        graph = DotGraph()
                        graph.loadDotGraphJson(targetFile)
                        print("".join(["**"]*10))
                        print(os.path.basename(file))
                        diff = GraphDiff(None, graph)
                        test_case_accuracy = diff.diff_testing_traces(test_traces_file=test_traces_file)
                        
                        
                        diff =  GraphDiff(spec_graph, graph)
                        g_state_number, g_transition_number, m_state_number, m_transition_number, recall, precision = diff.diff()
                        # with open("./Dapp-Automata-data/rq1-result.csv", "a")  as f:
                        with open("./Dapp-Automata-data/rq1-result-fix.csv", "a")  as f:
                            f.write("{}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(project,  g_state_number, g_transition_number, os.path.basename(file), m_state_number, m_transition_number, recall, precision, test_case_accuracy))
            


def testDiffTestCase():
    dot_graph_json = "Dapp-Automata-data/fuzzer/testnetdata-model/AssetTransfer/BlueFringeMDLDFA.json"
    graph = DotGraph()
    graph.loadDotGraphJson(dot_graph_json=dot_graph_json)

    test_traces_dir = "Dapp-Automata-data/fuzzer/testnetdata-traces"
    test_traces_file = os.path.join(test_traces_dir, "AssetTransfer.traces.json")
    diff = GraphDiff(None, graph)
    test_case_accuracy = diff.diff_testing_traces(test_traces_file=test_traces_file)
    print(os.path.basename(dot_graph_json))
    print("test case accuracy = {}".format(test_case_accuracy))       



def testDApp():
    Files = ["Dapp-Automata-data/result/gamechannel/0xaec1f783b29aab2727d7c374aa55483fe299fefa/GameChannel/FSM-8.gv", "Dapp-Automata-data/result/model-fix/0x41a322b28d0ff354040e2cbc676f0320d8c8850d/SupeRare/FSM-17-edit.gv", "Dapp-Automata-data/result/model-fix/0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6/MoonCatRescue/FSM-14.gv", "Dapp-Automata-data/result/model-fix/0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb/CryptoPunksMarket/FSM-21.gv"]
    Specs = ["Dapp-Automata-data/RQ2/Groundtruth/ideal/GameChannel-0xaec1f783b29aab2727d7c374aa55483fe299fefa.json", "Dapp-Automata-data/RQ2/Groundtruth/ideal/SupeRare.json", "Dapp-Automata-data/RQ2/Groundtruth/ideal/MoonCatRescue.json", "Dapp-Automata-data/RQ2/Groundtruth/ideal/CryptoPunksMarket.json"]
    for i in range(len(Files)):
        file = Files[i]
        targetFile = file+".json"
        cmd = "dot -Txdot_json -o{0} {1}".format(targetFile, file)
        os.system(cmd + " >/dev/null 2>&1")
        graph =  DotGraph()
        graph.loadDotGraphJson(targetFile)
        state_number, transition_number = graph.statistics()
        print("".join(["**"]*10))
        print(file)
        print("state number: ", state_number)    
        print("transition number: ", transition_number)

        spec_json_file =  Specs[i]
        spec_graph = ManualSpecificationGraph()
        spec_graph.loadSpecification(spec_json_file)

        diff = GraphDiff(spec_graph, graph)
        groundtruth_state_number, groundtruth_transition_number, right_state_number, right_transition_number, recall, precision = diff.diff()
        print("recall = {}, precision = {}".format(recall, precision))


def test():
    dot_graph_json = "Dapp-Automata-data/fuzzer/testnetdata-model-rq1-fix/Starter/contractorplus.gv.json"
    graph = DotGraph()
    graph.loadDotGraphJson(dot_graph_json=dot_graph_json)
    
    # dot_graph_json = "Dapp-Automata-data/fuzzer/testnetdata-model-rq1/AssetTransfer/contractorplus.gv.json"
    # graph = DotGraph()
    # graph.loadDotGraphJson(dot_graph_json=dot_graph_json)

    spec_json_file = "Dapp-Automata-data/RQ1/azure-benchmark/workbench-fix/Starter/Starter.json"
    contract_name = "Starter"
    spec_graph = SpecificationGraph()
    spec_graph.loadSpecification(spec_json_file, contract_name)

    diff = GraphDiff(spec_graph, graph)
    groundtruth_state_number, groundtruth_transition_number, right_state_number, right_transition_number, recall, precision = diff.diff()
    print("recall = {}, precision = {}".format(recall, precision))

if __name__ == '__main__':
    # compute_result()
    # test()
    testDApp()
    