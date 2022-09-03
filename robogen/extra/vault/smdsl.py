from pyparsing import (
    CaselessKeyword, CaselessLiteral, Group, Optional, ZeroOrMore, Suppress,
    Word, alphanums, alphas, delimitedList, cppStyleComment,
    pythonStyleComment
)

#
# Keywords
#

TRANSITIONS   = CaselessKeyword('transitions')
INITIAL_STATE = CaselessKeyword('initial_state')
END_STATE     = CaselessKeyword('end_state')
STATES        = CaselessKeyword('states')
PARALLEL      = CaselessKeyword('parallel')

#
# Symbols
#

SC     = Suppress(Word(';'))
OBRACE = Suppress(Word('{'))
CBRACE = Suppress(Word('}'))
TO     = Suppress(CaselessLiteral('=>') | CaselessLiteral('⇒'))

identifier = Word(alphas + '_', alphanums + '_')

states = (
    Suppress(STATES)
    - delimitedList(identifier)
    - SC
)

transition = Group(
    identifier('from')
    + TO
    - delimitedList(identifier)('to')
    - SC
)

transitions = (
    Suppress(TRANSITIONS)
    - OBRACE
    - ZeroOrMore(transition)
    - CBRACE
    - SC
)

initial_state = Suppress(INITIAL_STATE) - identifier - SC
final_state   = Suppress(END_STATE)     - identifier - SC

# TODO: things come in arrays and I don't know why? Ugly hack ahead, beware.

contents = (
    states('states')
    & initial_state('initial_state').setParseAction(lambda x: x[0])
    & final_state('final_state').setParseAction(lambda x: x[0])
    & transitions('transitions')
)

parent = Suppress(Word(':')) + identifier

substate = (
    parent('parent')
    - Optional(PARALLEL('parallel').setParseAction(lambda: True))
    - OBRACE
    - contents
    - CBRACE
    - SC
)

#
# Top-level parser
#

SMDSL = (
    identifier('name')
    - OBRACE
    - contents
    - CBRACE
    - SC
    - Group(ZeroOrMore(substate))('substates')
).ignore(cppStyleComment | pythonStyleComment)

class SMDSLParser:
    def parse(self, src):
        return SMDSL.parseString(src).asDict()
