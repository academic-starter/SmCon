from typing import Any, Dict, List 
import logging
from slither import Slither
from slither.core.solidity_types.mapping_type import MappingType
from slither.core.solidity_types.array_type import ArrayType 
from slither.core.solidity_types.user_defined_type import UserDefinedType
from slither.core.declarations.structure import Structure
from slither.core.declarations.enum_contract import EnumContract
from slither.core.declarations.structure_contract import StructureContract
from slither.core.declarations.contract import Contract
from slither.core.variables.structure_variable import StructureVariable
import re, math  

def fetchAbi(slither: Slither, contractName: str):
        result: List = None 
        for cid in slither.crytic_compile.compilation_units:
            complilation_unit = slither.crytic_compile.compilation_units[cid]
            for filename in complilation_unit.filenames:
                result =  complilation_unit.source_unit(filename).abi(contractName)
                if result is not None:
                    return result  
        return result 

dynamicArrayRegex = re.compile(r"(\w+)\[\]")
fixedArrayRegex = re.compile(r"(\w+)\[([0-9]+)\]")
def compute_type_info(vartype, _type_info, contract):
    type_ = str(vartype)
    if type_ == "bool":
        _type_info[contract.name][type_]  = dict(encoding="inplace", label="bool", numberOfBytes =str(vartype.storage_size[0])) 
    elif type_ == "uint256":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="uint256", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "uint128":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="uint128", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "uint96":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="uint96", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "uint64":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="uint64", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "uint32":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="uint32", numberOfBytes =str(vartype.storage_size[0]))
    elif type_ == "uint16":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="uint16", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "uint8":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="uint8", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "int256":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="int256", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "int128":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="int128", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "int64":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="int64", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "int32":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="int32", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "int16":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="int16", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "int8":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="int8", numberOfBytes =str(vartype.storage_size[0]))
    elif type_ == "address":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="address", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "bytes":
        _type_info[contract.name][type_]  =  dict(encoding="bytes", label="bytes", numberOfBytes = str(vartype.storage_size[0]))
    elif type_ == "string":
        _type_info[contract.name][type_]  =  dict(encoding="bytes", label="string", numberOfBytes = str(vartype.storage_size[0]))
    elif re.compile("^^bytes([0-9]+)$").match(str(type_)):
         _type_info[contract.name][type_]  =  dict(encoding="inplace", label=type_, numberOfBytes = re.compile("^^bytes([0-9]+)$").match(str(type_)).groups()[0])
    elif type_ == "enum":
        _type_info[contract.name][type_]  =  dict(encoding="inplace", label="enum", numberOfBytes = str(vartype.storage_size[0]))
    elif isinstance(vartype, ArrayType):
        arraytype: ArrayType = vartype
        # print(arraytype, arraytype.length, arraytype.type, type_)
        # pprint(arraytype)
        if hasattr(arraytype, "is_fixed_array") and (arraytype.length is not None):
            base = arraytype.type 
            size = arraytype.length
            # print(size)
            m =  re.compile("^^bytes([0-9]+)\[([0-9]+)\]$").match(str(arraytype))
            if m:
                # print(m.groups())
                size = int(m.groups()[1])* int(m.groups()[0])  
                # print(arraytype, size)
            m =  re.compile("^^uint([0-9]+)\[([0-9]+)\]$").match(str(arraytype))
            if m:
                # print(m.groups())
                size = int(int(m.groups()[1])/8) * int(m.groups()[0])   
                # print(arraytype, size)
            m =  re.compile("^^int([0-9]+)\[([0-9]+)\]$").match(str(arraytype))
            if m:
                # print(m.groups())
                size = int(int(m.groups()[1])/8) * int(m.groups()[0])   
                # print(arraytype, size)
            compute_type_info(base, _type_info, contract)
            _type_info[contract.name][type_]  =  dict(base = str(base), encoding= "inplace", label=type_, numberOfBytes=str(size))
        else:
            assert hasattr(arraytype, "is_dynamic_array") or arraytype.length is None , "must be dynamic array"
            # m = dynamicArrayRegex.match(type_)
            # base = m.groups()[0]
            base = arraytype.type 
            compute_type_info(base, _type_info, contract)
            _type_info[contract.name][type_]  =  dict(base = str(base), encoding= "dynamic_array", label=type_, numberOfBytes=str(vartype.storage_size[0]))
    elif isinstance(vartype, MappingType):
        type_from = vartype.type_from
        type_to = vartype.type_to
        _type_info[contract.name][type_] =  dict(encoding="mapping", key=str(type_from), label=type_, numberOfBytes="32", value=str(type_to))
        compute_type_info(type_from, _type_info, contract)
        compute_type_info(type_to, _type_info, contract)
    elif isinstance(vartype, UserDefinedType): 
            # print("UserDefinedType:", vartype, type(vartype.type))
            # and isinstance(var.type.type, EnumContract):
            if isinstance(vartype.type, EnumContract):
                _type_info[contract.name][type_] =  dict(encoding="inplace", label="enum_"+type_, numberOfBytes=str(vartype.storage_size[0]))  
            elif isinstance(vartype.type, StructureContract):
                structure = vartype.type
                name = structure.name 
                # print(name)
                elems = structure.elems_ordered
                members = []
                _index = 0
                _slot = 0
                _offset = 0
                totalsize = 0
                for elem in elems:
                    _astid = _index
                    _size, _new_slot = elem.type.storage_size 
                    m =  re.compile("^^bytes([0-9]+)").match(str(elem.type))
                    if m:
                        # print(m.groups())
                        _size = int(m.groups()[0])    
                        # print(elem.type, _size, _new_slot)
                    totalsize += _size
                    if _new_slot:
                        if _offset > 0:
                            _slot += 1
                            _offset = 0
                    elif _size + _offset > 32:
                            _slot += 1
                            _offset = 0
                            
                    _type_ = str(elem.type)

                    members.append(dict(
                                astId = _astid,
                                contract = contract.name,
                                label = elem.name,
                                offset = _offset,
                                slot = _slot,
                                type = _type_))
                    if _type_ not in _type_info:
                        compute_type_info(elem.type, _type_info, contract)
                    else:
                        pass 
                    if _new_slot:
                        _slot += math.ceil(_size / 32)
                    else:
                        _offset += _size
                    _index += 1
                _type_info[contract.name][type_] = dict(encoding = "inplace", label=str(vartype), members=members,numberOfBytes = totalsize)
            elif isinstance(vartype.type, Contract):
                _type_info[contract.name][type_] =  dict(encoding="inplace", label="address", numberOfBytes=str(20))  
            else:
                logging.error(type_ + " is currently not supported")
                raise Exception(type_ + " is currently not supported")        
    else:
        raise Exception(type_ + " is currently not supported") 

def compute_storage_layout(self):
        if not hasattr(self, "_type_info") or self._type_info is None:
            self._type_info = dict()
            self._storage = dict() 
        for contract in self.contracts:
            if contract.name not in self._type_info:
                self._type_info[contract.name] = dict()
            if contract.name not in self._storage:
                self._storage[contract.name] = []
            slot = 0
            offset = 0
            index = 0
            for var in contract.state_variables_ordered:
                # print(var, var.type,var.is_constant or (hasattr(var, "is_immutable") and  var.is_immutable))
                if var.is_constant or (hasattr(var, "is_immutable") and  var.is_immutable):
                    continue    
                astnode_id = index
                size, new_slot = var.type.storage_size
                m =  re.compile("^^bytes([0-9]+)$").match(str(var.type))
                if m:
                    # print(m.groups())
                    size = int(m.groups()[0])    
                    # print(var.type, size, new_slot)
                m =  re.compile("^^bytes([0-9]+)\[([0-9]+)\]$").match(str(var.type))
                if m:
                    # print(m.groups())
                    size = 32 * math.ceil(int(m.groups()[1])  / math.floor(32/int(m.groups()[0])))  
                    # print(var.type, size, new_slot)
                # print(size, new_slot)
                if new_slot:
                    if offset > 0:
                        slot += 1
                        offset = 0
                elif size + offset > 32:
                    slot += 1
                    offset = 0
                type_ = str(var.type)
                self._storage[contract.name].append(dict(
                    astId = astnode_id,
                    contract = contract.name,
                    label =  var.name,
                    # label = var.contract.name+"_own_" + var.name if var.contract.name != contract.name else var.name,
                    offset = offset,
                    slot = str(slot),
                    type = type_
                ))
                compute_type_info(var.type, self._type_info, contract)
                if new_slot:
                    slot += math.ceil(size / 32)
                else:
                    offset += size
                index += 1

# @description, the main algorithm to produce storage layout of a smart contract
def computeStorageLayout(slither: Slither, contractName: str):
    result: Dict = None 
    compilation_units = slither.compilation_units
    for compilation_unit in compilation_units:
        compute_storage_layout(compilation_unit)
        if contractName in compilation_unit._storage:
            result =  dict(storage = compilation_unit._storage[contractName], types = compilation_unit._type_info[contractName])
            break
    return result

