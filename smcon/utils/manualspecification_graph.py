import os 
import simplejson as json 
from graph import Graph, Node 


class ManualSpecificationGraph(Graph):
    def __init__(self) -> None:
        super().__init__()
        self.words = set()
    
    def strings(self, groundtruth_transition_number):
        if len(self.words) == 0:
            self.words = super().strings(groundtruth_transition_number=groundtruth_transition_number)
        return self.words
    
    def loadSpecification(self, spec_json_file):
        spec = json.load(open(spec_json_file))
        statemachine = spec["statemachine"]
        start_state_name = "0"
        node_map = dict()
        for from_state_name in statemachine:
            if from_state_name not in node_map:
                from_state = Node()
                node_map[from_state_name] = from_state
            else:
                from_state = node_map[from_state_name]

            for method in statemachine[from_state_name]:
                if isinstance(statemachine[from_state_name][method], str):
                    to_state_name = statemachine[from_state_name][method]
                    if to_state_name not in node_map:
                        to_state = Node()
                        node_map[to_state_name] = to_state
                    else:
                        to_state = node_map[to_state_name]
                    self.addTransition(fromNode=from_state, label=method, toNode=to_state)
                elif isinstance(statemachine[from_state_name][method], list):
                    for to_state_name in statemachine[from_state_name][method]:
                        if to_state_name not in node_map:
                            to_state = Node()
                            node_map[to_state_name] = to_state
                        else:
                            to_state = node_map[to_state_name]
                        self.addTransition(fromNode=from_state, label=method, toNode=to_state)
                else:
                    assert False, "unknown transition"
        assert start_state_name in node_map
        rootNode = node_map[start_state_name]
        self.setRoot(rootNode)
        output_file = os.path.join(os.path.dirname(spec_json_file), os.path.basename(spec_json_file).replace(".json", "-dot"))
        self.visualize(output_file=output_file)
        return 


if __name__ == "__main__":
    spec_json_file = "Dapp-Automata-data/RQ2/Groundtruth/ideal/MoonCatRescue.json"
    contract_name = "MoonCatRescue"
    graph = ManualSpecificationGraph()
    graph.loadSpecification(spec_json_file, contract_name)