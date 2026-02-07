import logging
import matplotlib.pylab as plt
import numpy as np
from abc import ABC, abstractmethod
from config import Configuration
from pathlib import Path
from PIL import Image


class BackendGenerator:
    @classmethod
    def get(cls, ext: str) -> Backend:
        logger = logging.getLogger("BackendGenerator")
        if ext == ".ppm":
            logger.debug(".ppm file format recognized.")
            return PPM()
        elif ext == ".png":
            logger.debug(".png file format recognized.")
            return PNG()
        elif ext == ".plt":
            logger.debug(".plt file format recognized.")
            return PLT()
        else:
            logger.debug("Unrecognized file format {ext}. Using ppm instead.")
            return PPM()


class Backend(ABC):
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)

    @abstractmethod
    def write(self, outfile, *args, **kwargs) -> None:
        pass


class ImageBackend(Backend):
    @abstractmethod
    def write(self, outfile, width: int, height: int, pixels, scaling: int, *args, **kwargs):
        pass


class PlotBackend(Backend):
    @abstractmethod
    def write(self, outfile, x, y, *args, **kwargs):
        pass


class PPM(ImageBackend):
    def write(self, outfile, width: int, height: int, pixels, scaling: int = 60):
        w = width * scaling
        h = height * scaling
        with open(outfile, "w") as f:
            f.write(f'P3\n{w} {h}\n255\n')
            output = ""
            for y in range(0, height):
                line = ""
                for x in range(0, width):
                    ind = y * width + x
                    px_str = [str(x) for x in pixels[ind]]
                    line += (" ".join(px_str) + "\n") * scaling
                output += line*scaling
            f.write(output)


class PNG(ImageBackend):
    def write(self, outfile, width, height, pixels, scaling, *args, **kwargs):
        pixels = np.array(pixels, dtype=np.uint8)
        pixels = np.reshape(pixels, (width, height, 3))
        img = Image.fromarray(pixels, "RGB")
        img = img.resize((width * scaling, height * scaling), resample=Image.Resampling.NEAREST)
        img.save(outfile)


class PLT(PlotBackend):
    def write(self, outfile, x, y, *args, x_label: str= "x", y_label: str = "y", format: str = "PNG", dpi: int = 300, labelprops=None, **kwargs):
        self.logger.debug(f"Output file: {outfile}")
        self.logger.debug(f"Output format: {outfile}")
        plt.figure()
        plt.plot(x, y, *args, **kwargs)
        plt.xlabel(x_label, **labelprops)
        plt.ylabel(y_label, **labelprops)
        plt.grid(True)
        plt.savefig(outfile, format=format, dpi=dpi)