__name__    = 'component_artifact'
__version__ = '0.1.0'
__author__  = 'José Miguel Sánchez García'

from .parser import CDSLParser
from .artifact import ComponentArtifact

class Plugin:
	@classmethod
	def install(klass, installer):
		installer.install_parser('cdsl', CDSLParser, {'cdsl'})
		installer.install_artifact('component', ComponentArtifact, markers={'c'}, extensions={'cdsl'})
