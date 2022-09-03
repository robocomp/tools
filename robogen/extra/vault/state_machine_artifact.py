from schema import Schema, Optional
from .artifact import Artifact

# TODO: avoid redundancy?

class StateMachine(Artifact):
    # TODO: substates
    SCHEMA = Schema({
        'name': str,

        'states': [str],
        'initial_state': str,
        'final_state': str,
        'transitions': [{
            'from': str,
            'to': [str],
        }],
        Optional('substates', default=[]): [{
            'parent': str,
            'states': [str],
            'initial_state': str,
            'final_state': str,
            'transitions': [{
                'from': str,
                'to': [str],
            }],
        }],
    })

    def __init__(self, raw):
        validated = StateMachine.validate(raw)
        super().__init__(validated)
