import logging
import numpy as np
from config import Configuration

from .neighborhood import Neighborhood
from .state import State

class RuleGenerator:
    @classmethod
    def get(cls, config: Configuration):
        logger = logging.getLogger("RuleGenerator")
        rules = []
        for rule in config.rules:
            if rule == "DecreaseWhenFireRule":
                rules.append(DecreaseWhenFireRule())
                logger.debug("Append DecreaseWhenFireRule")
            elif rule =="IncreaseHotForNeighborRule":
                rules.append(IncreaseHotForNeighborRule())
                logger.debug("Append IncreaseHotForNeighborRule")
            elif str =="IncreaseHeatExactlyOneFireRule":
                rules.append(IncreaseHeatExactlyOneFireRule())
            else:
                logger.error("Unknown Rule")
        return rules


class Rule:
    def calculate(self, state: State, nbs: Neighborhood) -> State:
        pass


class DecreaseWhenFireRule(Rule):
    def calculate(self, state: State, nbs: Neighborhood) -> State:
        mask = (state.cell_state == State.FIRE)
        
        # reduce oxygen, fuel, heat by 1 where the cell is on fire; clamp at 0
        mask = (state.cell_state == State.FIRE)
        state.oxygen = np.where(mask, np.maximum(state.oxygen - 1, 0), state.oxygen)
        state.fuel = np.where(mask, np.maximum(state.fuel - 1, 0), state.fuel)
        state.heat = np.where(mask, np.maximum(state.heat - 1, 0), state.heat)
        
        return state
    

class IncreaseHotForNeighborRule(Rule):
    
    def calculate(self, state, nbs):
        # every state with hot in the neighborhood increases hot of the cell, max 5
        state.heat = np.minimum(state.heat+nbs.cell_state[State.HOT],5)
        
        return state
    
class IncreaseHeatExactlyOneFireRule(Rule):
    def calculate(self, state, nbs):
        mask = (nbs.cell_state[State.FIRE] == 1)
        state.heat = np.where(mask,np.minimum(state.heat + 2, 5), state.heat)

        return state