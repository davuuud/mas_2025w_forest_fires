import logging
from config import Configuration
from visual import VisualizerGenerator

from .preset import PresetGenerator
from .neighborhood import NeighborhoodGenerator
from .rule import RuleGenerator


class Simulation:
    def __init__(self, config: Configuration):
        self.logger = logging.getLogger("Simulation")
        self.config = config

        self.preset = PresetGenerator.get(self.config)
        self.state = self.preset.generate()
        self.logger.debug(self.state)

        self.neighborhood = NeighborhoodGenerator.get(self.config)

        self.rules = RuleGenerator.get(self.config)

        self.visualizers = VisualizerGenerator.get(self.config)


    def run(self, steps: int = 1):
        #pass intial frame to visualizer
        for v in self.visualizers:
            v.write_frame(self.state)

        for step in range(steps):
            #calculate neighborhood
            nbs = self.neighborhood.calculate(self.state)

            #apply rules
            for rule in self.rules:
                self.state = rule.calculate(self.state, nbs)
            
            #pass frame to visualizer
            for v in self.visualizers:
                v.write_frame(self.state)
            print(f"##### step {step}: #####")
            print(self.state)


