from config import Configuration
from visual import Visualizer, PPM
import numpy as np

class Simulation:
    #  GRID_SHAPE = (HEIGTH, WIDTH, CELL_VALUES)

    CELL_SHAPE = (0,0,0,0)  # (oxygen,fuel,heat,state)

    #states
    FIRE = 0
    INCOMBUSTIBLE = 1
    HOT = 2
    Vegetation = 3

    def __init__(self, config: Configuration, visualizer: Visualizer = PPM()):
        self.config = config
        self.visualizer = visualizer
        self.grid = self.config.preset.generate()
        print(self.grid)

    def run(self, steps=1):
        #pass intial frame to visualizer
        #self.visualizer.frame(self.grid)

        for step in range(steps):
            #calculate neighborhood
            nbs = self.config.neighborhood.calculate(self.grid,self.config.width,self.config.height)

            #apply rules
            for rule in self.config.rules:
                self.grid = rule.calculate(self.grid,nbs)
            
            #pass frame to visualizer
            #self.visualizer.frame(self.grid)
            print(f"##### step {step}: #####")
            print("orxygen map:")
            print(self.grid[0])
            print("fuel map:")
            print(self.grid[1])
            print("heat map:")
            print(self.grid[2])
            print("state map:")
            print(self.grid[3])


