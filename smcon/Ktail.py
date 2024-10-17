"""
 * Implements the KTails algorithm as defined in Biermann & Feldman '72.
"""
import json
import argparse
from typing import List
from automathon import NFA
from smcon.PrefixTree import PrefixTree, Node


class KTail:
    def __init__(self, tree: PrefixTree = PrefixTree()) -> None:
        self.tree = tree

    def add(self, trace: List[str]):
        self.tree.add(trace)

    @property
    def initialState(self):
        return self.tree.graph.root

    @property
    def states(self):
        return self.tree.graph.nodes

    @property
    def transitions(self):
        return self.tree.graph.transitions

    def valid_merge(self, node1, node2, suffix1, suffix2):
        if suffix1 == suffix2 and len(suffix1) > 0:
            self.tree.graph.merge(node1, node2)
            return True
        else:
            return False

    def k_tails(self,  k: int):
        if k == 0:
            return None
        # tree = self.tree
        # for i in range(len(tree.graph.nodes)):
        #         for j in range(i+1, len(tree.graph.nodes)):
        #             node1 = tree.graph.nodes[i]
        #             node2 = tree.graph.nodes[j]
        #             # suffix1 = tree.suffix(node1, k)
        #             # suffix2 = tree.suffix(node2, k)
        #             # if suffix1 == suffix2 and len(suffix1) > 0:
        #             if self.valid_merge(node1, node2, k):
        #                 tree.graph.merge(node1, node2)
        #                 return self.k_tails(k)
        # return None

        stable = False
        while not stable:
            stable = True
            tree = self.tree
            cached = dict()
            for i in range(len(tree.graph.nodes)):
                node1: Node = tree.graph.nodes[i]

                if node1.unique_id not in cached:
                    suffix1 = tree.suffix(node1, k)
                    cached[node1.unique_id] = suffix1
                else:
                    suffix1 = cached[node1.unique_id]

                if len(suffix1) == 0:
                    continue

                for j in range(i+1, len(tree.graph.nodes)):
                    node2 = tree.graph.nodes[j]
                    if node2.unique_id not in cached:
                        suffix2 = tree.suffix(node2, k)
                        cached[node2.unique_id] = suffix2
                    else:
                        suffix2 = cached[node2.unique_id]

                    if len(suffix2) == 0:
                        continue
                    if self.valid_merge(node1, node2, suffix1=suffix1, suffix2=suffix2):
                        stable = False
                        break
                if stable is False:
                    break
        return None

    def visualize(self, k, workdir):
        self._visualize(k, workdir=workdir, name="Ktail")

    def _visualize(self, k, workdir, name):
        states = set()
        labels = set()
        string_transitions = dict()
        for from_state in self.transitions:
            real_from_state = list(
                filter(lambda node: node.unique_id == from_state, self.states))[0]
            states.add(str(self.states.index(real_from_state)))
            # if not self.tree.graph.isConnect(self.initialState, real_from_state):
            #     continue
            if self.states.index(real_from_state) not in string_transitions:
                string_transitions[str(
                    self.states.index(real_from_state))] = dict()
            for label in self.transitions[from_state]:
                if label is None:
                    continue
                to_states = self.transitions[from_state][label]
                for to_state in to_states:
                    real_to_state = list(
                        filter(lambda node: node.unique_id == to_state, self.states))[0]
                    states.add(str(self.states.index(real_to_state)))
                    req_label = str(label)
                    req_label = req_label.split("@")[0]
                    labels.add(req_label)
                    if req_label not in string_transitions[str(self.states.index(real_from_state))]:
                        string_transitions[str(self.states.index(
                            real_from_state))][req_label] = set()
                    string_transitions[str(self.states.index(real_from_state))][req_label].add(
                        str(self.states.index(real_to_state)))

        for from_state in string_transitions:
            for label in string_transitions[from_state]:
                string_transitions[from_state][label] = list(
                    string_transitions[from_state][label])

        initialState = str(self.states.index(self.initialState))
        nfa = NFA(
            Q=states,
            sigma=labels,
            delta=string_transitions,
            initialState=initialState,
            F=set()
        )
        nfa.view(f"{workdir}/{name}-{k}")

        result = {
            "states": list(states),
            "statemachine": string_transitions,
            "initialState": initialState
        }
        json.dump(result, open(f"{workdir}/{name}-{k}.json", "w"))


def translate_trace(trace):
    result = []
    for item in trace:
        funcName = item[0]
        assert isinstance(funcName, str)
        result.append(funcName)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--workdir", type=str, required=True)
    parser.add_argument("--k", type=int, required=True)
    args = parser.parse_args()
    traces = json.load(open(args.input, "r"))
    ktail = KTail()
    for trace_id in traces:
        ktail.add(translate_trace(traces[trace_id]))
    import time
    start_time = time.time()
    ktail.k_tails(args.k)
    print("--- %s seconds ---" % (time.time() - start_time))
    # ktail.visualize(args.k, args.workdir)


if __name__ == "__main__":
    main()
