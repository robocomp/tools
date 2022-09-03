from schema import Schema, Optional
from .artifact import Artifact

class Module(Artifact):
    SCHEMA = Schema({
        'name': str,
        Optional('imports', default=[]): [str],
        Optional('sequences', default={}): {
            Optional(str): {
                'type': str,
            },
        },
        Optional('dictionaries', default={}): {
            Optional(str): {
                'from': str,
                'to':   str,
            },
        },
        Optional('enums', default={}): {
            Optional(str): [str],
        },
        Optional('exceptions', default={}): {
            Optional(str): [{
                'name': str,
                'type': str,
            }],
        },
        Optional('interfaces', default={}): {
            Optional(str): {
                Optional(str): {
                    Optional('return_type', default='void'): str,
                    Optional('is_idempotent', default=False): bool,
                    Optional('params', default=[]): [{
                        'name': str,
                        'type': str,
                        Optional('is_output', default=False): bool,
                    }],
                }
            },
        },
        Optional('structs', default={}): {
            Optional(str): [{
                'name': str,
                'type': str,
                Optional('default_value'): str,
            }],
        },
    })

    def __init__(self, raw):
        validated = Module.validate(raw)
        super().__init__(validated)
