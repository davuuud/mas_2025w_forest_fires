from .config import Configuration
import numpy as np

class Preset:
    def get(self):
        pass


class RandomPreset(Preset):
    @classmethod
    def get(cls, config: Configuration):
        oxygen = np.random.randint(5, size=(config.width, config.height))
        fuel = np.random.randint(5, size=(config.width, config.height))
        heat = np.random.randint(5, size=(config.width, config.height))
        return (oxygen, fuel, heat)