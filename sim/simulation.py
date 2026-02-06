import logging
from config import Configuration
from visual.visualizer import VisualizerContainer

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

        self.visualizers = VisualizerContainer(self.config)


    def run(self, steps: int = None):
        steps = steps if steps else self.config.steps 

        #pass intial frame to visualizer
        self.visualizers.visualize(self.state)

        for step in range(steps):
            #calculate neighborhood
            nbs = self.neighborhood.calculate(self.state)

            #apply rules
            for rule in self.rules:
                self.state = rule.calculate(self.state, nbs)
            
            #pass frame to visualizer
            self.visualizers.visualize(self.state)

        self.visualizers.finish()
