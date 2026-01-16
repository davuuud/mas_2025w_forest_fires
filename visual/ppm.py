class PPM:
    @classmethod
    def write_ppm(cls, outfile, width: int, height: int, pixels, scaling: int = 60):
        w = width * scaling
        h = height * scaling
        outfile.write(f'P3\n{w} {h}\n255\n')
        for y in range(0, h):
            for x in range(0, w):
                ind = y//scaling + x//scaling
                px_str = [str(x) for x in pixels[ind]]
                outfile.write(" ".join(px_str) + "\n")
