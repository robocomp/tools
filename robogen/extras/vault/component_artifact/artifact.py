from schema import Schema, And, Or, Optional, Use
import robogen
import os

COMM_ITEM = Schema({
    'name': str,
    Optional('type', default='ice'): And(Use(str.lower), Or('ros', 'ice')),
})

class ComponentArtifact(robogen.Artifact):
    options    = set()
    extensions = {
        'root': {}
    }

    @classmethod
    def schema(klass):
        return Schema({
            'name': str,
            'language': str,
            Optional('imports',       default=[]): [str],
            Optional('options',       default=[]): [And(Use(str.lower), Or(*klass.options))],
            Optional('implements',    default=[]): [COMM_ITEM],
            Optional('requires',      default=[]): [COMM_ITEM],
            Optional('publishes',     default=[]): [COMM_ITEM],
            Optional('subscribes_to', default=[]): [COMM_ITEM],

            # Unpack extensions
            **{keyword: schema for keyword, schema in klass.extensions['root'].items()}
        })

    @classmethod
    def extend_schema(klass, anchor, keyword, schema):
        klass.extensions[anchor][keyword] = schema

    def __init__(self, raw):
        super().__init__(raw)

        self.name     = self.tree['name']
        self.language = self.tree['language']
        self.options  = [option.lower for option in self.tree['options']]
        self.imports  = [*map(os.path.basename, sorted(self.tree['imports']))]
        self.recursive_imports = []

        self.interfaces    = {'ros': [], 'ice': []}
        self.implements    = []
        self.requires      = []
        self.publishes     = []
        self.subscribes_to = []
        self.using_ros     = False

        for comm_type in {'implements', 'requires', 'publishes', 'subscribes_to'}:
            if comm_type not in self.tree:
                continue

            for interface in sorted(self.tree[comm_type], key=lambda comm: comm['name']):
                getattr(self, comm_type).append(interface['name'])
                self.interfaces[interface['type']].append(interface)
