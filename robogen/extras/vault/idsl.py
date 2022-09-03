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
EXCEPTION  = CaselessKeyword('enum')
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

identifier = Word(alphas + '_', alphanums + '_')
type_identifier = delimitedList(identifier, delim='::').setParseAction('::'.join)

inport = (
    Suppress(IMPORT)
    - QuotedString('"')
    - SC
)

member = Group(
    type_identifier('type')
    + identifier('name')
    + Optional(EQ - CharsNotIn(';')('default_value'))
    + SC
)

struct = Group(
    STRUCT.setParseAction(lambda: 'structs')('category')
    - identifier('name')
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
        - type_identifier('from')
        - COMMA
        - type_identifier('to')
        - GT
    )('contents')
    - identifier('name')
    - SC
)

sequence = Group(
    SEQUENCE.setParseAction(lambda: 'sequences')('category')
    - Group(
        LT
        - identifier('type')
        - GT
    )('contents')
    - identifier('name')
    - SC
)

enum = Group(
    ENUM.setParseAction(lambda: 'enums')('category')
    - identifier('name')
    - Group(
        OBRACE
        - delimitedList(identifier)
        - CBRACE
    )('contents')
    - SC
)

exception = Group(
    EXCEPTION.setParseAction(lambda: 'exceptions')('category')
    - identifier('name')
    - Group(
        OBRACE
        - ZeroOrMore(member)
        - CBRACE
    )('contents')
    - SC
)

throws = (
    Suppress(THROWS)
    - delimitedList(identifier)
)

# TODO: booleans not working?

parameter = Group(
    Optional(OUT.setParseAction(lambda: True))('is_output')
    + type_identifier('type')
    + identifier('name')
)

remote_method = Group(
    Optional(IDEMPOTENT.setParseAction(lambda: True))('is_idempotent')
    + type_identifier('return_type')
    + identifier('name')
    + OPARENS
    + Optional(delimitedList(parameter))('params')
    + CPARENS
    + Optional(throws)('throws')
    + SC
)

interface = Group(
    INTERFACE.setParseAction(lambda: 'interfaces')('category')
    - identifier('name')
    - Group(
        OBRACE
        + ZeroOrMore(remote_method)
        + CBRACE
    )('contents')
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
    - identifier('name')
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
