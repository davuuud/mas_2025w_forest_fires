import numpy as np
import logging
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
        oxygen, fuel, heat, state = state
        mask = (state == 0)
        
        # reduce oxygen, fuel, heat by 1 where the cell is on fire; clamp at 0
        oxygen = np.where(mask, np.maximum(oxygen - 1, 0), oxygen)
        fuel = np.where(mask, np.maximum(fuel - 1, 0), fuel)
        heat = np.where(mask, np.maximum(heat - 1, 0), heat)
        
        return (oxygen, fuel, heat, state)
    
class IncreaseHotForNeighborRule(Rule):
    
    def calculate(self, state, nbs):
        oxygen, fuel, heat, state = state
        nbs_ox, nbs_fuel, nbs_heat, nbs_state = nbs
        # every state with hot in the neighborhood increases hot of the cell, max 5
        heat = np.minimum(heat+nbs_state[2],5)
        
        return (oxygen, fuel, heat, state)