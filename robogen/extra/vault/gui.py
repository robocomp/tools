__name__    = 'gui'
__version__ = '0.1.0'
__author__  = 'José Miguel Sánchez García'

from schema import Schema, And, Or, Use
from pyparsing import CaselessKeyword, Suppress, Word, alphanums, alphas

GUI = CaselessKeyword('gui')

identifier = Word(alphas + '_', alphanums + '_')

CDSL = (
    Suppress(GUI)
    - identifier('type')
    - Suppress(Word('('))
    - identifier('widget')
    - Suppress(Word(')'))
)

SCHEMA = Schema({
	'type': And(Use(str.lower), 'qt'),
	'widget': Or('QWidget', 'QMainWindow', 'QDialog'),
})

class Plugin:
	'''Automates the generation of GUI.'''

	@classmethod
	def install(klass, manager):
		manager.install_input_element('gui', SCHEMA, cdsl=CDSL)
