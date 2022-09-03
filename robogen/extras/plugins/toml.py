__name__    = 'toml'
__version__ = '0.1.0'
__author__  = 'José Miguel Sánchez García'

import toml
import robogen

class TOMLParser(robogen.Parser):
    def parse(self, src):
        return toml.loads(src)

class Plugin:
    @classmethod
    def install(klass, installer):
        installer.install_parser('toml', TOMLParser, 'toml')
