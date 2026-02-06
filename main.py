import argparse
import logging
import os
import shutil
import sys
from config import Configuration
from sim.simulation import Simulation
from pathlib import Path

logger = logging.getLogger("main")

YES = ["y", "yes", "yay", "ja", "jawohl", "yeah", "yessir", "jup"]
NO = ["n", "no", "nay", "nein", "niemals", "nope", "never"]


def yes_no_prompt(question: str) -> bool:
    response = input(question + " (y/N): ").strip().lower()
    if response in YES:
        return True
    return False


def main(config_file: str, seed: int):
    config = Configuration(config_file, seed=seed)

    output_dir = Path(config.output_dir)
    if output_dir.exists():
        if output_dir.is_dir():
            if yes_no_prompt(f"Output directory '{output_dir.absolute()}' does already exist. Delete?"):
                print("Deleted :)")
                shutil.rmtree(output_dir)
            else:
                print("Okidoki. But I don't want to simulate anymore :'(")
                exit(0)
        else:
            print("Error: '{output_dir.absolute()}' exists and is not a directory.", file=sys.stderr)
            exit(1)

    logger.debug("Starting simulation")
    sim = Simulation(config)
    sim.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Path to the configuration file (default: sim.ini)", type=str, default="sim.ini")
    parser.add_argument("-d", "--debug", help="Debug mode with the given log level", type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
    parser.add_argument("--seed", help="Seed used for random values", type=int)
    args = parser.parse_args()

    log_level = getattr(logging, args.debug.upper(), logging.INFO)
    logging.basicConfig(filename="sim.log", level=log_level)

    main(args.config, args.seed)
