__name__    = 'yaml'
__version__ = '0.1.0'
__author__  = 'José Miguel Sánchez García'

import yaml
import robogen

class YAMLParser(robogen.Parser):
    def parse(self, src):
        return yaml.safe_load(src)

class Plugin:
    @classmethod
    def install(klass, installer):
        installer.install_parser('yaml', YAMLParser, 'yaml')
