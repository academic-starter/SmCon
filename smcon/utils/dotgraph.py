import simplejson as json
import os 
from typing import List, Dict, Set
from graph import Graph, Node

class DotGraph(Graph):
    def __init__(self) -> None:
        super().__init__()

    def loadDotGraphJson(self, dot_graph_json):
        dot_graph = json.load(open(dot_graph_json))
        objects = dot_graph["objects"]
        edges = dot_graph["edges"]
        node_map = dict() 
        for item in objects:
            gvid = item["_gvid"]
            shape = item["shape"]
            label = item["label"]
            if shape != "none" and label is not None and label!="":
                node = Node()
                self.addNode(node)
                node_map[gvid] = node 
        
        for edge in edges:
            tail = edge["tail"]
            head = edge["head"]
            label = edge["label"]
            if label == "":
                # root node
                self.setRoot(node_map[head])
            else:
                assert tail in node_map and head in node_map
                self.addTransition(node_map[tail], label.split("@")[0], node_map[head])

        return 

    def statistics(self):
        state_number = len(self.nodes)
        transition_number = 0
        for from_id in self.transitions:
            for label in self.transitions[from_id]:
                to_ids = self.transitions[from_id][label]
                transition_number += len(to_ids)

      
        return state_number, transition_number

    def applyDeterministism(self):
        stable = False
        while not stable: 
            stable = True
            for from_id in self.transitions:
                for label in self.transitions[from_id]:
                    to_ids = self.transitions[from_id][label]
                    if len(to_ids) > 1:
                        left = list(filter(lambda x: x.unique_id == to_ids[0], self.nodes))[0]
                        right = list(filter(lambda x: x.unique_id == to_ids[1], self.nodes))[0]
                        self.merge(left, right)
                        stable = False
                        break 
                if not stable:
                    break    
    


def batch_statistics():
    Files = ["Dapp-Automata-data/result/model-fix/0x1f52b87c3503e537853e160adbf7e330ea0be7c4/SaleClockAuction/FSM-3.gv","Dapp-Automata-data/result/gamechannel/0xaec1f783b29aab2727d7c374aa55483fe299fefa/GameChannel/FSM-8.gv", "Dapp-Automata-data/result/model-fix/0x41a322b28d0ff354040e2cbc676f0320d8c8850d/SupeRare/FSM-17-edit.gv", "Dapp-Automata-data/result/model-fix/0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6/MoonCatRescue/FSM-14.gv", "Dapp-Automata-data/result/model/0xa8f9c7ff9f605f401bde6659fd18d9a0d0a802c5/RpsGame/FSM-4.gv", "Dapp-Automata-data/result/model-fix/0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb/CryptoPunksMarket/FSM-21.gv"]
    for file in Files:
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

def make_deterministic():
    Files = ["Dapp-Automata-data/result/model-fix/0x1f52b87c3503e537853e160adbf7e330ea0be7c4/SaleClockAuction/FSM-3.gv","Dapp-Automata-data/result/gamechannel/0xaec1f783b29aab2727d7c374aa55483fe299fefa/GameChannel/FSM-8.gv", "Dapp-Automata-data/result/model/0x41a322b28d0ff354040e2cbc676f0320d8c8850d/SupeRare/FSM-17.gv", "Dapp-Automata-data/result/model/0x60cd862c9c687a9de49aecdc3a99b74a4fc54ab6/MoonCatRescue/FSM-20.gv", "Dapp-Automata-data/result/model/0xa8f9c7ff9f605f401bde6659fd18d9a0d0a802c5/RpsGame/FSM-4.gv", "Dapp-Automata-data/result/model/0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb/CryptoPunksMarket/FSM-21.gv"]
    for file in Files:
        targetFile = file+".json"
        cmd = "dot -Txdot_json -o{0} {1}".format(targetFile, file)
        os.system(cmd + " >/dev/null 2>&1")
        graph =  DotGraph()
        graph.loadDotGraphJson(targetFile)
        graph.applyDeterministism()

        state_number, transition_number = graph.statistics()
        print("".join(["**"]*10))
        print(file)
        print("state number: ", state_number)    
        print("transition number: ", transition_number)

        graph.visualize(file+".dfa")


if __name__ == "__main__":
    # dot_graph_json = "Dapp-Automata-data/fuzzer/testnetdata-model/AssetTransfer/BlueFringeMDLDFA.json"
    # graph = DotGraph()
    # graph.loadDotGraphJson(dot_graph_json=dot_graph_json)
    batch_statistics()
    # make_deterministic()
