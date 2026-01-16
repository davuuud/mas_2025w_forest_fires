from .visualizer import Visualizer

class PPM(Visualizer):
    @classmethod
    def write_ppm(cls, outfile, width, height, pixels):
        outfile.write(f'P3\n{width} {height}\n')
        for pixel in pixels:
            outfile.write(" ".join(pixel))
