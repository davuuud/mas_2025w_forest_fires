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
            elif vis == "FullVisualizer":
                logger.debug("Append FullVisualizer.")
                visualizers.append(FullVisualizer(config))
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
    State.INCOMBUSTIBLE:    [0x23, 0x00, 0x07],
    State.VEGETATION:       [0x60, 0x6C, 0x38], 
    State.HOT:              [0xD2, 0x82, 0x31],
    State.FIRE:             [0xC1, 0x1D, 0x1D], 
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

class FullVisualizer(Visualizer):
    # Base color by state (RGB)
    BASE_COLORS = {
        State.INCOMBUSTIBLE:    [0x23, 0x00, 0x07],
        State.VEGETATION:       [0x60, 0x6C, 0x38], 
        State.HOT:              [0xFF, 0xC6, 0x00],
        State.FIRE:             [0xC1, 0x1D, 0x1D], 
    }

    # Heat LUT: (add_to_R, subtract_from_G_and_B)
    HEAT_LUT = [
        (  0,   0),   # heat 0
        ( 30,  10),
        ( 60,  20),
        (100,  35),
        (140,  50),
        (180,  70),   # heat 5
    ]

    # Fuel LUT: brightness multiplier
    FUEL_LUT = [
        0.40,  # fuel 0
        0.52,
        0.64,
        0.78,
        0.90,
        1.00,  # fuel 5
    ]

    # Oxygen LUT: saturation factor (reduced influence)
    # 0 = fully gray, 1 = full color
    OXYGEN_LUT = [
        0.65,
        0.70,
        0.74,
        0.77,
        0.79,
        0.80,  # capped influence
    ]


    def clamp(self, x):
        return max(0, min(255, int(x)))

    def apply_oxygen(self, r, g, b, oxygen_level):
        """
        Pull color toward gray based on oxygen level.
        Lower oxygen => smokier / desaturated.
        """
        gray = (r + g + b) // 3
        t = self.OXYGEN_LUT[oxygen_level]

        r = gray + (r - gray) * t
        g = gray + (g - gray) * t
        b = gray + (b - gray) * t

        return r, g, b

    def cell_color(self,state, heat, fuel, oxygen):
        """
        Compute RGB color for a cell using lookup tables.

        state   : "fire", "hot", "vegetation", "incombustible"
        heat    : int [0..5]
        fuel    : int [0..5]
        oxygen  : int [0..5]
        """

        # Base color
        r, g, b = self.BASE_COLORS[state]

        # Heat influence
        add_r, sub_gb = self.HEAT_LUT[int(heat)]
        r += add_r
        g -= sub_gb
        b -= sub_gb

        # Fuel influence (brightness)
        f = self.FUEL_LUT[int(fuel)]
        r *= f
        g *= f
        b *= f

        # Oxygen influence (desaturation)
        r, g, b = self.apply_oxygen(r, g, b, int(oxygen))

        return [
            max(0, min(255, int(r))), 
            max(0, min(255, int(g))), 
            max(0, min(255, int(b)))]


    def frame(self, state: State):
        width = self.config.width
        height = self.config.height
        # flatten arrays and compute color per cell
        heat_arr = state.heat.flatten()
        fuel_arr = state.fuel.flatten()
        oxy_arr = state.oxygen.flatten()
        st_arr = state.cell_state.flatten()

        cell_colors = [
            self.cell_color(s, h, f, o)
            for h, f, o, s in zip(heat_arr, fuel_arr, oxy_arr, st_arr)
        ]

        with open(self.get_output_path(), "w") as outfile:
            self.backend.write(outfile, width, height, cell_colors, scaling=self.config.output_scaling)
