import numpy as np
from sim import State

class PresetGenerator:
    @classmethod
    def get(cls, source="random", width=10, height=10, seed=None, file=None):
        preset = None
        if source == "random":
            preset = RandomPreset(width, height, seed)
        else:
            #preset =  RandomPreset(width, height)
            pass
        return preset


class Preset:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def generate(self):
        pass


class RandomPreset(Preset):
    def __init__(self, width, height, seed):
        super().__init__(width,height)
        self.seed = seed
    
    def generate(self):
        rng = np.random.default_rng(self.seed)
        oxygen = rng.integers(0, 5, size=(self.width, self.height))
        fuel = rng.integers(0, 5, size=(self.width, self.height))
        heat = rng.integers(0, 5, size=(self.width, self.height))
        state = rng.integers(0, 3, size=(self.width, self.height))
        return State(heat,fuel,oxygen,state)