import logging
import numpy as np
from config import Configuration

from .state import State

class PresetGenerator:
    @classmethod
    def get(cls, config: Configuration) -> Preset:
        logger = logging.getLogger()
        preset: Preset = None
        if config.preset_source == "random":
            preset = RandomPreset(config)
            logger.info("RemotePreset chosen")
        else:
            preset = RandomPreset(config)
            logger.error("No or invalid preset given -> fallback to RemotePreset")
        return preset


class Preset:
    def __init__(self, config: Configuration):
        self.config = config

    def generate(self):
        pass


class RandomPreset(Preset):
    def generate(self):
        #rng = np.random.default_rng(self.config.preset_seed)
        rng = np.random.default_rng(self.config.seed)
        state = rng.integers(0, 3, size=(self.config.width, self.config.height))
        oxygen = rng.integers(0, 5, size=(self.config.width, self.config.height))
        fuel = rng.integers(0, 5, size=(self.config.width, self.config.height))
        heat = rng.integers(0, 5, size=(self.config.width, self.config.height))
        return State(heat, fuel, oxygen, state)