import configparser
import logging

class Configuration:
    DEFAULTS = {
        'preset': {
            'source': 'random',
            #'seed': 123,
            'file': None,
        },
        'simulation': {
            'size': 10,
            'seed': 123,
            'neighborhood' : 'NeumannNeighborhood',
            'rules': 'DecreaseWhenFireRule',
        },
        'output': {
            'visualizers': 'PPMCellStateVisualizer',
            'directory': 'out/',
            'pattern': 'output-%%03d',
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
        self.seed = seed if seed else self.config.getint('simulation', 'seed', fallback=self.DEFAULTS['simulation']['seed'])
        logger.debug(f"config.width = {self.width}")
        logger.debug(f"config.height = {self.height}")
        logger.debug(f"config.seed = {self.seed}")

        ## Preset settings
        self.preset_source = self.config.get('preset', 'source', fallback=self.DEFAULTS['preset']['source'])
        #self.preset_seed = self.config.getint('preset', 'seed', fallback=self.DEFAULTS['preset']['seed'])
        self.preset_file = self.config.get('preset', 'file', fallback=self.DEFAULTS['preset']['file'])
        logger.debug(f"config.preset_source = {self.preset_source}")
        #logger.debug(f"config.preset_seed = {self.preset_seed}")
        logger.debug(f"config.preset_file = {self.preset_file}")

        ## Neighborhood and rules
        self.neighborhood= self.config.get('simulation', 'neighborhood', fallback=self.DEFAULTS['simulation']['neighborhood'])
        self.rules = self.config.get('simulation', 'rules', fallback=self.DEFAULTS['simulation']['rules']).split(' ')
        logger.debug(f"config.neighborhood = {self.neighborhood}")
        logger.debug(f"config.rules = {self.rules}")

        # Visulization settings
        self.visualizers = self.config.get('output', 'visualizers', fallback=self.DEFAULTS['output']['visualizers']).split(' ')
        self.output_dir = self.config.get('output', 'directory', fallback=self.DEFAULTS['output']['directory'])
        self.output_pattern = self.config.get('output', 'pattern', fallback=self.DEFAULTS['output']['pattern'])
        logger.debug(f"config.visualizers = {self.visualizers}")
        logger.debug(f"config.output_dir = {self.output_dir}")
        logger.debug(f"config.output_pattern = {self.output_pattern}")

    def __str__(self) -> str:
        return (
            'Configuration('
            f'width={self.width}, '
            f'height={self.height}, '
            f'seed={self.seed}, '
            f'preset_source={self.preset_source}, '
            #f'preset_seed={self.preset_seed}, '
            f'preset_file={self.preset_file}, '
            f'neighborhood={self.neighborhood}, '
            f'rules={self.rules}, '
            f'visualizers={self.visualizers}, '
            f'output_dir={self.output_dir}, '
            f'output_pattern={self.output_pattern}'
            ')'
        )