import numpy as np
from sim import State

class NeighborhoodGenerator:
    @classmethod
    def get(cls, neighborhood_str = ""):
        neighborhood = None
        if neighborhood_str == "NeumannNeighborhood":
            neighborhood = NeumannNeighborhood()
        else:
            pass
        return neighborhood


class Neighborhood:

    #returns new state
    def calculate(self, state):
        pass


class NeumannNeighborhood(Neighborhood):
    
    def calculate(self, state, width, height):
        #oxygen, fuel, heat, state = state
        
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