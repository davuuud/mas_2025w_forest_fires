class PPM:
    @classmethod
    def write_ppm(cls, outfile, width, height, pixels):
        w = width * 60
        h = height * 60
        outfile.write(f'P3\n{w} {h}\n255\n')
        for y in range(0, h):
            for x in range(0, w):
                ind = int(y/60) + int(x/60)
                px_str = [str(x) for x in pixels[ind]]
                outfile.write(" ".join(px_str) + "\n")
