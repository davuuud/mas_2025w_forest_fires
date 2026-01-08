import numpy as np

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
        oxygen, fuel, heat, state = state
        
        # oxygen neighborhood
        nbs_ox = np.zeros((width+2, height+2))
        #nbs_ox[1:-1,1:-1]+=oxygen #middle
        nbs_ox[1:-1,:-2]+=oxygen #left
        nbs_ox[1:-1,2:]+=oxygen #right
        nbs_ox[:-2,1:-1]+=oxygen #up
        nbs_ox[2:,1:-1]+=oxygen #down

        # fuel neighborhood
        nbs_fuel = np.zeros((width+2, height+2))
        #nbs_fuel[1:-1,1:-1]+=fuel #middle
        nbs_fuel[1:-1,:-2]+=fuel #left
        nbs_fuel[1:-1,2:]+=fuel #right
        nbs_fuel[:-2,1:-1]+=fuel #up
        nbs_fuel[2:,1:-1]+=fuel #down
        
        # heat neighborhood
        nbs_heat = np.zeros((width+2, height+2))
        #nbs_heat[1:-1,1:-1]+=heat #middle
        nbs_heat[1:-1,:-2]+=heat #left
        nbs_heat[1:-1,2:]+=heat #right
        nbs_heat[:-2,1:-1]+=heat #up
        nbs_heat[2:,1:-1]+=heat #down
        
        # state neighborhood (is array with numbers of all 4 states)
        nbs_state = []
        for i in range(4):
            state_i = (state == i)
            nbs_state_i = np.zeros((width+2, height+2))
            #nbs_state_i[1:-1,1:-1]+=state_i #middle
            nbs_state_i[1:-1,:-2]+=state_i #left
            nbs_state_i[1:-1,2:]+=state_i #right
            nbs_state_i[:-2,1:-1]+=state_i #up
            nbs_state_i[2:,1:-1]+=state_i #down
            nbs_state.insert(i,nbs_state_i[1:-1,1:-1])

        return [nbs_ox[1:-1,1:-1], nbs_fuel[1:-1,1:-1], nbs_heat[1:-1,1:-1], nbs_state]