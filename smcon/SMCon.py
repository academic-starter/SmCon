import logging
from smcon.specAutomata import *
from smcon.utils.graph import Graph, Node
from typing import Union, List
from itertools import repeat

Predicate = Union[str, list]

REMOVE_STATE = 1


class StateNode(Node):
    predicate: Predicate
    visit: bool

    def __init__(self, predicate: Predicate) -> None:
        super().__init__()
        self.predicate = predicate
        self.visit = False

    def __str__(self) -> str:
        return str(self.predicate)


class StateAutomata(Graph):
    printCount = 0
    initialState: StateNode
    statevars: list
    pre_invariants: dict
    post_invariants: dict
    statetraces: list

    def __init__(self, statevars: list, pre_invariants: dict, post_invariants: dict, statetraces: list) -> None:
        self.statevars = statevars
        self.pre_invariants = pre_invariants
        self.post_invariants = post_invariants
        self.statetraces = statetraces
        super().__init__()

        StateAutomata.printCount = 0

    @property
    def states(self) -> List[StateNode]:
        return self.nodes

    def addState(self, predicate: Predicate) -> StateNode:
        state = StateNode(predicate=predicate)
        self.addNode(state)
        return state

    def rmState(self, state: StateNode):
        assert isinstance(state, StateNode)
        self.removeNode(state)

    def setInitialState(self, state: StateNode):
        self.initialState = state
        self.setRoot(state)

    def print(self, output_dir):
        self.visualize(output_dir)
        StateAutomata.printCount += 1

    def visualize(self, workdir):
        assert len(self.states) > 1
        states = set()
        labels = set()
        string_transitions = dict()
        for from_state_id in self.transitions:
            from_state = list(filter(lambda x: x.unique_id ==
                              from_state_id, self.states))[0]
            from_state_index = str(self.states.index(from_state))
            if from_state_index not in string_transitions:
                string_transitions[from_state_index] = dict()

            for label in self.transitions[from_state_id]:
                for to_state_id in self.transitions[from_state_id][label]:
                    to_state = list(
                        filter(lambda x: x.unique_id == to_state_id, self.states))[0]
                    to_state_index = str(self.states.index(to_state))

                    states.add(from_state_index)
                    states.add(to_state_index)

                    _label = str(label)
                    _label = _label.split("@")[0]
                    labels.add(_label)
                    if _label not in string_transitions[from_state_index]:
                        string_transitions[from_state_index][_label] = set()
                    string_transitions[from_state_index][_label].add(
                        to_state_index)

        for from_state_index in string_transitions:
            for label in string_transitions[from_state_index]:
                string_transitions[from_state_index][label] = list(
                    string_transitions[from_state_index][label])

        initialState_index = str(self.states.index(self.initialState))
        nfa = NFA(
            Q=states,
            sigma=labels,
            delta=string_transitions,
            initialState=initialState_index,
            F=set(),
        )

        result = {
            "states": {index: state.predicate for index, state in enumerate(self.states)},
            "transitions": string_transitions,
            "initialState": initialState_index
        }
        nfa.view(f"{workdir}/FSM-{StateAutomata.printCount}")

        logging.warning(f"{workdir}/FSM-{StateAutomata.printCount}.json")
        json.dump(result, open(
            f"{workdir}/FSM-{StateAutomata.printCount}.json", "w"))

    def applyTraces(self):
        logging.warning("apply traces of FSM")
        self.recorded_all_state_traces = []
        visited_transitions = set()
        visited_states = set()

        def applyTrace(cur, trace, statetrace):
            assert cur in self.states
            if len(trace) == 0:
                self.recorded_all_state_traces.append(statetrace)
                for i in range(0, len(statetrace)-2, 2):
                    visited_transitions.add(
                        (statetrace[i], statetrace[i+1], statetrace[i+2]))
                    visited_states.add(statetrace[i])
                    visited_states.add(statetrace[i+2])
                return True

            method, posts = trace[0]

            if cur.unique_id not in self.transitions or method not in self.transitions[cur.unique_id]:
                return False

            for next_state_id in self.transitions[cur.unique_id][method]:
                nextState: StateNode = list(
                    filter(lambda state: state.unique_id == next_state_id, self.states))[0]

                preds = set(posts)
                # preds.add("dummyState != 0")
                for pred in copy.copy(preds):
                    if pred.split(" ")[0].strip() not in self.statevars:
                        preds.remove(pred)
                        trace[0][1].remove(pred)

                if isinstance(nextState.predicate, str):
                    preds.add(nextState.predicate)
                elif isinstance(nextState.predicate, list) or \
                        isinstance(nextState.predicate, set) or \
                        isinstance(nextState.predicate, tuple):
                    preds.update(nextState)
                else:
                    assert False

                if SMT_SAT(fieldorfileds=tuple(self.statevars), preds=frozenset(preds)) and applyTrace(cur=nextState, trace=trace[1:], statetrace=statetrace+[method, next_state_id]):
                    # find a correct path match
                    # FIXME: Maybe there exist multiple path candidates
                    # as all the symbolic states are exclusive and only one path candidate exists
                    return True
            return False

        for trace in self.statetraces:
            cur: StateNode = self.initialState
            applyTrace(cur=cur, trace=trace, statetrace=[cur.unique_id])

        return visited_transitions, visited_states

    def metatransition_construct(self):
        toProcess = list()
        processed = list()
        toProcess.append(self.initialState)
        self.transitions = dict()
        while len(toProcess) > 0:
            cur: StateNode = toProcess.pop()
            processed.append(cur)
            for method in self.pre_invariants:
                pre_conditions = self.pre_invariants[method]
                assert isinstance(pre_conditions, list) or \
                    isinstance(pre_conditions, set) or \
                    isinstance(pre_conditions, tuple)

                pres = set(pre_conditions)
                pres.add(cur.predicate)

                if SMT_SAT(fieldorfileds=tuple(self.statevars), preds=frozenset(pres)):
                    with Pool() as p:
                        sat_results = p.starmap(parrellel_checking,
                                                zip(repeat(method),
                                                    repeat(
                                                    self.post_invariants),
                                                    repeat(self.statevars),
                                                    [state.predicate for state in self.states]
                                                    ))
                        for i in range(len(sat_results)):
                            if sat_results[i] == True:
                                nextState = self.states[i]
                                if nextState not in processed and nextState not in toProcess:
                                    toProcess.append(nextState)
                                self.addTransition(cur, method, nextState)

    def generate(self, output_dir):
        self.metatransition_construct()
        # self.print(output_dir=output_dir)
        visited_transitions, visited_states = self.applyTraces()

        # remove unvisited transitions from the automata
        unvisited_transitions = set()
        for from_state_id in self.transitions:
            for label in self.transitions[from_state_id]:
                for to_state_id in self.transitions[from_state_id][label]:
                    if (from_state_id, label, to_state_id) not in visited_transitions:
                        unvisited_transitions.add(
                            (from_state_id, label, to_state_id))

        for transition in unvisited_transitions:
            from_state_id, label, to_state_id = transition[0], transition[1], transition[2]
            self.removeTransition(from_index=from_state_id,
                                  label=label, to_index=to_state_id)

        unvisited_states = list(
            filter(lambda state: state.unique_id not in visited_states, self.states))
        logging.warning("unvisited transition {}".format(
            unvisited_transitions))
        logging.warning("unvisited states {}".format(
            [state.predicate for state in unvisited_states]))
        for state in unvisited_states:
            self.rmState(state)
            self.transitions.pop(state.unique_id, None)
        self.print(output_dir=output_dir)
        return self

    def checkSpuriousPath(self):
        new_recorded_all_state_traces = sorted(
            self.recorded_all_state_traces, key=lambda x: len(x), reverse=True)
        for state_trace in new_recorded_all_state_traces:
            for i in range(len(state_trace)-1, 1, -2):
                q_n = state_trace[i]
                assert any(map(lambda x: x.unique_id == q_n, self.states)
                           ), "invalid state trace containing unknown states"
                if q_n not in self.transitions:
                    continue
                t_n_1_s = list(self.transitions[q_n].keys())
                for t_n_1 in t_n_1_s:
                    for item in self.transitions[q_n][t_n_1]:
                        q_n_1 = item
                        pi_n_1 = state_trace[:i+1] + [t_n_1, q_n_1]

                        # check if there is a self loop
                        if q_n_1 == q_n:
                            loop = [q_n, t_n_1, q_n, t_n_1, q_n]
                            selfloop = False
                            for _state_trace in new_recorded_all_state_traces:
                                if "".join(map(str, _state_trace)).count("".join(map(str, loop))) != 0:
                                    selfloop = True
                                    break
                            if not selfloop:
                                yield pi_n_1
                            else:
                                continue
                        else:
                            # check if there is a cycle loop
                            if "".join(map(str, pi_n_1)).count("".join(map(str, [q_n, t_n_1, q_n_1]))) >= 2:
                                cycleloop = False
                                for _state_trace in new_recorded_all_state_traces:
                                    if "".join(map(str, _state_trace)).count("".join(map(str, [q_n, t_n_1, q_n_1]))) >= 2:
                                        cycleloop = True
                                        break
                                if not cycleloop:
                                    yield pi_n_1
                                else:
                                    continue
                            else:
                                # check if there is a s->q_n*t_n_1*q_n_1, namely pi_n_1 in the recorded traces
                                appear = False
                                for _state_trace in new_recorded_all_state_traces:
                                    if len(_state_trace) >= len(pi_n_1) and _state_trace[:len(pi_n_1)] == pi_n_1:
                                        appear = True
                                        break

                                if not appear:
                                    yield pi_n_1
                                else:
                                    continue

    def splitAndRemove(self, pi_n_1):

        # logging.warning(f"split and remove")
        remove_kind = -1

        pre_method = pi_n_1[-4]

        cur_method = pi_n_1[-2]
        q_n_state: StateNode = list(
            filter(lambda x: x.unique_id == pi_n_1[-3], self.states))[0]
        assert isinstance(q_n_state, StateNode)
        q_n = q_n_state.predicate

        prev_m_pre_invs = self.pre_invariants[pre_method]
        prev_post_invs = self.post_invariants[pre_method]

        cur_m_pre_invs = self.pre_invariants[cur_method]
        cur_m_post_invs = self.post_invariants[cur_method]

        g_cur_m = translate2Z3exprFromPredSet(cur_m_pre_invs)
        u_cur_m = translate2Z3exprFromPredSet(cur_m_post_invs)

        u_prev_m = translate2Z3exprFromPredSet(prev_post_invs)

        hat_q_1 = f"And({q_n}, {u_prev_m})"
        hat_q_2 = f"And({q_n}, Not({u_prev_m}))"

        if SMT_SAT(fieldorfileds=tuple(self.statevars), preds=hat_q_1) and SMT_SAT(fieldorfileds=tuple(self.statevars), preds=hat_q_2):
            logging.warning("split state into two states (1)")

            self.rmState(q_n_state)
            self.addState(hat_q_1)
            self.addState(hat_q_2)

            remove_kind = REMOVE_STATE
            return remove_kind
        else:
            # pick any pi_n
            for state_trace in self.recorded_all_state_traces:
                for i in range(0, len(state_trace)-1, 2):
                    if state_trace[i] == q_n and state_trace[i+1] == cur_method:
                        assert i > 1
                        method = state_trace[i-1]

                        m_post_invs = self.post_invariants[method]

                        m_post = translate2Z3exprFromPredSet(m_post_invs)

                        OnePred = f"And({q_n}, And({m_post}, And({g_cur_m}, Not({u_cur_m}))))"
                        OtherPred1 = f"And({q_n}, Not(And({m_post}, And({g_cur_m}, Not({u_cur_m})))))"

                        candidates = [OnePred, OtherPred1]

                        feasible_candidates = []
                        for candidate in candidates:
                            if SMT_SAT(fieldorfileds=tuple(self.statevars), preds=candidate):
                                feasible_candidates.append(candidate)

                        if len(feasible_candidates) < 2:
                            continue

                        self.rmState(q_n_state)

                        for candidate in feasible_candidates:
                            self.addState(candidate)

                        remove_kind = REMOVE_STATE
                        break
                if remove_kind == REMOVE_STATE:
                    break

            if remove_kind == REMOVE_STATE:
                logging.warning("split state into two states (2)")
                return remove_kind
            else:
                # when there is no pi_n, we need to remove a pi_n_1 using the adjective transitions
                # FIXME: guarantee the termination of this algorithm
                assert len(pi_n_1) > 4

                # g_cur_m may be two generalized
                # pre-state must be different from post-state if available
                OnePred = f"And({q_n}, {g_cur_m})"
                OtherPred = f"And({q_n}, Not({g_cur_m}))"

                candidates = [OnePred, OtherPred]

                feasible_candidates = []
                for candidate in candidates:
                    if SMT_SAT(fieldorfileds=tuple(self.statevars), preds=candidate):
                        feasible_candidates.append(candidate)

                if len(feasible_candidates) == 2:
                    logging.warning("split state into two states (3)")
                    self.rmState(q_n_state)
                    self.addState(OnePred)
                    self.addState(OtherPred)
                    remove_kind = REMOVE_STATE
                else:
                    # logging.warning("failed splitting about the trace:")
                    # logging.warning(" ".join([pi_n_1[i] for i in range(1, len(pi_n_1)-1, 2)]))
                    pass

                return remove_kind

    def mergeLeafStates(self):
        leafStates = set()
        for state in self.states:
            if state.unique_id not in self.transitions or len(self.transitions[state.unique_id]) == 0:
                leafStates.add(state)
        if len(leafStates) == 0 or len(leafStates) == 1:
            return None

        new_EndingState = "False"
        for state in leafStates:
            assert state != self.initialState
            new_EndingState = f"Or({new_EndingState}, {state.predicate})"
            self.rmState(state)

        self.addState(new_EndingState)
        return new_EndingState


class SMCon:
    initialState: Predicate
    statevars: list
    pre_invariants: dict
    post_invariants: dict
    statetraces: list

    def __init__(self, workdir, initialState: Predicate, statevars, pre_invariants, post_invariants, statetraces) -> None:
        self.workdir = workdir
        # initialState is a predicate
        self.initialState = initialState
        self.statevars = statevars
        self.pre_invariants = pre_invariants
        self.post_invariants = post_invariants
        self.statetraces = statetraces

    def Init(self) -> StateAutomata:
        fsm = StateAutomata(self.statevars, self.pre_invariants,
                            self.post_invariants, self.statetraces)

        state = fsm.addState(self.initialState)
        fsm.setInitialState(state)

        otherState = f"Not({self.initialState})"
        fsm.addState(otherState)

        return fsm

    def Construct(self, fsm: StateAutomata):
        # fsm.setInitialState(self.initialState)
        fsm.generate(self.workdir)
        return fsm

    def RmPath(self, fsm: StateAutomata):
        for pi_n_1 in fsm.checkSpuriousPath():
            removeKind = fsm.splitAndRemove(pi_n_1)
            if removeKind == REMOVE_STATE:
                return False, fsm

        return True, fsm

    def fair_shedule(self):
        cap_count = 20

        fsm = self.Init()
        fsm = self.Construct(fsm)
        old_states_size = len(fsm.states)
        stable, fsm = self.RmPath(fsm)

        logging.warning(str(old_states_size) + "->" + str(len(fsm.states)))

        while not stable and cap_count > 0:
            fsm = self.Construct(fsm)
            old_states_size = len(fsm.states)
            stable, fsm = self.RmPath(fsm)
            cap_count -= 1
            logging.warning(str(old_states_size) + "->" + str(len(fsm.states)))

        if not stable:
            logging.warning("Still spurious path found")
            self.Construct(fsm)
        else:
            logging.warning("No spurious path found")

        if fsm.mergeLeafStates() is not None:
            self.Construct(fsm)

        return fsm

    def smcon(self):
        fsm = self.fair_shedule()
        return fsm
