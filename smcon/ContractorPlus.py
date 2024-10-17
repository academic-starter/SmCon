from typing import Dict, Set, List
from smcon.utils.graph import Graph, Node
from smcon.specAutomata import SMT_ImplyTwoPredicateSets, SMT_SAT, translate2Z3exprFromPredSet


class ContractorPlus(Graph):
    def __init__(self, variables: List[str], pre_invaraints: Dict[str, Set], post_invariants: Dict[str, Set]) -> None:
        super().__init__()
        self.variables = tuple(variables)
        self.pre_invaraints = pre_invaraints
        self.post_invariants = post_invariants
        self.A = list(self.pre_invaraints.keys())

        init = list()
        for field in self.variables:
            init.append(f"{field} == 0")
        init = translate2Z3exprFromPredSet(init)
        self.init = init

    def get_symbolic_state(self, actions: Set):
        predicate = "True"
        for action in actions:
            if action.startswith("not"):
                # continue
                action = action.split("not")[1].strip()
                inv = translate2Z3exprFromPredSet(self.pre_invaraints[action])
                predicate = "And({}, Not({}))".format(predicate, inv)
            else:
                inv = translate2Z3exprFromPredSet(self.pre_invaraints[action])
                predicate = "And({}, {})".format(predicate, inv)
        return predicate

    def get_S_0(self, S):
        S_0: Set = set()
        for actions in S:
            predicate = self.get_symbolic_state(actions)
            init_check_pred = "And({}, {})".format(self.init, predicate)
            if SMT_SAT(self.variables, init_check_pred):
                S_0.add(actions)
        return S_0

    def inv_consistency(self, actions: Set):
        predicate = self.get_symbolic_state(actions)
        if SMT_SAT(self.variables, predicate):
            return True
        else:
            return False

    def enableness_construction(self):
        D_plus_plus: Set = set()
        D_plus_minus: Set = set()
        D_minus_plus: Set = set()
        D_minus_minus: Set = set()
        for a in self.A:
            for b in self.A:
                if a == b:
                    continue
                Pa = translate2Z3exprFromPredSet(self.pre_invaraints[a])
                Pb = translate2Z3exprFromPredSet(self.pre_invaraints[b])
                if SMT_ImplyTwoPredicateSets(self.variables, tuple([Pa]), tuple([Pb])):
                    D_plus_plus.add((a, b))
                elif SMT_ImplyTwoPredicateSets(self.variables, tuple([Pa]), tuple([f"Not({Pb})"])):
                    D_plus_minus.add((a, b))
                elif SMT_ImplyTwoPredicateSets(self.variables, tuple([f"Not({Pa})"]), tuple([Pb])):
                    D_minus_plus.add((a, b))
                elif SMT_ImplyTwoPredicateSets(self.variables, tuple([f"Not({Pa})"]), tuple([f"Not({Pb})"])):
                    D_minus_minus.add((a, b))
                else:
                    pass
        self.D_plus_plus, self.D_plus_minus, self.D_minus_plus, self.D_minus_minus = D_plus_plus, D_plus_minus, D_minus_plus, D_minus_minus
        return D_plus_plus, D_plus_minus, D_minus_plus, D_minus_minus

    def enumerate(self, current: Set, i: int):
        n = len(self.A)

        if i > n:
            if self.inv_consistency(current):
                return frozenset([frozenset(current)])
            else:
                return frozenset()
        else:
            a_i = self.A[i-1]
            not_a_i = f"not {a_i}"
            if a_i not in current and not_a_i not in current:
                c_1 = current.union(set([a_i]))

                for item in self.D_plus_plus:
                    a, b = item
                    if a == a_i:
                        c_1.add(b)

                for item in self.D_plus_minus:
                    a, b = item
                    if a == a_i:
                        c_1.add(f"not {b}")

                c_2 = current.union(set([f"not {a_i}"]))
                for item in self.D_minus_plus:
                    a, b = item
                    if a == a_i:
                        c_2.add(b)

                for item in self.D_minus_minus:
                    a, b = item
                    if a == a_i:
                        c_2.add(f"not {b}")

                return self.enumerate(c_1, i+1).union(self.enumerate(c_2, i+1))
            else:
                return self.enumerate(current, i+1)

    def contractor(self):
        self.enableness_construction()
        S = self.enumerate(current=set(), i=1)

        node_mapping: Dict[frozenset, Node] = dict()
        for s in S:
            node_mapping[s] = Node()
            self.addNode(node_mapping[s])

        S_0 = list(self.get_S_0(S))
        assert len(S_0) == 1, "mutiple starting states are not permitted"

        rootNode = node_mapping[S_0[0]]
        self.setRoot(rootNode)

        for s_left in S:
            for s_right in S:
                for a in s_left:
                    if a.startswith("not"):
                        continue
                    # inv_s_left = self.get_symbolic_state(s_left)
                    inv_s_left = "True"
                    inv_s_right = self.get_symbolic_state(s_right)
                    q_a = translate2Z3exprFromPredSet(self.post_invariants[a])
                    vc = "And({}, And({}, {}))".format(
                        inv_s_left, q_a, inv_s_right)
                    if SMT_SAT(self.variables, vc):
                        self.addTransition(
                            node_mapping[s_left], a, node_mapping[s_right])
