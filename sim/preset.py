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
        print(config.preset_source == "firewall")
        if config.preset_source == "random":
            preset = RandomPreset(config)
            logger.info("RandomPreset chosen")
        elif config.preset_source == "firewall":
            preset = FireWallPreset(config)
            logger.info("FireWallPreset chosen")
        elif config.preset_source == "spark":
            preset = SparkPreset(config)
            logger.info("SparkPreset chosen")
        else:
            preset = RandomPreset(config)
            logger.error("No or invalid preset given -> fallback to RandomPreset")
        return preset


class Preset(ABC):
    def __init__(self, config: Configuration):
        self.config = config

    @abstractmethod
    def generate(self):
        pass


class RandomPreset(Preset):
    FIRE_PROBABILITY = 0.05

    def generate(self):
        size = (self.config.width, self.config.height)
        rng = np.random.default_rng(self.config.seed)

        veg_state = np.full(size, State.VEGETATION)
        veg_oxygen = np.full(size, 4)
        veg_fuel = rng.integers(0, 6, size=size)
        veg_heat = np.zeros(size)

        fire_state = np.full(size, State.FIRE)
        fire_oxygen = np.full(size, 4)
        fire_fuel = np.full(size, 4)
        fire_heat = np.full(size, 4)

        mask = rng.uniform(size=size)
        state = np.where(mask < self.FIRE_PROBABILITY, fire_state, veg_state)
        oxygen = np.where(mask < self.FIRE_PROBABILITY, fire_oxygen, veg_oxygen)
        fuel = np.where(mask < self.FIRE_PROBABILITY, fire_fuel, veg_fuel)
        heat = np.where(mask < self.FIRE_PROBABILITY, fire_heat, veg_heat)

        return State(heat, fuel, oxygen, state)


class FireWallPreset(Preset):
    def generate(self):
        random = RandomPreset(self.config).generate()
        size = (self.config.width, self.config.height)

        state = np.full(size, State.VEGETATION)
        #oxygen = (random.oxygen % 3) + 1
        #fuel = (random.fuel % 3) + 1
        oxygen = random.oxygen
        fuel = random.fuel
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
    

class SparkPreset(Preset):
    def generate(self):
        random = RandomPreset(self.config).generate()
        size = (self.config.width, self.config.height)

        state = np.full(size, State.VEGETATION)
        oxygen = random.oxygen
        fuel = (random.fuel % 3)
        heat = np.zeros(size)

        state[(self.config.width//2),(self.config.height//2)] = State.FIRE
        oxygen[(self.config.width//2),(self.config.height//2)] = 4
        fuel[(self.config.width//2),(self.config.height//2)] = 4
        heat[(self.config.width//2),(self.config.height//2)] = 4

        return State(heat, fuel, oxygen, state)