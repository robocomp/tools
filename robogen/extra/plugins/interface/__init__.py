__name__    = 'interface'
__version__ = '0.1.0'
__author__  = 'José Miguel Sánchez García'

from .parser import IDSLParser
from .artifact import InterfaceArtifact

class Plugin:
    @classmethod
    def install(klass, installer):
        installer.install_parser('idsl', IDSLParser, {'idsl'})
        installer.install_artifact('interface', InterfaceArtifact, markers={'i'}, extensions={'idsl'})
