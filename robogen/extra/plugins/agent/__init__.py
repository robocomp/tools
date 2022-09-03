__name__    = 'agent'
__version__ = '0.1.0'
__author__  = 'José Miguel Sánchez García'

from .parser import ADSLParser
from .artifact import AgentArtifact

class Plugin:
    @classmethod
    def install(klass, installer):
        installer.install_parser('adsl', ADSLParser, {'adsl'})
        installer.install_artifact('agent', AgentArtifact, markers={'a'}, extensions={'adsl'})
