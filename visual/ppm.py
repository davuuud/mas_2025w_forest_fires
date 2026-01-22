class PPM:
    @classmethod
    def write_ppm(cls, outfile, width: int, height: int, pixels, scaling: int = 60):
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
