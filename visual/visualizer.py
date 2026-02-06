import inspect
import logging
import os
import sys
from abc import ABC, abstractmethod
from ffmpeg import FFmpeg
from pathlib import Path
from config import Configuration
from sim.state import State

from .backend import WriterBackendGenerator

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
        self.frames: list[State] = []

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
        self.frames.append(state)
        for vis in self.visualizers:
            vis.visualize(state)

    def finish(self) -> None:
        for vis in self.visualizers:
            vis.finish(self.frames)
    

class Visualizer(ABC):
    def __init__(self, config: Configuration):
        self.config = config 
        self.frame_id = 0
        file_ext = self.get_file_name().suffix
        self.backend = WriterBackendGenerator.get(file_ext)

    def get_output_path(self):
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
    def get_dir_name(self) -> Path:
        pass

    @abstractmethod
    def get_file_name(self) -> Path:
        pass

    @abstractmethod
    def frame(self, state: State):
        pass

    @abstractmethod
    def finish(self, frames: list[State]):
        pass


COLOR_MAP = {
    State.INCOMBUSTIBLE:    [0x23, 0x00, 0x07],
    State.VEGETATION:       [0x60, 0x6C, 0x38], 
    State.HOT:              [0xD2, 0x82, 0x31],
    State.FIRE:             [0xC1, 0x1D, 0x1D], 
}
assert(len(COLOR_MAP) == State.STATESCOUNT)

class CellStateVisualizer(Visualizer):
    NAME = 'CellStateVisualizer'
    DEFAULT_CONFIG = {
        'directory': 'cellstate/',
        'pattern': 'output-%03d.ppm',
        'scaling': 20,
        'video': None,
        'rate': 1,
    }

    def get_pattern(self) -> str:
        pattern = self.config.get(self.NAME, 'pattern', fallback=self.DEFAULT_CONFIG['pattern'])
        return pattern

    def get_video(self) -> str:
        video = self.config.get(self.NAME, 'video', fallback=self.DEFAULT_CONFIG['video'])
        return video

    def get_rate(self) -> int:
        rate = self.config.getint(self.NAME, 'rate', fallback=self.DEFAULT_CONFIG['rate'])
        return rate

    def get_dir_name(self):
        dir = self.config.get(self.NAME, 'directory', fallback=self.DEFAULT_CONFIG['directory'])
        return Path(dir)

    def get_file_name(self) -> Path:
        return Path(self.get_pattern() % (self.frame_id))

    def frame(self, state: State):
        width = self.config.width
        height = self.config.height
        scaling = self.config.getint(self.NAME, 'scaling', fallback=self.DEFAULT_CONFIG['scaling'])
        cell_state = state.cell_state.flatten()
        cell_colors = [COLOR_MAP[x] for x in cell_state]
        with open(self.get_output_path(), "w") as outfile:
            self.backend.write(outfile, width, height, cell_colors, scaling=scaling)

    def finish(self, frames):
        video_name = self.get_video()
        if video_name:
            dir = Path(self.config.output_dir)
            dir = dir / self.get_dir_name()
            generate_video(dir, video_name, self.get_pattern(), self.get_rate())


class FullVisualizer(Visualizer):
    NAME = 'FullVisualizer'
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

    def get_pattern(self) -> str:
        pattern = self.config.get(self.NAME, 'pattern', fallback=self.DEFAULT_CONFIG['pattern'])
        return pattern

    def get_video(self) -> str:
        video = self.config.get(self.NAME, 'video', fallback=self.DEFAULT_CONFIG['video'])
        return video

    def get_rate(self) -> int:
        rate = self.config.getint(self.NAME, 'rate', fallback=self.DEFAULT_CONFIG['rate'])
        return rate

    def get_dir_name(self) -> Path:
        dir = self.config.get(self.NAME, 'directory', fallback=self.DEFAULT_CONFIG['directory'])
        return Path(dir)

    def get_file_name(self) -> Path:
        return Path(self.get_pattern() % (self.frame_id))

    def frame(self, state: State):
        width = self.config.width
        height = self.config.height
        scaling = self.config.getint(self.NAME, 'scaling', fallback=self.DEFAULT_CONFIG['scaling'])
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
            self.backend.write(outfile, width, height, cell_colors, scaling=scaling)

    def finish(self, frames):
        video_name = self.get_video()
        if video_name:
            dir = Path(self.config.output_dir)
            dir = dir / self.get_dir_name()
            generate_video(dir, video_name, self.get_pattern(), self.get_rate())


class PlotVisualizer(Visualizer):
    NAME = 'PlotVisualizer'
    DEFAULT_CONFIG = {
            'directory': 'plot/',
            'name': 'output.plt',
    }

    def get_dir_name(self):
        dir = self.config.get(self.NAME, 'directory', fallback=self.DEFAULT_CONFIG['directory'])
        return Path(dir)

    def get_file_name(self) -> Path:
        name = self.config.get(self.NAME, 'name', fallback=self.DEFAULT_CONFIG['name'])
        return Path(name)

    def frame(self, state):
        pass

    def finish(self, frames: list[State]):
        print(self.get_output_path())
        print(len(frames))


if __name__ == "__main__":
    conf = Configuration("sim.ini")
    c = VisualizerContainer(conf)