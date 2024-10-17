import os
import json
import random
import argparse
import time

import subprocess
import threading
from multiprocessing import Pool

import shlex
import random as rand
from typing import Dict
from web3 import Web3  # type: ignore


# This file is used to evaluate if the mined automata can benefit smart contract evolution by generating more effective test cases to detect potential bugs.

# Address bug introduced in smart contract evolution

# Subject: Mytrhil, a state-of-the-art security analysis tool powered by symbolic execution and static analysis
# How do we evaluate?
#  (1) manually insert bugs into DApp smart contracts
#  (2) run native/random Mythril on these buggy contracts and record the number of bugs detected and the test cases used.
#  (3) run automata-guided Mythril by our approach to generating tests for bug detection and recording the number of bugs detected and the test cases used

# Do we need to highlight on-chain or off-chain fuzzing?
# On-chain fuzzing -> contract upgrading
# Off-chain fuzzing -> contract migration

FuncSig = str
Hash = str

TEST_CMD_MYTH_DEFAULT = "myth -v 2 analyze {contract_file}:{contract_name} -t 3 --parallel-solving"

TEST_CMD = 'myth -v 2 analyze {contract_file}:{contract_name} --transaction-sequences "{transactions}" --parallel-solving'


def get_function_selector(function_signature):
    # Encode the function signature using Keccak-256 (SHA-3)
    keccak = Web3.keccak(text=function_signature)
    # Take the first 4 bytes of the hash
    selector = keccak[:4]
    # Convert to hex string for readability
    selector_hex = selector.hex()
    return selector_hex


def run_with_timeout(readable_command, command, timeout):
    """
    Runs a command with a timeout. If the timeout is exceeded, the subprocess is killed.

    Args:
        command (list): The command to run as a list (e.g., ['ping', 'google.com']).
        timeout (int): The timeout in seconds.

    Returns:
        str: The standard output from the command, or a timeout message.
    """

    my_cmd = shlex.split(command.strip())
    start = time.time()

    # Start the subprocess
    process = subprocess.Popen(
        my_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def kill_process():
        process.kill()
        print("Process killed due to timeout!")

    # Start a timer to kill the process if it runs too long
    timer = threading.Timer(timeout, kill_process)
    timer.start()

    try:
        stdout, stderr = process.communicate()
        if timer.is_alive():
            # print(readable_command)
            # print(command)
            result = stdout.decode('utf-8')  # Return the output if successful
            return result
        else:
            return "Process timed out and was killed."
    finally:
        timer.cancel()  # Cancel the timer if the process finishes on time


# We should use coverage-guided test case generation
# need to think about it more

class TestCaseGen():
    def __init__(self, contract_file, contract_name, model_file, abi_file, mbt=False, random=False):
        self.contract_file = contract_file
        self.contract_name = contract_name
        self.model_file = model_file
        if abi_file is not None:
            self.abi_file = abi_file
        else:
            output_dir = "Dapp-Automata-data/RQ2/artifacts"
            cmd = "solc {contract_file} --overwrite --bin --abi -o {output_dir}".format(
                contract_file=contract_file, output_dir=output_dir)
            print(cmd)
            exit_code = os.system(cmd)
            print(exit_code)
            abi_file = os.path.join(output_dir, contract_name+".abi")
            assert os.path.exists(
                abi_file), "abi file not found, which may be caused by compilation failure. Please check it"
            self.abi_file = abi_file
            # print(self.get_abi())
            # print(self.gen_func_hashes())

        self.opt = "mbt" if mbt else "random" if random else "native"

    def get_abi(self):
        return json.load(open(self.abi_file))

    def get_model(self):
        return json.load(open(self.model_file))

    def gen_func_hashes(self):
        result: Dict[FuncSig, Hash] = dict()
        for abi_func in self.get_abi():
            if abi_func["type"] == "function":
                if "stateMutability" in abi_func and abi_func["stateMutability"] not in ["view", "constant", "pure"]:
                    func_sig = "{func_name}({types})".format(func_name=abi_func["name"], types=",".join(
                        [item["type"] for item in abi_func["inputs"]]))
                    func_selector = get_function_selector(func_sig)
                    print(func_sig, func_selector)
                    result[func_sig] = func_selector
        return result

    def mbt_myth(self):
        model = self.get_model()
        transitions = model.get("transitions", None)
        assert transitions is not None
        curState = model.get("initialState")
        valid_results = set()
        trace_limit = 5

        funcs = set()

        def dfs(curState, trace=[]):
            if len(trace) > trace_limit:
                return
            next_transitions = transitions.get(curState, dict())
            for func in next_transitions:
                if func in trace:
                    # loop transitions
                    continue
                next_states = next_transitions[func]
                funcs.add(func)
                valid_results.add(tuple(trace+[func]))
                for next_state in next_states:
                    dfs(next_state, trace+[func])

        dfs(curState=curState)

        def validity_check(seq):
            refined_seq = [item.split(
                "(")[0] for item in seq if item.split("(")[0] in funcs]
            if tuple(refined_seq) in valid_results:
                return True
            else:
                return False

        valid_results = list(valid_results)

        # self.random_myth(validity_func=validity_check)
        all_func_hashes = self.gen_func_hashes()
        func_sigs = list(all_func_hashes.keys())

        other_func_sigs = list(
            filter(lambda x: x.split("(")[0] not in funcs, func_sigs))

        max_seq = 100
        time_out = 60*60

        explored_ids = set()
        start = time.time()

        readable_cmds = []
        real_cmds = []

        def execute_funcs(seq):
            cmd = TEST_CMD.format(contract_file=self.contract_file,
                                  contract_name=self.contract_name, transactions=[
                                      [func_sig] for func_sig in seq])
            print(cmd)
            readable_cmds.append(cmd)
            real_cmd = TEST_CMD.format(contract_file=self.contract_file,
                                       contract_name=self.contract_name, transactions="["+",".join(['['+all_func_hashes[func_sig]+']' for func_sig in seq])+"]")
            real_cmds.append(real_cmd)
            result = run_with_timeout(cmd, real_cmd, timeout=10*60)
            print(result)
            print("overall time used (seconds): " +
                  str(time.time() - start))
            print("\n\n")

        for i in range(len(other_func_sigs)):
            execute_funcs([other_func_sigs[i]])

        for _ in range(max_seq):
            if len(explored_ids) >= len(valid_results):
                break
            if time.time() - start > time_out:
                print("timeout!!! exceed {} seconds".format(time_out))
                break

            select_seq_index = rand.randint(0, len(valid_results)-1)
            # print(select_seq_index, select_seq_index in explored_ids)
            while select_seq_index in explored_ids:
                select_seq_index = rand.randint(0, len(valid_results)-1)

            explored_ids.add(select_seq_index)

            selected_seq = valid_results[select_seq_index]
            seq = []
            for item in selected_seq:
                selected_func_sigs = list(
                    filter(lambda x: x.split("(")[0] == item, func_sigs))
                assert selected_func_sigs is not None and len(
                    selected_func_sigs) > 0, "func signature not found"
                selected_func_sig = selected_func_sigs[rand.randint(
                    0, len(selected_func_sigs)-1)]
                seq.append(selected_func_sig)

            execute_funcs(seq)
            for _ in range(0, 2):
                select_seq_index = rand.randint(0, len(other_func_sigs)-1)
                seq.insert(0, other_func_sigs[select_seq_index])
                execute_funcs(seq)

        # print("test case number:", len(real_cmds))
        # with Pool(2) as pool:
        #     pool.starmap(run_with_timeout, zip(readable_cmds,
        #                                        real_cmds, [10*60]*len(real_cmds)))

        # def test():
        #     print(real_cmd)
        #     my_cmd = shlex.split(real_cmd.strip())
        #     result = run_with_timeout(my_cmd, timeout=10*60)
        #     print(result)
        #     print("overall time used (seconds): " + str(time.time() - start))
        #     print("\n\n")

        return

    def native_myth(self):
        cmd = TEST_CMD_MYTH_DEFAULT.format(contract_file=self.contract_file,
                                           contract_name=self.contract_name,
                                           output_file=os.path.join(os.path.dirname(self.contract_file), os.path.basename(self.contract_file).split(".")[0]+".myth.json"))
        print(cmd)
        # exit_code = os.system(cmd)
        # if exit_code == 0:
        #     pass
        # else:
        #     print("Error or timeout")

    def random_myth(self, validity_func=None):
        all_func_hashes = self.gen_func_hashes()
        func_sigs = list(all_func_hashes.keys())
        seq_limit = 5
        max_seq = 100
        time_out = 60*60

        start = time.time()
        for i in range(max_seq):
            if time.time() - start > time_out:
                print("timeout!!! exceed {} seconds".format(time_out))
                break
            seq_size = rand.randint(1, seq_limit)

            if validity_func is None:
                seq = []
                for _ in range(seq_size):
                    seq.append(
                        func_sigs[int(rand.random()*len(func_sigs))])
            else:
                seq = []
                for _ in range(seq_size):
                    seq.append(
                        func_sigs[int(rand.random()*len(func_sigs))])
                while not validity_func(seq):
                    seq = []
                    for _ in range(seq_size):
                        seq.append(
                            func_sigs[int(rand.random()*len(func_sigs))])

            cmd = TEST_CMD.format(contract_file=self.contract_file,
                                  contract_name=self.contract_name, transactions=[
                                      [func_sig] for func_sig in seq])
            print(cmd)
            real_cmd = TEST_CMD.format(contract_file=self.contract_file,
                                       contract_name=self.contract_name, transactions="["+",".join(['['+all_func_hashes[func_sig]+']' for func_sig in seq])+"]")
            print(real_cmd)
            my_cmd = shlex.split(real_cmd.strip())
            result = run_with_timeout(my_cmd, real_cmd, timeout=2*60)
            print(result)
            print("overall time used (seconds): " + str(time.time() - start))
            print("\n\n")

        return

    def test(self):
        if self.opt == "mbt":
            self.mbt_myth()
        elif self.opt == "random":
            self.random_myth()
        else:
            self.native_myth()


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Test Case Quality Evaluation")
    parser.add_argument("--mbt", action="store_true",
                        help="model guided test case generation")
    parser.add_argument("--random", action="store_true",
                        help="random-based test case generation")
    parser.add_argument("--contract-name", type=str,
                        default=None, help="contract name")
    parser.add_argument("--model-file", type=str,
                        default=None, help="automata json file")
    parser.add_argument("--abi-file", type=str, default=None, help="abi file")
    parser.add_argument("contract_file")
    args = parser.parse_args()
    print(args.__dict__)
    generator = TestCaseGen(**args.__dict__)
    generator.test()
