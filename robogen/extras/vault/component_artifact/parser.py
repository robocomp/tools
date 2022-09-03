from functools import reduce
from pyparsing import (
    CaselessKeyword, Group, Optional, QuotedString, Suppress, Word, ZeroOrMore,
    alphanums, alphas, cppStyleComment, delimitedList, pythonStyleComment
)

import robogen

#
# Symbols
#

SC      = Suppress(Word(';'))
OBRACE  = Suppress(Word('{'))
CBRACE  = Suppress(Word('}'))
OPARENS = Suppress(Word('('))
CPARENS = Suppress(Word(')'))

#
# Keywords
#

COMMUNICATIONS = CaselessKeyword('communications')
COMPONENT      = CaselessKeyword('component')
IMPLEMENTS     = CaselessKeyword('implements')
IMPORT         = CaselessKeyword('import')
LANGUAGE       = CaselessKeyword('language')
OPTIONS        = CaselessKeyword('options')
PUBLISHES      = CaselessKeyword('publishes')
REQUIRES       = CaselessKeyword('requires')
SUBSCRIBES_TO  = CaselessKeyword('subscribesTo')

identifier = Word(alphas + '_', alphanums + '_')
inport     = Suppress(IMPORT) - QuotedString('"') - SC
comm_type  = OPARENS - identifier - CPARENS

comm = Group(
    identifier('name')
    + Optional(comm_type('type'))
)

implements    = Suppress(IMPLEMENTS)    - delimitedList(comm) - SC
requires      = Suppress(REQUIRES)      - delimitedList(comm) - SC
subscribes_to = Suppress(SUBSCRIBES_TO) - delimitedList(comm) - SC
publishes     = Suppress(PUBLISHES)     - delimitedList(comm) - SC

communication_list = (
    Optional(implements('implements'))
    & Optional(requires('requires'))
    & Optional(subscribes_to('suscribes_to'))
    & Optional(publishes('publishes'))
)

communications = Group(
    Suppress(COMMUNICATIONS)
    - OBRACE
    - communication_list
    - CBRACE
    - SC
)

language = Suppress(LANGUAGE) - identifier - SC

options = Suppress(OPTIONS) - delimitedList(identifier) - SC

# TODO: things come in arrays and I don't know why? Ugly hack ahead, beware.

contents = (
    communications.setParseAction(lambda x: x[0])
    & language('language').setParseAction(lambda x: x[0])
    & Optional(options('options'))
)

#
# Top-level parser
#

CDSL = lambda ext: (
    ZeroOrMore(inport)('imports')
    - Suppress(COMPONENT)
    - identifier('name')
    - OBRACE
    # Unpack extensions
    - reduce(lambda acc, next: acc & create_item(*next) , ext.items(), contents)
    - CBRACE
    - SC
).ignore(cppStyleComment | pythonStyleComment)

class CDSLParser(robogen.Parser):
    extensions = {
        'root': set(),
    }

    @classmethod
    def extend_syntax(klass, anchor, syntax):
        klass.extensions[anchor].add(syntax)

    def parse(self, src):
        return CDSL(CDSLParser.extensions).parseString(src).asDict()
