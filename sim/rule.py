import logging
import numpy as np
from abc import ABC, abstractmethod
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
            elif rule == "IncreaseHeatExactlyOneFireRule":
                rules.append(IncreaseHeatExactlyOneFireRule())
            elif rule == "IncreaseHeatMoreThanOneFireRule":
                rules.append(IncreaseHeatMoreThanOneFireRule())
                logger.debug("Append IncreaseHeatMoreThanOneFireRule")
            elif rule == "IncreaseOxygenIfNeighborsHigherRule":
                rules.append(IncreaseOxygenIfNeighborsHigherRule())
                logger.debug("Append IncreaseOxygenIfNeighborsHigherRule")
            elif rule == "VegetationToHotRule":
                rules.append(VegetationToHotRule())
                logger.debug("Append VegetationToHotRule")
            elif rule == "CellOnFireRule":
                # pass config so the rule can check rule_approach and seed
                rules.append(CellOnFireRule(config))
                logger.debug("Append CellOnFireRule")
            elif rule == "DecreaseHeatInIncombustibleRule":
                rules.append(DecreaseHeatInIncombustibleRule())
                logger.debug("Append DecreaseHeatInIncombustibleRule")
            else:
                logger.error("Invalid rule: {rule}.")
        return rules


class Rule(ABC):
    @abstractmethod
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
    # every state with hot in the neighborhood increases hot of the cell, max 5
    def calculate(self, state, nbs):
        state.heat = np.minimum(state.heat+nbs.cell_state[State.HOT],5)
        
        return state
    
class IncreaseHeatExactlyOneFireRule(Rule):
    # increase heat by 2 if exactly one neighbor is on fire, max 5
    def calculate(self, state, nbs):
        mask = (nbs.cell_state[State.FIRE] == 1)
        state.heat = np.where(mask,np.minimum(state.heat + 2, 5), state.heat)

        return state

class IncreaseHeatMoreThanOneFireRule(Rule):
    # increase heat by 4 if more than one neighbor is on fire, max 5
    def calculate(self, state, nbs):
        mask = (nbs.cell_state[State.FIRE] > 1)
        state.heat = np.where(mask,np.minimum(state.heat + 4, 5), state.heat)

        return state


class IncreaseOxygenIfNeighborsHigherRule(Rule):
    # increase oxygen by 1 if 2 or more neighbors have higher oxygen level, max 5
    def calculate(self, state, nbs):
        # nbs.oxygen_higher_count contains number of neighbors with higher oxygen (0..4)
        mask = (nbs.oxygen_higher_count >= 2)
        state.oxygen = np.where(mask, np.minimum(state.oxygen + 1, 5), state.oxygen)
        return state


class VegetationToHotRule(Rule):
    # Vegetation with any heat becomes HOT
    def calculate(self, state: State, nbs: Neighborhood) -> State:
        mask = (state.cell_state == State.VEGETATION) & (state.heat > 0)
        state.cell_state = np.where(mask, State.HOT, state.cell_state)
        return state
    
class DecreaseHeatInIncombustibleRule(Rule):
    # Decrease heat by 1 for INCOMBUSTIBLE cells each step, clamp at 0
    def calculate(self, state: State, nbs: Neighborhood) -> State:
        mask = (state.cell_state == State.INCOMBUSTIBLE)
        state.heat = np.where(mask, np.maximum(state.heat - 1, 0), state.heat)
        return state
    
class CellOnFireRule(Rule):
    # Decide ignition/extinguishing based on the configured approach.
    def __init__(self, config: Configuration = None, threshold_sum: int = 8,
                 t_heat: int = 3, t_fuel: int = 1, t_oxygen: int = 1,
                 pb: float = 0.05, po: float = 0.10):
        # default values
        self.config = config
        self.approach = 'general'
        self.threshold_sum = threshold_sum
        self.t_heat = t_heat
        self.t_fuel = t_fuel
        self.t_oxygen = t_oxygen
        self.pb = pb
        self.po = po

        # override from config if provided
        if config is not None:
            self.approach = getattr(config, 'rule_approach', self.approach)
            self.threshold_sum = getattr(config, 'threshold_sum', self.threshold_sum)
            self.t_heat = getattr(config, 't_heat', self.t_heat)
            self.t_fuel = getattr(config, 't_fuel', self.t_fuel)
            self.t_oxygen = getattr(config, 't_oxygen', self.t_oxygen)
            self.pb = getattr(config, 'pb', self.pb)
            self.po = getattr(config, 'po', self.po)
            seed = getattr(config, 'seed', None)
        else:
            seed = 123

        # reproducible RNG when seed provided
        self.rng = np.random.RandomState(seed)

    def calculate(self, state: State, nbs: Neighborhood) -> State:
        # only HOT cells can ignite now
        hot = (state.cell_state == State.HOT)
        has_fuel_ox = (state.fuel > 0) & (state.oxygen > 0)

        if self.approach == 'general':
            total = state.heat + state.fuel + state.oxygen
            ignite = hot & has_fuel_ox & (total >= self.threshold_sum)
            state.cell_state = np.where(ignite, State.FIRE, state.cell_state)

        elif self.approach == 'individual':
            cond = (
                hot & has_fuel_ox &
                (state.heat >= self.t_heat) &
                (state.fuel >= self.t_fuel) &
                (state.oxygen >= self.t_oxygen)
            )
            state.cell_state = np.where(cond, State.FIRE, state.cell_state)

        elif self.approach == 'stochastic':
            # ignition: HOT cell with fuel+oxygen can ignite with probability pb
            rand = self.rng.random_sample(state.cell_state.shape)
            ignite = hot & has_fuel_ox & (rand < self.pb)
            state.cell_state = np.where(ignite, State.FIRE, state.cell_state)

            # extinction: burning cells can go out with probability po -> become HOT
            rand2 = self.rng.random_sample(state.cell_state.shape)
            burning = (state.cell_state == State.FIRE)
            extinguish = burning & (rand2 < self.po)
            state.cell_state = np.where(extinguish, State.INCOMBUSTIBLE, state.cell_state)

        else:
            # fallback to general
            total = state.heat + state.fuel + state.oxygen
            ignite = hot & has_fuel_ox & (total >= self.threshold_sum)
            state.cell_state = np.where(ignite, State.FIRE, state.cell_state)
        
        # Extinction rule for general and individual approaches: if any of
        # heat, oxygen or fuel is zero, a burning cell becomes INCOMBUSTIBLE
        unsustainable = (state.heat <= 0) | (state.oxygen <= 0) | (state.fuel <= 0)
        burning_now = (state.cell_state == State.FIRE)
        to_incombustible = burning_now & unsustainable
        state.cell_state = np.where(to_incombustible, State.INCOMBUSTIBLE, state.cell_state)

        return state

