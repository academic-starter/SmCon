from typing import List, Tuple
from typing_extensions import Self
from smcon.utils.graph import Graph, Node


class PrefixTree:
    def __init__(self) -> None:
        self.graph = Graph()
        rootNode = Node()
        self.graph.addNode(rootNode)
        self.graph.setRoot(rootNode)

    def add(self, trace):
        cur = self.graph.root
        for word in trace:
            if not self.graph.hasTransition(cur, word):
                node = Node()
                self.graph.addTransition(cur, word, node)
            assert word is not None
            curIndex = self.graph.transitions[cur.unique_id][word][0]
            cur = list(filter(lambda node: node.unique_id ==
                       curIndex, self.graph.nodes))[0]

    def suffix(self, node: Node, k: int):
        return self.graph.suffix(node, k)


class DataNode(Node):
    concrete_vals: List[List[str]]

    def __init__(self) -> None:
        super().__init__()
        self.concrete_vals = []

    def merge(self, node: Self) -> None:
        self.concrete_vals.extend(node.concrete_vals)

    def add_concrete_val(self, concrete_val):
        self.concrete_vals.append(concrete_val)


class DataPrefixTree():
    def __init__(self) -> None:
        self.graph = Graph()
        rootNode = DataNode()
        self.graph.addNode(rootNode)
        self.graph.setRoot(rootNode)

    def add(self, trace: List[Tuple[str, List[str]]]):
        cur: DataNode = self.graph.root
        for item in trace:
            word, concrete_val = item
            if not self.graph.hasTransition(cur, word):
                node = DataNode()
                self.graph.addTransition(cur, word, node)

            assert word is not None
            curIndex = self.graph.transitions[cur.unique_id][word][0]
            cur = list(filter(lambda node: node.unique_id ==
                       curIndex, self.graph.nodes))[0]
            cur.add_concrete_val(concrete_val=concrete_val)

    def suffix(self, node: Node, k: int):
        return self.graph.suffix(node, k)
