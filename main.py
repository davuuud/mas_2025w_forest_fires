import argparse
import logging
import os
from config import Configuration
from sim import Simulation
from pathlib import Path
from ffmpeg import FFmpeg

logger = logging.getLogger("main")


def generate_video(config: Configuration):
    output_dir = Path(config.output_dir)
    if output_dir.exists() and output_dir.is_dir():
        video_path = output_dir / Path(config.output_video)
        if video_path.exists():
            logger.warning("Deleting existing video {video_path}.")
            os.remove(video_path)
        output_pattern = output_dir / Path(config.output_pattern)
        logger.info("Generating video {video_path} from {output_pattern}.")
        FFmpeg().input(output_pattern).option("r", 1).output(video_path).execute()


def main(config_file: str, seed: int):
    config = Configuration(config_file, seed=seed)

    sim = Simulation(config)
    sim.run(3)

    if config.output_video:
        generate_video(config)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Path to the configuration file (default: sim.ini)", type=str, default="sim.ini")
    parser.add_argument("-d", "--debug", help="Debug mode with the given log level", type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
    parser.add_argument("--seed", help="Seed used for random values", type=int)
    args = parser.parse_args()

    log_level = getattr(logging, args.debug.upper(), logging.INFO)
    logging.basicConfig(filename="sim.log", level=log_level)

    main(args.config, args.seed)
