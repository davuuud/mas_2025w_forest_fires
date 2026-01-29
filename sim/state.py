import numpy as np

class State:
    STATESCOUNT = 4

    #states
    FIRE = 0
    INCOMBUSTIBLE = 1
    HOT = 2
    VEGETATION = 3

    def __init__(self, heat, fuel, oxygen, cell_state):
        self.heat = heat
        self.fuel = fuel
        self.oxygen = oxygen
        self.cell_state = cell_state
        self.time_since_burnt_out = np.zeros_like(cell_state, dtype=int)

    def __str__(self):
        return (
            f"State map:\n {self.cell_state}\n"
            f"Oxygen map:\n {self.oxygen}\n"
            f"Fuel map:\n {self.fuel}\n"
            f"Heat map:\n {self.heat}"
        )