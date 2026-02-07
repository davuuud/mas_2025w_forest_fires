import copy
import inspect
import logging
import numpy as np
import os
import sys
from abc import ABC, abstractmethod
from ffmpeg import FFmpeg
from pathlib import Path
from config import Configuration
from sim.state import State

from .backend import BackendGenerator, ImageBackend, PlotBackend

logger = logging.getLogger("Visualizer")

def generate_video(dir: Path, name: Path, input_pattern: str, rate: int) -> None:
    if dir.exists() and dir.is_dir():
        video_path = dir / name
        if video_path.exists():
            logger.warning(f"Deleting existing video {video_path}.")
            os.remove(video_path)
        logger.info(f"Generating video {video_path} from {input_pattern}.")
        input_pattern = dir / Path(input_pattern)
        FFmpeg().input(input_pattern).option("r", rate).output(video_path).execute()
    else:
        logger.critical(f"Output directory {dir} does not exist. It should be created by the visualizer, so something went horribly wrong.")


class VisualizerContainer:
    def __init__(self, config: Configuration):
        self.logger = logging.getLogger("VisualizerContainer")

        mod = sys.modules[__name__]
        classes = inspect.getmembers(mod, inspect.isclass)
        self.available_visualizers = {name: klass for name, klass in classes if issubclass(klass, Visualizer) and klass is not Visualizer}
        self.visualizers: list[Visualizer] = []

        done = []
        for name in config.visualizers:
            visualizer = self.get(name)
            if not visualizer or name in done:
                continue
            self.visualizers.append(visualizer(config))

    def get(self, name):
        visualizer = self.available_visualizers.get(name, None)
        if visualizer:
            self.logger.debug(f"Append {name}")
            return visualizer
        self.logger.error(f"Invalid visualizer: {name}")
        return None

    def visualize(self, state: State) -> None:
        for vis in self.visualizers:
            vis.visualize(state)

    def finish(self) -> None:
        for vis in self.visualizers:
            vis.finish()
    

class Visualizer(ABC):
    def __init__(self, config: Configuration):
        if not hasattr(self, 'DEFAULT_CONFIG'):
            raise NotImplementedError(f"{self.__class__.__name__} is missing DEFAULT_CONFIG")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config 
        self.frame_id = 0
        
    def get_dir_name(self) -> str:
        dir = self.config.get(self.__class__.__name__, 'directory', fallback=self.DEFAULT_CONFIG.get('directory'))
        if not dir:
            raise NotImplementedError(f"{self.__class__.__name__}.DEFAULT_CONFIG is missing 'directory'.")
        return dir

    def get_pattern(self) -> str:
        pattern = self.config.get(self.__class__.__name__, 'pattern', fallback=self.DEFAULT_CONFIG.get('pattern'))
        if not pattern:
            raise NotImplementedError(f"{self.__class__.__name__}.DEFAULT_CONFIG is missing 'pattern'.")
        return pattern

    def get_file_name(self) -> str:
        name = self.config.get(self.__class__.__name__, 'name', fallback=self.DEFAULT_CONFIG.get('name'))
        if not name:
            raise NotImplementedError(f"{self.__class__.__name__}.DEFAULT_CONFIG is missing 'name'.")
        return name

    def get_output_path(self) -> Path:
        output_dir = Path(self.config.output_dir)
        if not output_dir.exists():
            os.mkdir(output_dir)
        dir = output_dir / self.get_dir_name()
        if not dir.exists():
            os.mkdir(dir)
        return dir / self.get_file_name()

    def visualize(self, state: State):
        self.frame(state)
        self.frame_id += 1

    @abstractmethod
    def frame(self, state: State):
        pass

    @abstractmethod
    def finish(self):
        pass


class ImageVisualizer(Visualizer):
    def __init__(self, config):
        super().__init__(config)

        file_name = self.get_file_name()
        if isinstance(file_name, str):
            file_name = Path(file_name)
        file_ext = file_name.suffix

        self.logger.debug(f"Got file suffix: {file_ext}")
        self.backend = BackendGenerator.get(file_ext)

    def get_file_name(self) -> str:
        return self.get_pattern() % (self.frame_id)

    def get_scaling(self) -> int:
        scaling = self.config.getint(self.__class__.__name__, 'scaling', fallback=self.DEFAULT_CONFIG.get('scaling'))
        if not scaling:
            raise NotImplementedError(f"{self.__class__.__name__}.DEFAULT_CONFIG is missing 'rate'.")
        return scaling


class VideoVisualizer(ImageVisualizer):
    def get_video(self) -> str:
        return self.config.get(self.__class__.__name__, 'video', fallback=self.DEFAULT_CONFIG.get('video'))

    def get_rate(self) -> int:
        rate = self.config.getint(self.__class__.__name__, 'rate', fallback=self.DEFAULT_CONFIG.get('rate'))
        if not rate:
            raise NotImplementedError(f"{self.__class__.__name__}.DEFAULT_CONFIG is missing 'rate'.")
        return rate

    def finish(self):
        video_name = self.get_video()
        if video_name:
            dir = Path(self.config.output_dir)
            dir = dir / self.get_dir_name()
            generate_video(dir, video_name, self.get_pattern(), self.get_rate())


class PlotVisualizer(Visualizer):
    def __init__(self, config):
        super().__init__(config)
        self.logger.debug(f"PlotVisualizer in da house!!!")
        self.backend = BackendGenerator.get(".plt")

    def get_plot_properties(self):
        props_name = self.config.get(self.__class__.__name__, 'plot_properties', fallback=None)
        if self.config.config.has_section(props_name):
            return self.config.config[props_name]
        return {}

    def get_label_properties(self):
        props_name = self.config.get(self.__class__.__name__, 'label_properties', fallback=None)
        if self.config.config.has_section(props_name):
            return self.config.config[props_name]
        return {}


COLOR_MAP = {
    State.INCOMBUSTIBLE:    [0x23, 0x00, 0x07],
    State.VEGETATION:       [0x60, 0x6C, 0x38], 
    State.HOT:              [0xD2, 0x82, 0x31],
    State.FIRE:             [0xC1, 0x1D, 0x1D], 
}
assert(len(COLOR_MAP) == State.STATESCOUNT)

class CellStateVisualizer(VideoVisualizer):
    DEFAULT_CONFIG = {
        'directory': 'cellstate/',
        'pattern': 'output-%03d.ppm',
        'scaling': 20,
        'video': None,
        'rate': 1,
    }

    def frame(self, state: State):
        width = self.config.width
        height = self.config.height
        scaling = self.get_scaling()
        cell_state = state.cell_state.flatten()
        cell_colors = [COLOR_MAP[x] for x in cell_state]
        self.backend.write(self.get_output_path(), width, height, cell_colors, scaling=scaling)


class FullVisualizer(VideoVisualizer):
    DEFAULT_CONFIG = {
        'directory': 'full/',
        'pattern': 'output-%03d.ppm',
        'scaling': 20,
        'video': None,
        'rate': 1,
    }

    # Base color by state (RGB)
    BASE_COLORS = {
        State.INCOMBUSTIBLE:    [0x23, 0x00, 0x07],
        State.VEGETATION:       [0x60, 0x6C, 0x38], 
        State.HOT:              [0xc9, 0x93, 0x2e],
        State.FIRE:             [0xFF, 0x1D, 0x1D], 
    }

    # Heat LUT for FIRE: aggressive red enhancement
    HEAT_LUT_FIRE = [
        (  0,   0),   # heat 0
        ( 40,  20),
        ( 80,  40),
        (120,  60),
        (160,  80),
        (200, 100),   # heat 5
    ]

    # Heat LUT for HOT: maintain yellow, reduce blue to add intensity
    HEAT_LUT_HOT = [
        (  0,   0),   # heat 0
        ( 10,  15),
        ( 20,  25),
        ( 30,  35),
        ( 40,  45),
        ( 50,  60),   # heat 5
    ]

    # Generic heat LUT for other states
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

        # State-specific heat influence
        if state == State.FIRE:
            add_r, sub_gb = self.HEAT_LUT_FIRE[int(heat)]
        elif state == State.HOT:
            add_r, sub_gb = self.HEAT_LUT_HOT[int(heat)]
        else:
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
        scaling = self.get_scaling()
        # flatten arrays and compute color per cell
        heat_arr = state.heat.flatten()
        fuel_arr = state.fuel.flatten()
        oxy_arr = state.oxygen.flatten()
        st_arr = state.cell_state.flatten()

        cell_colors = [
            self.cell_color(s, h, f, o)
            for h, f, o, s in zip(heat_arr, fuel_arr, oxy_arr, st_arr)
        ]

        self.backend.write(self.get_output_path(), width, height, cell_colors, scaling=scaling)


class HeatPlotVisualizer(PlotVisualizer):
    DEFAULT_CONFIG = {
            'directory': 'plot/',
            'name': 'output.png',
    }

    def __init__(self, config):
        super().__init__(config)
        self.avg_heat = []

    def frame(self, state):
        self.avg_heat.append(np.mean(state.heat))

    def finish(self):
        if isinstance(self.backend, PlotBackend):
            x = [x for x in range(len(self.avg_heat))]
            y = self.avg_heat
            output_path = self.get_output_path()
            self.logger.debug(f"Plot output path: {output_path}")
            self.backend.write(output_path, x, y, x_label="Step", y_label="Avg. heat")
        else:
            logger.error(f"{type(self.backend).__name__} is not a child of PlotBackend.")


class AllAttributePlotVisualizer(PlotVisualizer):
    DEFAULT_CONFIG = {
            'directory': 'allplot/',
            'pattern': 'output-%s.png',
    }

    def __init__(self, config):
        super().__init__(config)
        self.num_fir = []
        self.num_inc = []
        self.num_hot = []
        self.num_veg = []
        self.avg_cell_state = []
        self.avg_heat = []
        self.avg_oxygen = []
        self.avg_fuel = []

    def get_file_name(self):
        return ""

    def frame(self, state):
        self.num_fir.append((state.cell_state == State.FIRE).sum())
        self.num_inc.append((state.cell_state == State.INCOMBUSTIBLE).sum())
        self.num_hot.append((state.cell_state == State.HOT).sum())
        self.num_veg.append((state.cell_state == State.VEGETATION).sum())

        self.avg_cell_state.append(np.mean(state.cell_state))
        self.avg_heat.append(np.mean(state.heat))
        self.avg_oxygen.append(np.mean(state.oxygen))
        self.avg_fuel.append(np.mean(state.fuel))

    def finish(self):
        if isinstance(self.backend, PlotBackend):
            x = [x for x in range(len(self.avg_heat))]
            output_path = self.get_output_path()
            plot_props = self.get_plot_properties()
            label_props = self.get_label_properties()
            self.logger.debug(f"Plot output path: {output_path}")
            self.backend.write(output_path / (self.get_pattern() % ("cell_state")), x, self.avg_cell_state, x_label="Step", y_label="Avg. cell state", labelprops=label_props, **plot_props)
            self.backend.write(output_path / (self.get_pattern() % ("heat")), x, self.avg_heat, x_label="Step", y_label="Avg. heat", labelprops=label_props,**plot_props)
            self.backend.write(output_path / (self.get_pattern() % ("oxygen")), x, self.avg_oxygen, x_label="Step", y_label="Avg. oxygen", labelprops=label_props, **plot_props)
            self.backend.write(output_path / (self.get_pattern() % ("fuel")), x, self.avg_fuel, x_label="Step", y_label="Avg. fuel", labelprops=label_props, **plot_props)

            import matplotlib.pyplot as plt
            plt.figure()
            line_inc, = plt.plot(x, self.num_inc, label="Incombustible")
            line_hot, = plt.plot(x, self.num_hot, label="Hot")
            line_veg, = plt.plot(x, self.num_veg, label="Vegetation")
            line_fir, = plt.plot(x, self.num_fir, label="Fire")
            plt.xlabel("Step", **label_props)
            plt.ylabel("# Cells in State", **label_props)
            plt.legend(handles=[line_fir, line_inc, line_hot, line_veg])
            plt.savefig(output_path / (self.get_pattern() % ("num_states")))

        else:
            logger.error(f"{self.backend.__class__.__name__} is not a child of PlotBackend.")



if __name__ == "__main__":
    conf = Configuration("sim.ini")
    # c = VisualizerContainer(conf)
    c = AllAttributePlotVisualizer(conf)
    print(c.get_dir_name())