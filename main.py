import argparse
from config import Configuration
from sim import Simulation
from visual import PPM

def main(config_file: str):
    config = Configuration(config_file)
    sim = Simulation(config)
    sim.run()

    print(config.log_level)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Path to the configuration file (default: sim.ini)", default="sim.ini")
    args = parser.parse_args()

    main(args.config)
