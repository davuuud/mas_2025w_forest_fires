import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from config import Configuration
from sim.state import State

from .backend import ImageWriterBackendGenerator

class VisualizerGenerator:
    @classmethod
    def get(cls, config: Configuration):
        logger = logging.getLogger("VisualizerGenerator")
        visualizers = []
        for vis in config.visualizers:
            if vis == "CellStateVisualizer":
                logger.debug("Append CellStateVisualizer.")
                visualizers.append(CellStateVisualizer(config))
            else:
                logger.error("Invalid visualizer: {vis}.")
                pass
        return visualizers


class Visualizer(ABC):
    def __init__(self, config: Configuration):
        self.config = config 
        self.backend = ImageWriterBackendGenerator.get(self.config)
        self.frame_id = 0

    def get_output_path(self):
        output_dir = Path(self.config.output_dir)
        if not output_dir.exists():
            os.mkdir(output_dir)
        return output_dir / Path(self.config.output_pattern % (self.frame_id))

    def write_frame(self, state: State):
        self.frame(state)
        self.frame_id += 1

    @abstractmethod
    def frame(self, state: State):
        pass


COLOR_MAP = {
    State.FIRE:             [255, 0, 0], 
    State.INCOMBUSTIBLE:    [0, 0, 0],
    State.HOT:              [255, 165, 0],
    State.VEGETATION:       [0, 255, 0], 
}
assert(len(COLOR_MAP) == State.STATESCOUNT)

# Visualizers for every variable:
#     - cell state 
#     - oxygen
#     - fuel
#     - heat

class CellStateVisualizer(Visualizer):
    def frame(self, state: State):
        width = self.config.width
        height = self.config.height
        cell_state = state.cell_state.flatten()
        cell_colors = [COLOR_MAP[x] for x in cell_state]
        with open(self.get_output_path(), "w") as outfile:
            self.backend.write(outfile, width, height, cell_colors, scaling=self.config.output_scaling)
