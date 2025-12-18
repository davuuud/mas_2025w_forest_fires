import configparser

class Configuration:
    DEFAULTS = {
        'debug': {
            'log_level': 0
        },
        'preset': {
            'source': 'random',
            'file': None
        },
        'simulation': {
            'size': 10
        },
        'output': {
            'directory': 'out/',
            'pattern': 'output-%03d'
        }
    }

    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.debug = 'debug' in self.config
        self.log_level = self.config.getint('debug', 'log_level', fallback=self.DEFAULTS['debug']['log_level'])

        self.preset_source = self.config.get('preset', 'source', fallback=self.DEFAULTS['preset']['source'])
        self.preset_file = self.config.get('preset', 'file', fallback=self.DEFAULTS['preset']['file'])

        size = self.config.get('simulation', 'size', fallback=self.DEFAULTS['simulation']['size'])
        self.width = self.config.get('simulation', 'width', fallback=size)
        self.height = self.config.get('simulation', 'height', fallback=size)

        self.output_dir = self.config.get('output', 'directory', fallback=self.DEFAULTS['output']['directory'])
        self.output_pattern = self.config.get('output', 'pattern', fallback=self.DEFAULTS['output']['pattern'])

    def __str__(self) -> str:
        debug = 'debug, ' if self.debug else ''
        return f'Configuration({debug}width={self.width}, height={self.height})'