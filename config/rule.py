import numpy as np
import logging
from sim import State
#from sim import Simulation

class RuleGenerator:
    @classmethod
    def get(cls, rules_str = [""]):
        logger = logging.getLogger("RuleGenerator")
        rules = []
        for str in rules_str:
            if str == "DecreseWhenFireRule":
                rules.append(DecreseWhenFireRule())
            elif str =="IncreaseHotForNeighborRule":
                rules.append(IncreaseHotForNeighborRule())
            else:
                logger.error("Unkown Rule")
        return rules


class Rule:

    #returns new state
    def calculate(self, state, nbs):
        pass


class DecreseWhenFireRule(Rule):
    
    def calculate(self, state, nbs):
        mask = (state.cell_state == State.FIRE)
        
        # reduce oxygen, fuel, heat by 1 where the cell is on fire; clamp at 0
        state.oxygen = np.where(mask, np.maximum(state.oxygen - 1, 0), state.oxygen)
        state.fuel = np.where(mask, np.maximum(state.fuel - 1, 0), state.fuel)
        state.heat = np.where(mask, np.maximum(state.heat - 1, 0), state.heat)
        
        return state
    
class IncreaseHotForNeighborRule(Rule):
    
    def calculate(self, state, nbs):
        #oxygen, fuel, heat, state = state
        #nbs_ox, nbs_fuel, nbs_heat, nbs_state = nbs
        # every state with hot in the neighborhood increases hot of the cell, max 5
        state.heat = np.minimum(state.heat+nbs.cell_state[State.HOT],5)
        
        return state