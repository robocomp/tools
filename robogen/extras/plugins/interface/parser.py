from pyparsing import (
    CaselessKeyword, CharsNotIn, Group, Optional, QuotedString, Suppress, Word,
    ZeroOrMore, alphanums, alphas, cppStyleComment, delimitedList,
    pythonStyleComment
)

#
# Keywords
#

DICTIONARY = CaselessKeyword('dictionary')
ENUM       = CaselessKeyword('enum')
EXCEPTION  = CaselessKeyword('exception')
IDEMPOTENT = CaselessKeyword('idempotent')
IMPORT     = CaselessKeyword('import')
INTERFACE  = CaselessKeyword('interface')
MODULE     = CaselessKeyword('module')
OUT        = CaselessKeyword('out')
SEQUENCE   = CaselessKeyword('sequence')
STRUCT     = CaselessKeyword('struct')
THROWS     = CaselessKeyword('throws')

#
# Symbols
#

COMMA   = Suppress(Word(','))
SC      = Suppress(Word(';'))
OBRACE  = Suppress(Word('{'))
CBRACE  = Suppress(Word('}'))
OPARENS = Suppress(Word('('))
CPARENS = Suppress(Word(')'))
LT      = Suppress(Word('<'))
GT      = Suppress(Word('>'))
EQ      = Suppress(Word('='))

ident      = Word(alphas + '_', alphanums + '_')
type_ident = delimitedList(ident, delim='::').setParseAction('::'.join)

inport = (
    Suppress(IMPORT)
    - QuotedString('"')
    - SC
)

member = Group(
    type_ident('type')
    - ident('name')
    - Optional(EQ - CharsNotIn(';')('default_value'))
    - SC
)

struct = Group(
    STRUCT.setParseAction(lambda: 'structs')('category')
    - ident('name')
    - Group(
        OBRACE
        - ZeroOrMore(member)
        - CBRACE
    )('contents')
    - SC
)

dictionary = Group(
    DICTIONARY.setParseAction(lambda: 'dictionaries')('category')
    - Group(
        LT
        - type_ident('from')
        - COMMA
        - type_ident('to')
        - GT
    )('contents')
    - ident('name')
    - SC
)

sequence = Group(
    SEQUENCE.setParseAction(lambda: 'sequences')('category')
    - Group(
        LT
        - ident('type')
        - GT
    )('contents')
    - ident('name')
    - SC
)

enum = Group(
    ENUM.setParseAction(lambda: 'enums')('category')
    - ident('name')
    - Group(
        OBRACE
        - delimitedList(ident)
        - CBRACE
    )('contents')
    - SC
)

exception = Group(
    EXCEPTION.setParseAction(lambda: 'exceptions')('category')
    - ident('name')
    - OBRACE
    - Group(ZeroOrMore(member))('contents')
    - CBRACE
    - SC
)

throws = (
    Suppress(THROWS)
    - delimitedList(type_ident)
)

# TODO: booleans not working?

parameter = Group(
    Optional(OUT.setParseAction(lambda: True))('is_output')
    + type_ident('type')
    + ident('name')
)

remote_method = Group(
    Optional(IDEMPOTENT.setParseAction(lambda: True))('is_idempotent')
    + type_ident('return_type')
    + ident('name')
    + OPARENS
    + Optional(delimitedList(parameter))('params')
    + CPARENS
    + Optional(throws)('throws')
    + SC
)

interface = Group(
    INTERFACE.setParseAction(lambda: 'interfaces')('category')
    - ident('name')
    - OBRACE
    - Group(ZeroOrMore(remote_method))('contents')
    - CBRACE
    - SC
)

contents = Group(ZeroOrMore(
	struct
	| enum
	| exception
	| dictionary
	| sequence
	| interface
))

#
# Top-level parser
#

IDSL = (
    ZeroOrMore(inport)('imports')
    + Suppress(MODULE)
    - ident('name')
    - OBRACE
    - contents('contents')
    - CBRACE
    - SC
).ignore(cppStyleComment | pythonStyleComment)

class IDSLParser:
    def parse(self, src):
        result = IDSL.parseString(src).asDict()

        result['structs']      = {}
        result['enums']        = {}
        result['exceptions']   = {}
        result['dictionaries'] = {}
        result['sequences']    = {}
        result['interfaces']   = {}

        # Rearrange contents
        for item in result['contents']:
            name     = item['name']
            category = item['category']
            contents = item['contents']

            result[category][name] = contents

        del result['contents']

        # Rearrange interface methods
        for name, methods in result['interfaces'].items():
            new_methods = {}

            for method in methods:
                new_methods[method['name']] = method
                del method['name']

            result['interfaces'][name] = new_methods

        return result
