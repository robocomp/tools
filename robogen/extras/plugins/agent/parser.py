from functools import reduce
from pyparsing import (
    CaselessKeyword, Group, Optional, QuotedString, Suppress, Word, ZeroOrMore,
    alphanums, alphas, cppStyleComment, pythonStyleComment, delimitedList
)

import robogen

#
# Symbols
#

SC       = Suppress(Word(';'))
OBRACE   = Suppress(Word('{'))
CBRACE   = Suppress(Word('}'))
OBRACKET = Suppress(Word('['))
CBRACKET = Suppress(Word(']'))
OPARENS  = Suppress(Word('('))
CPARENS  = Suppress(Word(')'))
AT       = Word('@')
PIPE     = Word('|')

#
# Keywords
#

IMPORT         = CaselessKeyword('import')
AGENT          = CaselessKeyword('Agent')
LANGUAGE       = CaselessKeyword('Language')
QTDEBUG        = CaselessKeyword('Qtdebug')
APIS           = CaselessKeyword('Apis')
IGNORE_ATTRS   = CaselessKeyword('IgnoreAttrs')
SUBSCRIPTIONS  = CaselessKeyword('Subscriptions')
COMMUNICATIONS = CaselessKeyword('Communications')
ROBOCOMP       = CaselessKeyword('robocomp')
IMPLEMENTS     = CaselessKeyword('implements')
REQUIRES       = CaselessKeyword('requires')
PUBLISHES      = CaselessKeyword('publishes')
SUBSCRIBES_TO  = CaselessKeyword('subscribesTo')

#
# Convenient definitions
#

ident = Word(alphas + '_', alphanums + '_')

#
# Robocomp communication elements
#

comm_robocomp_item = Group(
    ident('name')
    - Optional(ident('type'))
)

comm_robocomp_kind = lambda kw: \
    Suppress(kw) - delimitedList(comm_robocomp_item) - SC

comm_robocomp = Group(
    Suppress(ROBOCOMP)
    - OBRACE
    - (
        Optional(comm_robocomp_kind(IMPLEMENTS)('implements'))
        & Optional(comm_robocomp_kind(REQUIRES)('requires'))
        & Optional(comm_robocomp_kind(PUBLISHES)('publishes'))
        & Optional(comm_robocomp_kind(SUBSCRIBES_TO)('subscribes_to'))
    )
    - CBRACE
    - SC
)

comm_items = lambda ext: \
    Group(reduce(lambda acc, next: acc & next, ext['communications'], Optional(comm_robocomp('robocomp'))))

#
# Agent elements
#

def turn_subs_into_dict(subs):
    CATEGORIES = {
        '@': 'nodes',
        '|': 'edges',
    }

    result = {
        'nodes': [],
        'edges': [],
    }

    for symbol, sub in subs:
        category = CATEGORIES[symbol]
        result[category].append(sub)

    return result

node  = Group(AT   - ident)
edge  = Group(PIPE - ident)
subs  = delimitedList(node | edge).setParseAction(turn_subs_into_dict)

inport         =             Suppress(IMPORT)         - QuotedString('"')                 - SC
language       =             Suppress(LANGUAGE)       - ident                             - SC
qtdebug        =             Suppress(QTDEBUG)                                            - SC
apis           =             Suppress(APIS)           - delimitedList(ident)              - SC
ignore_attrs   =             Suppress(IGNORE_ATTRS)   - delimitedList(ident)              - SC
subscriptions  =             Suppress(SUBSCRIPTIONS)  - subs                              - SC
communications = lambda ext: Suppress(COMMUNICATIONS) - OBRACE - comm_items(ext) - CBRACE - SC

# Things come inside arrays and I don't know why? Ugly hack ahead, beware.
hack = lambda x: x[0]

contents = lambda ext: (
    language('language').setParseAction(hack)
    & Optional(qtdebug.setParseAction(lambda: True)('qtdebug'))
    & Optional(apis('apis'))
    & Optional(ignore_attrs('ignore_attrs'))
    & Optional(subscriptions.setParseAction(hack)('subscriptions'))
    # I don't know why but it needs to be grouped. PyParsing is weird...
    & Optional(Group(communications(ext).setParseAction(hack))('communications'))
)

#
# Top-level parser
#

ADSL = lambda ext: (
    ZeroOrMore(inport)('imports')
    - Suppress(AGENT)
    - ident('name')
    - OBRACE
    # Unpack root extensions
    - reduce(lambda acc, next: acc & next , ext['root'], contents(ext))
    - CBRACE
    - SC
).ignore(cppStyleComment  | pythonStyleComment)

class ADSLParser(robogen.Parser):
    extensions = {
        'root':           set(),
        'communications': set(),
    }

    @classmethod
    def extend_syntax(klass, anchor, syntax):
        klass.extensions[anchor].add(syntax)

    def parse(self, src):
        return ADSL(ADSLParser.extensions).parseString(src).asDict()
