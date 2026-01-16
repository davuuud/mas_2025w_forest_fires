
class State:
    #states
    FIRE = 0
    INCOMBUSTIBLE = 1
    HOT = 2
    VEGETATION = 3

    STATESCOUNT = 4

    def __init__(self, heat, fuel, oxygen, cell_state):
        self.heat = heat
        self.fuel = fuel
        self.oxygen = oxygen
        self.cell_state = cell_state

    def __str__(self):
        return f"oxygen map:\n {self.oxygen} \n fuel map:\n {self.fuel}\n heat map:\n {self.heat}\n state map:\n {self.cell_state}"