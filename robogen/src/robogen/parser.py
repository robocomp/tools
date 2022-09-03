import json

from abc import ABC, abstractmethod

class Parser(ABC):
    '''Turn an input string into a dictionary-backed syntax tree.'''

    @classmethod
    def extend_syntax(klass, anchor, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def parse(self, src):
        pass

class JSONParser(Parser):
    def parse(self, src):
        return json.loads(src)

class ParserManager:
    '''Middleware which takes care of finding and adding parsers.'''
    parsers = {
        # Base JSON syntax
        'json': JSONParser,
    }

    extensions = {
        # Base JSON syntax
        'json': JSONParser
    }

    @classmethod
    def add_parser(klass, name, parser, extensions={}):
        klass.parsers[name] = parser
        klass.extensions.update({extension: parser for extension in extensions})

    @classmethod
    def find_parser_by_name(klass, name):
        return klass.parsers.get(name)

    @classmethod
    def find_parser_by_extension(klass, extension):
        return klass.parsers.get(extension)
