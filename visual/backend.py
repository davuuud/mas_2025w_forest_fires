import logging
from abc import ABC, abstractmethod
from config import Configuration
from pathlib import Path

class WriterBackendGenerator:
    @classmethod
    def get(cls, ext: str) -> WriterBackend:
        logger = logging.getLogger("WriterBackendGenerator")
        if ext == "ppm":
            logger.debug("ppm file format recognized.")
            return PPM()
        elif ext == "plt":
            logger.debug("plt file format recognized.")
            return PLT()
        else:
            logger.debug("Unrecognized file format {ext}. Using ppm instead.")
            return PPM()


class WriterBackend(ABC):
    @abstractmethod
    def write(self, outfile, width: int, height: int, pixels, scaling: int):
        pass


class PPM(WriterBackend):
    def write(self, outfile, width: int, height: int, pixels, scaling: int = 60):
        w = width * scaling
        h = height * scaling
        outfile.write(f'P3\n{w} {h}\n255\n')
        output = ""
        for y in range(0, height):
            line = ""
            for x in range(0, width):
                ind = y * width + x
                px_str = [str(x) for x in pixels[ind]]
                line += (" ".join(px_str) + "\n") * scaling
            output += line*scaling
        outfile.write(output)


class PLT(WriterBackend):
    def write(self, outfile, width, height, pixels, scaling):
        print("TODO")