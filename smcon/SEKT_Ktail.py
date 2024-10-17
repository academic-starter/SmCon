import copy
from typing import Set, Dict, List, Tuple
from smcon.Ktail import KTail
from smcon.PrefixTree import DataPrefixTree, DataNode
from smcon.specAutomata import SMT_ImplyTwoPredicateSets


class SEKT_TAIL(KTail):
    def __init__(self, pred_mapping: Dict[str, Set]):
        self.pred_mapping = pred_mapping
        self.variables = frozenset(self.pred_mapping.keys())
        self.preds = set()
        for variable in self.variables:
            self.preds.update(self.pred_mapping[variable])
        tree = DataPrefixTree()
        super().__init__(tree=tree)

    def get_visited_statetraces(self, node: DataNode):
        return node.concrete_vals

    def sat(self, predicate, program_state: List[str]):
        for pred in copy.copy(program_state):
            if pred.split(" ")[0].strip() not in self.variables:
                program_state.remove(pred)
        if SMT_ImplyTwoPredicateSets(self.variables, tuple(program_state), tuple([predicate])):
            return True
        else:
            return False

    def eval_state_consistency(self, node1, node2):

        left_concrete_vals = self.get_visited_statetraces(node1)
        right_concrete_vals = self.get_visited_statetraces(node2)

        # exists a new state q: where left_concrete_vals ==> q and right_concrete_vals ==> q
        left_satisifed_predicates = set()
        for predicate in self.preds:
            for program_state in left_concrete_vals:
                if self.sat(predicate, program_state):
                    left_satisifed_predicates.add(predicate)
                else:
                    left_satisifed_predicates.discard(predicate)

        right_satisifed_predicates = set()
        for predicate in self.preds:
            for program_state in right_concrete_vals:
                if self.sat(predicate, program_state):
                    right_satisifed_predicates.add(predicate)
                else:
                    right_satisifed_predicates.discard(predicate)

        if left_satisifed_predicates == right_satisifed_predicates:
            return True
        else:
            return False

    def valid_merge(self, node1: DataNode, node2: DataNode, suffix1: Set, suffix2: Set):
        if super().valid_merge(node1, node2, suffix1, suffix2):
            if self.eval_state_consistency(node1, node2):
                return True
            else:
                return False
        else:
            return False

    def visualize(self, k, workdir):
        self._visualize(k, workdir=workdir, name="SEKT")
