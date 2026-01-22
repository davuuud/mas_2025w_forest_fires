import argparse
import logging
from config import Configuration
from sim import Simulation
from pathlib import Path
from ffmpeg import FFmpeg

logger = logging.getLogger("main")

def main(config_file: str, seed: int):
    config = Configuration(config_file, seed=seed)
    sim = Simulation(config)
    sim.run(3)

    if config.output_video:
        output_dir = Path(config.output_dir)
        if output_dir.exists() and output_dir.is_dir():
            first_file = next(output_dir.iterdir(), None)
            output_pattern = Path(config.output_pattern).with_suffix(first_file.suffix)
            FFmpeg().input(output_dir / output_pattern).option("r", 1).output(output_dir / Path(config.output_video)).execute()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Path to the configuration file (default: sim.ini)", type=str, default="sim.ini")
    parser.add_argument("-d", "--debug", help="Debug mode with the given log level", type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
    parser.add_argument("--seed", help="Seed used for random values", type=int)
    args = parser.parse_args()

    log_level = getattr(logging, args.debug.upper(), logging.INFO)
    logging.basicConfig(filename="sim.log", level=log_level)

    main(args.config, args.seed)
