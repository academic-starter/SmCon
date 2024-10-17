from typing import Dict, List, Union
import logging 
from .model import createDataModel

class StorageModelReader:
    def __init__(self, storageLayout) -> None:
        self.model = createDataModel(storageLayout)

    def getModel(self):
        return self.model 
    
    def read(self, slot: Union[str, int], oldVal, newVal):
        if isinstance(slot, str) and slot.startswith("0x"):
            slot = int(slot[2:], base=16)
        if not self.model.setValue(slot, newVal):
            logging.log(logging.DEBUG, "missing (slot: {0}, value: {1})".format(hex(slot), newVal))
            return False 
        return True