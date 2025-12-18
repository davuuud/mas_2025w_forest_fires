from config import Configuration
from visual import Visualizer, PPM
import numpy as np

class Simulation:
    #  GRID_SHAPE = (HEIGTH, WIDTH, CELL_VALUES)

    CELL_SHAPE = (3,)  # (Heat, )

    def __init__(self, config: Configuration, visualizer: Visualizer = PPM()):
        self.config = config
        self.visualizer = visualizer
        self.grid = np.array()

    def run(self, steps=1):
        pass
