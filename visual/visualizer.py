import os
from pathlib import Path
from .ppm import PPM

class Visualizer:
    def __init__(self, config):
        self.config = config 
        self.frame_id = 0

    def get_output_path(self):
        output_dir = Path(self.config.output_dir)
        if not output_dir.exists():
            os.mkdir(output_dir)
        return output_dir / Path(self.config.output_pattern % (self.frame_id))

    def write_frame(self, state):
        self.frame(state)
        self.frame_id += 1

    def frame(self, state):
        pass


class VisualizerFactory:
    @classmethod
    def get_visualizers(cls, config):
        visualizers = []
        for vis in config.visualizers:
            if vis == "PPMCellStateVisualizer":
                visualizers.append(PPMCellStateVisualizer(config))
            else:
                pass
        return visualizers


COLOR_MAP = {
    0: [255, 0, 0], 
    1: [0, 0, 0],
    2: [255, 165, 0],
    3: [0, 255, 0], 
}

# Visualizers for every variable:
#     - cell state 
#     - oxygen
#     - fuel
#     - heat

class PPMCellStateVisualizer(Visualizer):
    def frame(self, state):
        width = self.config.width
        height = self.config.height
        cell_state = state.cell_state.flatten()
        cell_colors = [COLOR_MAP[x] for x in cell_state]
        ppm = PPM()
        with open(self.get_output_path().with_suffix(".ppm"), "w") as outfile:
            ppm.write_ppm(outfile, width, height, cell_colors)
