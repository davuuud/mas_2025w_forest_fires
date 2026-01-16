import logging
import numpy as np
from config import Configuration

from .state import State

class NeighborhoodGenerator:
    @classmethod
    def get(cls, config: Configuration):
        logger = logging.getLogger("NeighborhoodGenerator")
        neighborhood = None
        if config.neighborhood == "NeumannNeighborhood":
            neighborhood = NeumannNeighborhood(config)
            logger.debug("Von Neumann neighborhood chosen")
        else:
            neighborhood = NeumannNeighborhood(config)
            logger.error("No or invalid neighborhood given -> fallback to Von Neumann neighborhood")
        return neighborhood


class Neighborhood:
    def __init__(self, config: Configuration):
        self.config = config

    def calculate(self, state: State):
        pass


class NeumannNeighborhood(Neighborhood):
    def calculate(self, state):
        width = self.config.width
        height = self.config.height
        
        # oxygen neighborhood
        nbs_ox = np.zeros((width+2, height+2))
        #nbs_ox[1:-1,1:-1]+=oxygen #middle
        nbs_ox[1:-1,:-2]+=state.oxygen #left
        nbs_ox[1:-1,2:]+=state.oxygen #right
        nbs_ox[:-2,1:-1]+=state.oxygen #up
        nbs_ox[2:,1:-1]+=state.oxygen #down

        # fuel neighborhood
        nbs_fuel = np.zeros((width+2, height+2))
        #nbs_fuel[1:-1,1:-1]+=fuel #middle
        nbs_fuel[1:-1,:-2]+=state.fuel #left
        nbs_fuel[1:-1,2:]+=state.fuel #right
        nbs_fuel[:-2,1:-1]+=state.fuel #up
        nbs_fuel[2:,1:-1]+=state.fuel #down
        
        # heat neighborhood
        nbs_heat = np.zeros((width+2, height+2))
        #nbs_heat[1:-1,1:-1]+=heat #middle
        nbs_heat[1:-1,:-2]+=state.heat #left
        nbs_heat[1:-1,2:]+=state.heat #right
        nbs_heat[:-2,1:-1]+=state.heat #up
        nbs_heat[2:,1:-1]+=state.heat #down
        
        # state neighborhood (is array with numbers of all 4 states)
        nbs_state = []
        for i in range(State.STATESCOUNT):
            state_i = (state.cell_state == i)
            nbs_state_i = np.zeros((width+2, height+2))
            #nbs_state_i[1:-1,1:-1]+=state_i #middle
            nbs_state_i[1:-1,:-2]+=state_i #left
            nbs_state_i[1:-1,2:]+=state_i #right
            nbs_state_i[:-2,1:-1]+=state_i #up
            nbs_state_i[2:,1:-1]+=state_i #down
            nbs_state.insert(i,nbs_state_i[1:-1,1:-1])

        return State(nbs_ox[1:-1,1:-1], nbs_fuel[1:-1,1:-1], nbs_heat[1:-1,1:-1], nbs_state)