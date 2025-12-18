import numpy as np

class PresetGenerator:
    @classmethod
    def get(cls, source="random", width=10, height=10, file=None):
        preset = None
        if source == "random":
            preset = RandomPreset(width, height)
        else:
            preset =  RandomPreset(width, height)
        return preset.gene


class Preset:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def generate(self):
        pass


class RandomPreset(Preset):
    def generate(self, width, height):
        oxygen = np.random.randint(5, size=(width, height))
        fuel = np.random.randint(5, size=(width, height))
        heat = np.random.randint(5, size=(width, height))
        return (oxygen, fuel, heat)