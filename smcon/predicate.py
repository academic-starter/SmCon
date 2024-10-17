from typing import NewType, Union, List
from typing_extensions import Self

LOGIC_OP=NewType("logic_connector", str)
Predicate=NewType("predicate", str)
NOT="NOT"
AND="AND"
OR="OR"
class BasicPredicate:
    predicate: Predicate
    logicOp: LOGIC_OP
    def __init__(self, predicate: Predicate, logicOp: LOGIC_OP=None) -> None:
        self.predicate = predicate
        self.logicOp = logicOp
    
    def __str__(self) -> str:
        return self.predicate


class BinaryPredicate(BasicPredicate):
    predicates: List[BasicPredicate]
    logicOp: LOGIC_OP

    def __init__(self, predicates: List[BasicPredicate], logicOp: LOGIC_OP=AND) -> None:
        assert len(predicates) == 2, "binary predicate must have only two basic predicates"
        self.predicates = predicates
        self.logicOp = logicOp

    def And(self, other: Self):
        if self.logicOp is None and other.logicOp is None:

        return None 
    
    def Or(self, other: Self):
        return None 

class UnaryPredicate(BasicPredicate):
    predicate: BasicPredicate
    def __init__(self, predicate: BasicPredicate,) -> None:
        self.predicate = predicate
    
    def Not(self) -> Self:
        return UnaryPredicate(self, NOT)
    
    def And(self, other: Self) -> BinaryPredicate:
        return BinaryPredicate([self, other], AND)

    def Or(self, other: Self) -> BinaryPredicate:
        return BinaryPredicate([self, other], OR)



