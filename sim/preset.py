import logging
import numpy as np
from abc import ABC, abstractmethod
from config import Configuration

from .state import State

class PresetGenerator:
    @classmethod
    def get(cls, config: Configuration) -> Preset:
        logger = logging.getLogger("PresetGenerator")
        preset: Preset = None
        if config.preset_source == "random":
            preset = RandomPreset(config)
            logger.info("RemotePreset chosen")
        if config.preset_source == "firewall":
            preset = FireWallPreset(config)
            logger.info("FireWallPreset chosen")
        else:
            preset = RandomPreset(config)
            logger.error("No or invalid preset given -> fallback to RemotePreset")
        return preset


class Preset(ABC):
    def __init__(self, config: Configuration):
        self.config = config

    @abstractmethod
    def generate(self):
        pass


class RandomPreset(Preset):
    FIRE_PROBABILITY = 0.1

    def generate(self):
        size = (self.config.width, self.config.height)

        veg_state = np.full(size, State.VEGETATION)
        veg_oxygen = np.full(size, 4)
        veg_fuel = np.zeros(size)
        veg_heat = np.zeros(size)

        fire_state = np.full(size, State.FIRE)
        fire_oxygen = np.full(size, 4)
        fire_fuel = np.full(size, 4)
        fire_heat = np.full(size, 4)

        rng = np.random.default_rng(self.config.seed)
        mask = rng.uniform(size=size)
        state = np.where(mask < self.FIRE_PROBABILITY, fire_state, veg_state)
        oxygen = np.where(mask < self.FIRE_PROBABILITY, fire_oxygen, veg_oxygen)
        fuel = np.where(mask < self.FIRE_PROBABILITY, fire_fuel, veg_fuel)
        heat = np.where(mask < self.FIRE_PROBABILITY, fire_heat, veg_heat)

        return State(heat, fuel, oxygen, state)


class FireWallPreset(Preset):
    def generate(self):
        size = (self.config.width, self.config.height)

        state = np.full(size, State.VEGETATION)
        oxygen = np.full(size, 4)
        fuel = np.zeros(size)
        heat = np.zeros(size)

        state[:, 0] = State.FIRE
        state[:, -1] = State.FIRE
        oxygen[:, 0] = 4
        oxygen[:, -1] = 4
        fuel[:, 0] = 4
        fuel[:, -1] = 4
        heat[:, 0] = 4
        heat[:, -1] = 4

        return State(heat, fuel, oxygen, state)