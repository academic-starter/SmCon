import os 
import simplejson as json 
from graph import Graph, Node 


class SpecificationGraph(Graph):
    def __init__(self) -> None:
        super().__init__()
        self.words = set()
    
    def strings(self, groundtruth_transition_number):
        if len(self.words) == 0:
            self.words = super().strings(groundtruth_transition_number=groundtruth_transition_number)
        return self.words
    
    def loadSpecification(self, spec_json_file, contract_name):
        spec = json.load(open(spec_json_file))
        workflows = spec["Workflows"]
        workflow = list(filter(lambda x: x["Name"] == contract_name, workflows))[0]
        start_state_name = workflow["StartState"]
        states = workflow["States"]
        node_map = dict() 
        for state in states:
            state_name = state["Name"]
            if state_name in node_map:
                node = node_map[state_name]
            else:
                node = Node() 
                self.addNode(node)
                node_map[state_name] = node
            transitions = state["Transitions"]
            for transition in transitions:
                method = transition["Function"]
                next_state_names = transition["NextStates"]
                for next_state_name in next_state_names:
                    if next_state_name in node_map:
                        toNode = node_map[next_state_name]
                    else:
                        toNode = Node()
                        self.addNode(node)
                        node_map[next_state_name] = toNode
                    self.addTransition(node, method, toNode)
        rootNode = Node()
        self.addNode(rootNode)
        self.addTransition(rootNode, "constructor", node_map[start_state_name])
        self.setRoot(rootNode)

        # for node in self.nodes:
        #     matched = False
        #     if node.unique_id in self.transitions:
        #         matched = True 
        #     else:
        #         for other_node_id in self.transitions:
        #             for label in self.transitions[other_node_id]:
        #                 for to_node_id in self.transitions[other_node_id][label]:
        #                     if to_node_id == node.unique_id:
        #                         matched = True
        #     assert matched != False
        output_file = os.path.join(os.path.dirname(spec_json_file), os.path.basename(spec_json_file).replace(".json", "-dot"))
        self.visualize(output_file=output_file)
        return 


if __name__ == "__main__":
    spec_json_file = "Dapp-Automata-data/RQ1/azure-benchmark/workbench/AssetTransfer/AssetTransfer.json"
    contract_name = "AssetTransfer"
    graph = SpecificationGraph()
    graph.loadSpecification(spec_json_file, contract_name)
    output_file = "Dapp-Automata-data/RQ1/azure-benchmark/workbench/AssetTransfer/AssetTransfer-dot"
    graph.visualize(output_file)