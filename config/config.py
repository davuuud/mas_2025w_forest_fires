import configparser
import logging

class Configuration:
    DEFAULTS = {
        'preset': {
            'source': 'random',
            'file': None,
        },
        'simulation': {
            'size': 10,
            'steps': 5,
            'seed': 123,
            'neighborhood' : 'NeumannNeighborhood',
            'rules': 'DecreaseWhenFireRule',
            'rule_approach': 'general',
            # thresholds and probabilities for CellOnFireRule
            'threshold_sum': 8,
            't_heat': 3,
            't_fuel': 1,
            't_oxygen': 1,
            'pb': 0.05,
            'po': 0.10,
        },
        'output': {
            'visualizers': 'CellStateVisualizer',
            'directory': 'out/',
            'pattern': 'output-%03d.ppm',
            'scaling': 50
        }
    }

    def __init__(self, config_file, seed=None):
        logger = logging.getLogger("Configuration")

        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        logger.info(f"Finished reading {config_file}")

        # Simulation settings
        size = self.config.getint('simulation', 'size', fallback=self.DEFAULTS['simulation']['size'])
        self.width = self.config.getint('simulation', 'width', fallback=size)
        self.height = self.config.getint('simulation', 'height', fallback=size)
        self.steps = self.config.getint('simulation', 'steps', fallback=self.DEFAULTS['simulation']['steps'])
        self.seed = seed if seed else self.config.getint('simulation', 'seed', fallback=self.DEFAULTS['simulation']['seed'])
        logger.debug(f"config.width = {self.width}")
        logger.debug(f"config.height = {self.height}")
        logger.debug(f"config.steps = {self.steps}")
        logger.debug(f"config.seed = {self.seed}")

        ## Preset settings
        self.preset_source = self.config.get('preset', 'source', fallback=self.DEFAULTS['preset']['source'])
        self.preset_file = self.config.get('preset', 'file', fallback=self.DEFAULTS['preset']['file'])
        logger.debug(f"config.preset_source = {self.preset_source}")
        logger.debug(f"config.preset_file = {self.preset_file}")

        ## Neighborhood and rules
        self.neighborhood= self.config.get('simulation', 'neighborhood', fallback=self.DEFAULTS['simulation']['neighborhood'])
        self.rules = self.config.get('simulation', 'rules', fallback=self.DEFAULTS['simulation']['rules']).split(' ')
        # new: rule approach (one of: general, individual, stochastic)
        self.rule_approach = self.config.get('simulation', 'rule_approach', fallback=self.DEFAULTS['simulation']['rule_approach'])
        # thresholds and probabilities for CellOnFireRule
        self.threshold_sum = self.config.getint('simulation', 'threshold_sum', fallback=self.DEFAULTS['simulation']['threshold_sum'])
        self.t_heat = self.config.getint('simulation', 't_heat', fallback=self.DEFAULTS['simulation']['t_heat'])
        self.t_fuel = self.config.getint('simulation', 't_fuel', fallback=self.DEFAULTS['simulation']['t_fuel'])
        self.t_oxygen = self.config.getint('simulation', 't_oxygen', fallback=self.DEFAULTS['simulation']['t_oxygen'])
        self.pb = self.config.getfloat('simulation', 'pb', fallback=self.DEFAULTS['simulation']['pb'])
        self.po = self.config.getfloat('simulation', 'po', fallback=self.DEFAULTS['simulation']['po'])

        logger.debug(f"config.neighborhood = {self.neighborhood}")
        logger.debug(f"config.rules = {self.rules}")
        logger.debug(f"config.rule_approach = {self.rule_approach}")
        logger.debug(f"config.threshold_sum = {self.threshold_sum}")
        logger.debug(f"config.t_heat = {self.t_heat}")
        logger.debug(f"config.t_fuel = {self.t_fuel}")
        logger.debug(f"config.t_oxygen = {self.t_oxygen}")
        logger.debug(f"config.pb = {self.pb}")
        logger.debug(f"config.po = {self.po}")

        # Visulization settings
        self.visualizers = self.config.get('output', 'visualizers', fallback=self.DEFAULTS['output']['visualizers']).split(' ')
        self.output_dir = self.config.get('output', 'directory', fallback=self.DEFAULTS['output']['directory'])
        self.output_pattern = self.config.get('output', 'pattern', fallback=self.DEFAULTS['output']['pattern'])
        self.output_scaling = self.config.getint('output', 'scaling', fallback=self.DEFAULTS['output']['scaling'])
        self.output_video = self.config.get('output', 'video', fallback=None)
        logger.debug(f"config.visualizers = {self.visualizers}")
        logger.debug(f"config.output_dir = {self.output_dir}")
        logger.debug(f"config.output_pattern = {self.output_pattern}")
        logger.debug(f"config.output_scaling = {self.output_scaling}")
        logger.debug(f"config.output_video = {self.output_video}")

    def __str__(self) -> str:
        return (
            'Configuration('
            f'width={self.width}, '
            f'height={self.height}, '
            f'seed={self.seed}, '
            f'preset_source={self.preset_source}, '
            f'preset_file={self.preset_file}, '
            f'neighborhood={self.neighborhood}, '
            f'rules={self.rules}, '
            f'rule_approach={self.rule_approach}, '
            f'threshold_sum={self.threshold_sum}, '
            f't_heat={self.t_heat}, '
            f't_fuel={self.t_fuel}, '
            f't_oxygen={self.t_oxygen}, '
            f'pb={self.pb}, '
            f'po={self.po}, '
            f'visualizers={self.visualizers}, '
            f'output_dir={self.output_dir}, '
            f'output_pattern={self.output_pattern}'
            ')'
        )