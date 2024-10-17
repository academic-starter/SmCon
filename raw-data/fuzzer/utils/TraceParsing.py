import json
import logging
import os 
import sys
sys.setrecursionlimit(2000)

from typing import List,Dict,Iterator, Optional
from Crypto.Hash import keccak
from evm_trace import TraceFrame, create_trace_frames
from evm_trace.geth import TraceMemory   
from eth_pydantic_types import HashBytes20, HexBytes     

from evm_trace.enums import CALL_OPCODES

def keccak256(buffer: bytes) -> bytes:
    """
    Computes the keccak256 hash of the input `buffer`.

    Parameters
    ----------
    buffer :
        Input for the hashing function.

    Returns
    -------
    hash : `ethereum.base_types.Hash32`
        Output of the hash function.
    """
    k = keccak.new(digest_bits=256)
    return bytes(k.update(buffer).digest())

class Instruction:
    def __init__(self, frame: TraceFrame) -> None:
        self.frame = frame
        self.children: list["Instruction"] = []
    @property
    def op(self) -> str:
        return self.frame.op
    @property
    def stack(self) -> List[HexBytes]:
        return self.frame.stack
    @property
    def depth(self) -> int:
        return self.frame.depth
    @property
    def pc(self) -> int:
        return self.frame.pc
    @property
    def memory(self) -> TraceMemory:
        return self.frame.memory
    @property
    def storage(self) -> Dict[HexBytes, HexBytes]:
        return self.frame.storage
    
    @property
    def address(self) -> Optional[HashBytes20]:
        return self.frame.address
    
    @property
    def index_values(self):
        if self.op in  ["KECCAK256", "SHA3"]:
            return [] 
        elif self.op in ["SSTORE"]:
            return [] 
        elif self.op in ["MSTORE"]:
            value = self.stack[-2].hex()
            return [value] 
        elif self.op in ["ADD"]:
            return []
        else:
            return []

    def dependend(self, ins: "Instruction") -> bool:
        if self.op in  ["KECCAK256", "SHA3"]:
            memory_start_index = int(self.stack[-1].hex(), 16)
            size = int(self.stack[-2].hex(), 16)
            if ins.op in ["MSTORE", "MSTORE8"]:
                mstore_memory_start_index = int(ins.stack[-1].hex(), 16)
                value = int(ins.stack[-2].hex(), 16)
                if ins.op == "MSTORE":
                    word_size = 32 
                    if memory_start_index  <= mstore_memory_start_index and mstore_memory_start_index + word_size <= memory_start_index+size:
                        if value == int(self.memory.get(mstore_memory_start_index, word_size).hex(), 16):
                            return True
                        else:
                            return False
                else:
                    word_size = 8 
                    if memory_start_index  <= mstore_memory_start_index and mstore_memory_start_index + word_size <= memory_start_index+size:
                        if value == int(self.memory.get(mstore_memory_start_index, word_size).hex(), 16):
                            return True
                        else:
                            return False
              
        elif self.op in ["SSTORE"]:
            key =  int(self.stack[-1].hex(), 16)
            value = int(self.stack[-2].hex(), 16)
            if ins.op in ["KECCAK256", "SHA3"]:
                memory_start_index = int(ins.stack[-1].hex(), 16)
                size = int(ins.stack[-2].hex(), 16)
                data = ins.memory.get(memory_start_index, size)
                slot = int(keccak256(bytes.fromhex(data.hex()[2:])).hex(), 16)
                if slot == key:
                    return True
                else:
                    return False
            elif ins.op in ["ADD"]:
                x = int(ins.stack[-1].hex(), 16)
                y = int(ins.stack[-2].hex(), 16)
                if x + y == key:
                    return True
                else:
                    return False
            elif ins.op in ["SLOAD"]:
                x = int(ins.stack[-1].hex(), 16)
                if x == key:
                    return True 
                else:
                    return False
        elif self.op in ["MSTORE"]:
            value = int(self.stack[-2].hex(), 16)
            if ins.op in ["ADD"]:
                x = int(ins.stack[-1].hex(), 16)
                y = int(ins.stack[-2].hex(), 16)
                if x + y  == value:
                    return True
                else:
                    return False
            elif ins.op in  ["KECCAK256", "SHA3"]:
                memory_start_index = int(ins.stack[-1].hex(), 16)
                size = int(ins.stack[-2].hex(), 16)
                data = ins.memory.get(memory_start_index, size)
                _hash = int(keccak256(bytes.fromhex(data.hex()[2:])).hex(), 16)
                if _hash == value:
                    return True
                else:
                    return False
        elif self.op in ["ADD"]:
            x = int(self.stack[-1].hex(), 16)
            y = int(self.stack[-2].hex(), 16)
            if ins.op in  ["KECCAK256", "SHA3"]:
                memory_start_index = int(ins.stack[-1].hex(), 16)
                size = int(ins.stack[-2].hex(), 16)
                data = ins.memory.get(memory_start_index, size)
                _hash = int(keccak256(bytes.fromhex(data.hex()[2:])).hex(), 16)
                if _hash == x or _hash == y:
                    return True
                else:
                    return False
        
        return False
    
    def __str__(self) -> str:
        return f"{self.op} {self.stack} {self.depth} {self.pc} {self.memory} {self.storage}"
    
    def __json__(self) -> dict:
        if self.op in  ["KECCAK256", "SHA3"]:
            memory_start_index = int(self.stack[-1].hex(), 16)
            size = int(self.stack[-2].hex(), 16)
            data = self.memory.get(memory_start_index, size)
            _hash = int(keccak256(bytes.fromhex(data.hex()[2:])).hex(), 16)
            return {
                "op": self.op,
                "pc": self.pc,
                "data": data.hex(),
                "hash": hex(_hash),
                "children": [child.__json__() for child in self.children]
            }
        elif self.op in ["SSTORE"]:
            key =  int(self.stack[-1].hex(), 16)
            value = self.stack[-2].hex()
            return {
                "op": self.op,
                "pc": self.pc,
                "key": hex(key),
                "value": value,
                "children": [child.__json__() for child in self.children]
            }
        elif self.op in ["SLOAD"]:
            key =  self.stack[-1].hex()
            value = self.storage.get(self.stack[-1]).hex()
            return {
                "op": self.op,
                "pc": self.pc,
                "key": key,
                "value": value,
                "children": [child.__json__() for child in self.children]
            }
        elif self.op in ["MSTORE"]:
            value = self.stack[-2].hex()
            return {
                "op": self.op,
                "pc": self.pc,
                "value": value,
                "children": [child.__json__() for child in self.children]
            }
        elif self.op in ["MSTORE8"]:
            value = self.stack[-2].hex()
            return {
                "op": self.op,
                "pc": self.pc,
                "value": value,
                "children": [child.__json__() for child in self.children]
            }
        elif self.op in ["ADD"]:
            x = int(self.stack[-1].hex(), 16)
            y = int(self.stack[-2].hex(), 16)
            return {
                "op": self.op,
                "pc": self.pc,
                "x": hex(x),
                "y": hex(y),
                "children": [child.__json__() for child in self.children]
            }
        else:
            return {
                "op": self.op,
                # "stack": self.stack,
                # "depth": self.depth,
                "pc": self.pc,
                # "memory": self.memory,
                # "storage": self.storage,
                "children": [child.__json__() for child in self.children]
            }

class DependencyGraph:
    def __init__(self, ins: Instruction) -> None:
        self.root =  ins
        self.visited = list()
    
    def add_child(self, ins: "Instruction") -> None:
        self._add_child(self.root, ins)
        self.visited =  list()
    
    def _add_child(self, ins_bottom: "Instruction", ins_dependent: "Instruction") -> None:
        if ins_bottom in self.visited:
            return 
        self.visited.append(ins_bottom)
        if ins_bottom.dependend(ins_dependent):
            ins_bottom.children.append(ins_dependent)
        else:
            for child in ins_bottom.children:
                self._add_child(child, ins_dependent)
    
    def visitGetIndexValues(self):
        index_values = []
        self._visitGetIndexValues(self.root, index_values)
        return index_values
    
    def _visitGetIndexValues(self, ins: Instruction, index_values: list = []):
        index_values.extend(ins.index_values)
        for child in ins.children:
            self._visitGetIndexValues(child, index_values)

    def __str__(self) -> str:
        return str(self.root)
    
    def __json__(self) -> dict:
        return self.root.__json__()
    

class Simulator:
    graphs: List[DependencyGraph]
    data: object
    address: HashBytes20 
    def __init__(self, workdir, contract_name, address, tx_hash) -> None:
        assert os.path.exists(os.path.join(workdir, contract_name, address, tx_hash+".json"))
        self.data = json.load(open(os.path.join(workdir, contract_name, address, tx_hash+".json")))
        self.graphs = []
        self.address = bytes.fromhex(address[2:])

    def loadAndexec(self):
        trace_frames: Iterator[TraceFrame] = create_trace_frames(self.data["result"]["structLogs"])
        self.graphs = list()
        interested_frames = list()
        callee_address_stack = []
        callee_address_stack.append(self.address)
        for frame in trace_frames:
            if frame.op in ["KECCAK256", "SHA3", "SSTORE", "MSTORE", "ADD", "SLOAD"] + list(CALL_OPCODES) + ["RETURN"]:
                if frame.op in ["CALL", "CREATE", "CREATE2"]:
                    callee_address_stack.append(frame.address) 
                current_callee_address = callee_address_stack[-1]
                frame.contract_address = current_callee_address
                interested_frames.append(frame)
                if frame.op in ["RETURN", "REVERT", "STOP"]:
                    if len(callee_address_stack) > 0:
                        callee_address_stack.pop()
        for frame in reversed(interested_frames):
            if frame.op == "SSTORE":
                graph = DependencyGraph(Instruction(frame))
                self.graphs.append(graph)
            for graph in self.graphs:
                graph.add_child(Instruction(frame))
    
    def query(self, slot):
        result = []
        for graph in self.graphs:
            slot = slot if isinstance(slot, str) and slot.startswith("0x") else hex(slot)
            if int(graph.root.stack[-1].hex(), 16) == int(slot, 16):
                result = graph.visitGetIndexValues()
                break
        if len(result) == 0:
            logging.debug("query storage slot {0} with result {1}".format(slot, set(result)))
        else:
            logging.debug("query storage slot {0} with result {1}".format(slot, set(result)))
        return set(result)

    def get_state_diff(self):
        stateDiff: Dict[str, str] = dict() 
        for graph in self.graphs:
            # sstore slot value
            current_address = "0x" + graph.root.address.hex()

            if current_address not in stateDiff:
                stateDiff[current_address] = dict()

            _stateDiff = stateDiff[current_address]

            slot, value = graph.root.stack[-1].hex(), graph.root.stack[-2].hex()
            if slot in _stateDiff:
                continue 
            # find the earliest sload 
            old_value = None 
            for child in graph.root.children:
                if child.op == "SLOAD":
                    old_value = child.storage.get(graph.root.stack[-1]).hex()
            if old_value is not None:
                _stateDiff[slot] = (old_value, value)
            else:
                _stateDiff[slot] = (None, value)
        # print(json.dumps(stateDiff))
        return stateDiff
    
    def print_storage_value(self):
        
        print("--------------------------------------------------")
        print("Storage\t\tValue")
        for graph in self.graphs:
            print(graph.root.stack[-1].hex(), graph.root.stack[-2].hex())
            # if hex(graph.root.stack[-1]) == slot:
            if True:
                print(json.dumps(graph.__json__(), indent=4))
                # print("--------------------------------------------------")
                # print(set(graph.visitGetIndexValues()))
                print("--------------------------------------------------")
        print("--------------------------------------------------")

   