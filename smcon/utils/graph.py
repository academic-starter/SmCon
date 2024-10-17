
import random 
from typing_extensions import Self
from automathon import NFA

class Node:
    def __init__(self) -> None:
        pass

    def merge(self, node: Self) ->None:
        pass 

    @property
    def unique_id(self):
        return self.__hash__()

class Graph:
    root: Node = None 
    def __init__(self) -> None:
        self.nodes = []
        self.transitions = dict() 
        
    def setRoot(self, root: Node):
        self.root = root

    def addNode(self, node: Node):
        if node not in self.nodes:
            self.nodes.append(node)
            # print("AddNode: {}".format(node.unique_id))

    def addTransition(self, fromNode, label, toNode):
        if label is None:
            return 
        if fromNode not in self.nodes:
            self.addNode(fromNode)
        if toNode not in self.nodes:
            self.addNode(toNode)
        if fromNode.unique_id not in self.transitions:
            self.transitions[fromNode.unique_id] = dict()
        if label not in self.transitions[fromNode.unique_id]:
            self.transitions[fromNode.unique_id][label] = [toNode.unique_id]
        else:
            if toNode.unique_id not in self.transitions[fromNode.unique_id][label]:
                self.transitions[fromNode.unique_id][label].append(toNode.unique_id)
        
    def parents(self, node: Node):
        parents = set()
        for from_index in self.transitions:
            for label in self.transitions[from_index]:
                to_indice = self.transitions[from_index]
                if any(map(lambda index: index == node.unique_id, to_indice)):
                    parents.add(from_index)
        
        node_parents = list(filter(lambda node: node.unique_id in parents, self.nodes))
        return node_parents
    
    def children(self, node: Node):
        children = set()
        for from_index in self.transitions:
            if from_index == node.unique_id:
                for label in self.transitions[from_index]:
                    to_indice = self.transitions[from_index][label]
                    children.update(to_indice)
            
        node_children = list(filter(lambda node: node.unique_id in children, self.nodes))
        return node_children
    
    def outcomming_transitions(self, node: Node):
        out_transitions = set()
        for from_index in self.transitions:
            if from_index == node.unique_id:
                for label in self.transitions[from_index]:
                    to_indice = self.transitions[from_index][label]
                    for to_index in to_indice:
                        out_transitions.add((from_index, label, to_index))
        return out_transitions
    
    def incomming_transitions(self, node: Node):
        in_transitions = set()
        for from_index in self.transitions:
                for label in self.transitions[from_index]:
                    for to_index in self.transitions[from_index][label]:
                        if to_index == node.unique_id:
                            in_transitions.add((from_index, label, to_index))
        return in_transitions
    
    def removeNode(self, node: Node):
        if node in self.nodes:
            self.nodes.remove(node)
            # print("RmNode: {}".format(node.unique_id))
        
        # for from_index in self.transitions:
        #     assert from_index != node.unique_id
        #     for label in self.transitions[from_index]:
        #         for to_index in self.transitions[from_index][label]:
        #             assert to_index != node.unique_id

    def removeTransition(self, from_index: int, label:str, to_index: int):
        # print("RmTransition: {} {} {}".format(from_index, label, to_index))
        if from_index in self.transitions:
            if label in self.transitions[from_index]:
                if to_index in self.transitions[from_index][label]:
                    self.transitions[from_index][label].remove(to_index)
                    if len(self.transitions[from_index][label]) == 0:
                        self.transitions[from_index].pop(label, None)
            if len(self.transitions[from_index]) == 0:
                del self.transitions[from_index]
    
    def hasNode(self, node):
        return node in self.nodes
    
    def hasTransition(self, from_node: Node, label: str):
        if from_node not in self.nodes:
            return False 
        from_index = from_node.unique_id
        if from_index not in self.transitions:
            return False 
        return label in self.transitions[from_index]


    def merge(self, node1: Node, node2: Node):
        # delete node1 and its transition and merge all transitions to node2
        if node1 == self.root:
            # do not delete root node
            node1 = node2 
            node2 = self.root 

        node1_index = node1.unique_id

        incomming_transitions1 = self.incomming_transitions(node1)
        outcomming_transitions1 = self.outcomming_transitions(node1)

        for transition in incomming_transitions1:
            from_index, label, to_index = transition

            self.removeTransition(from_index, label, to_index)

        for transition in outcomming_transitions1:
            from_index, label, to_index = transition
            self.removeTransition(from_index, label, to_index)

        for transition in incomming_transitions1:
            from_index, label, to_index = transition
            if from_index == to_index:
                # loop transition
                assert to_index == node1_index
                self.addTransition(fromNode=node2, label=label, toNode=node2)
            else:
                from_nodes = list(filter(lambda node: node.unique_id == from_index, self.nodes))
                assert len(from_nodes) == 1
                from_node = from_nodes[0]
                self.addTransition(fromNode=from_node, label=label, toNode=node2)

        for transition in outcomming_transitions1:
            from_index, label, to_index = transition
            if from_index == to_index:
                assert to_index == node1_index
                # loop transition has been processed above
                pass 
            else:
                to_nodes = list(filter(lambda node: node.unique_id == to_index, self.nodes))
                assert len(to_nodes) == 1
                to_node = to_nodes[0]
                self.addTransition(fromNode=node2, label=label, toNode = to_node)
        
        self.removeNode(node1)

        node2.merge(node1)

        return  


    def isConnect(self, curNode, targetNode, visited = []):
        if curNode == targetNode:
            return True
        if curNode.unique_id not in self.transitions:
            return False
        if (curNode.unique_id, targetNode.unique_id) in visited:
            return False
        visited.append((curNode.unique_id, targetNode.unique_id))

        for label in self.transitions[curNode.unique_id]:
            nextNodeIndex = self.transitions[curNode.unique_id][label]
            nextNode = list(filter(lambda node: node.unique_id == nextNodeIndex, self.nodes))[0]
            if self.isConnect(nextNode, targetNode, visited = visited):
                return True
        return False
    
    
    def suffix(self, node: Node, k :int) -> set:
        result =  [] 
        def dfs(node_id: int, k: int, path: list):
            if k == 0:
                result.append(path)
                return
            if node_id not in self.transitions:
                result.append(path)
                return 
            for label in self.transitions[node_id]:
                path.append(label)
                next_node_ids = self.transitions[node_id][label]
                for next_node_id in next_node_ids:
                    dfs(next_node_id, k-1, path)

        start_node_index = node.unique_id
        dfs(start_node_index, k, [])
        return set([ " ".join(path) for path in result])

    def strings(self, groundtruth_transition_number):  
        # @criteria: each state or transition should be visited 100 times
        """
https://people.cs.umass.edu/~brun/pubs/pubs/Krka14fse.pdf
Automatic Mining of Specifications
from Invocation Traces and Method Invariants

Since the evaluated models
can have infinite traces, we restricted the length of the traces to twice
the number of transitions in the ground-truth model.
        """ 
        min_support = 20
        Loop_test_min = 2
        MAX_SEQ_LENGTH = groundtruth_transition_number if groundtruth_transition_number < 20 else 20
        max_seq_number = 10000
        max_seq_length = MAX_SEQ_LENGTH*20+1
        results = []
        satisfy_states = set()
        satisify_transitions = set()
        statistics_transitions = dict()
        statistics_states = dict()

        def count_states():
            for node in self.nodes:
                if node.unique_id in satisfy_states:
                    continue
                if statistics_states.get(node.unique_id, 0) < min_support:
                    return False
                else:
                    satisfy_states.add(node.unique_id)
            return True

        def count_transitions():
            if len(statistics_transitions) == 0:
                return False
            matched = True
            for transition in statistics_transitions:
                if statistics_transitions.get(transition) < min_support:
                    matched = False
                else:
                    satisify_transitions.add(transition)
            return matched

        def gen_string(node_id: int, seq: list):
            statistics_states[node_id] =  statistics_states.get(node_id, 0)+1
            if node_id not in self.transitions or len(seq) >= max_seq_length or " ".join(map(str, seq)).count(" ".join(map(str,seq[-2:]))) > Loop_test_min:
                return seq 
            else:
                labels = list(self.transitions[node_id].keys())
                while True:
                    choice = random.randint(0, len(labels)-1)
                    label = labels[choice]
                    next_state_ids = self.transitions[node_id][label]
                    choice = random.randint(0, len(next_state_ids)-1)
                    next_state_id = next_state_ids[choice]
                    if (node_id, label, next_state_id) in satisify_transitions:
                        if random.random() < 0.5:
                            statistics_transitions[(node_id, label, next_state_id)] = statistics_transitions.get(((node_id, label, next_state_id)), 0) + 1
                            return gen_string(next_state_id, seq+[label, next_state_id])
                        else:
                            continue    
                    else:
                        statistics_transitions[(node_id, label, next_state_id)] = statistics_transitions.get(((node_id, label, next_state_id)), 0) + 1
                        return gen_string(next_state_id, seq+[label, next_state_id])

        roots = set([node.unique_id for node in self.nodes])
        for node_id in self.transitions:
            for label in self.transitions[node_id]:
                roots.difference_update(self.transitions[node_id][label])
        roots = list(roots)
        if len(roots) == 0:
            roots = [self.root.unique_id]
        assert len(roots)>0, "must have at least one root"      
        while not count_transitions() and len(results) < max_seq_number:
            for root in roots:
                seq = gen_string(root, [root])
                results.append(seq)

        # post-processing
        new_results = [ list(filter(lambda x: isinstance(x, str), result)) for result in results] 
        # new_results = []
        # for result in results:
        #     label_string = list(filter(lambda x: isinstance(x, str), result))
        #     # new_results.append(label_string)
        #     new_results.extend([label_string[:i+1] for i in range(0, len(label_string))])   
        return new_results

    def accept(self, seq:list):
        def _accept(node_id: int, _seq):
            if len(_seq) == 0: 
                return True 
            
            if node_id not in self.transitions:
                return False
            
            if _seq[0] in self.transitions[node_id]:
                label = _seq[0]

                accepted = False
                for next_state_id in self.transitions[node_id][label]:
                    if _accept(next_state_id, _seq[1:]):
                        accepted = True
                        break 
                return accepted
            else:
                return False 

        return _accept(self.root.unique_id, seq)
    
    def visualize(self, output_file):
        states = set()
        labels = set()
        string_transitions = dict()
        for from_state in self.transitions:
            real_from_state = list(filter(lambda node: node.unique_id == from_state, self.nodes))[0]
            states.add(str(self.nodes.index(real_from_state)))
            # if not self.tree.graph.isConnect(self.initialState, real_from_state):
            #     continue
            if self.nodes.index(real_from_state) not in string_transitions:
                string_transitions[str(self.nodes.index(real_from_state))] =  dict() 
            for label in self.transitions[from_state]:
                    if label is None:
                        continue
                    to_states = self.transitions[from_state][label]
                    for to_state in to_states:
                        real_to_state = list(filter(lambda node: node.unique_id == to_state, self.nodes))[0]
                        states.add(str(self.nodes.index(real_to_state)))
                        req_label = str(label)
                        req_label = req_label.split("@")[0]
                        labels.add(req_label)
                        if req_label not in string_transitions[str(self.nodes.index(real_from_state))]:
                            string_transitions[str(self.nodes.index(real_from_state))][req_label] = set() 
                        string_transitions[str(self.nodes.index(real_from_state))][req_label].add(str(self.nodes.index(real_to_state)))
        
        for from_state in string_transitions:
            for label in string_transitions[from_state]:
                string_transitions[from_state][label] = list(string_transitions[from_state][label])

        initialState = str(self.nodes.index(self.root))
        nfa = NFA(
           Q=states,
           sigma= labels,
           delta= string_transitions,
           initialState= initialState,
           F = set()
        )
        nfa.view(output_file)
