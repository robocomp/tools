__name__    = 'state_machine'
__version__ = '0.1.0'
__author__  = 'José Miguel Sánchez García'

from pyparsing import CaselessKeyword, Optional as ParserOptional, QuotedString, Suppress
from schema import Schema, Optional as SchemaOptional

STATE_MACHINE = CaselessKeyword('statemachine')
VISUAL        = CaselessKeyword('visual')

CDSL = (
	Suppress(STATE_MACHINE)
	- QuotedString('"')('path')
	- ParserOptional(VISUAL('is_visual').setParseAction(lambda: True))
)

SCHEMA = Schema({
	'path': str,
	SchemaOptional('is_visual', default=False): bool,
})

class Plugin:
	'''Automates the generation of state machines.'''

	@classmethod
	def install(klass, manager):
		manager.install_input_element('state_machine', SCHEMA, cdsl=CDSL)
