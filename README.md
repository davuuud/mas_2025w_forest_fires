# Fire Spreading
The group project "Fire Spreading" for the Modeling and Simulation 2025W course.

## Installation
It is generaly recommended to let [uv](https://docs.astral.sh/uv/) take care of it for you.

```
uv run main.py
```

If the `video` configuration is used, i.e. if a video as output is expected, FFmpeg needs to be installed and available on the path.
If you have no desire to generate videos, just remove the `video` from the used visualizer in `sim.ini`.