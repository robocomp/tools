from .parser import ParserManager
from sys import exit, stderr
import os
import traceback

class Artifact:
    '''Entity which conforms to certain rules and can generate some output.'''

    def __init__(self, raw, importer):
        self.tree = self.__class__.validate(raw)

        if hasattr(self.__class__, 'ctor_extensions'):
            for function in self.__class__.ctor_extensions:
                function(self, importer)

    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def extend_schema(klass, anchor, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def extend_ctor(klass, function):
        if not hasattr(klass, 'ctor_extensions'):
            setattr(klass, 'ctor_extensions', [])
        klass.ctor_extensions.insert(0, function)

    @classmethod
    def schema(klass):
        return klass.SCHEMA

    @classmethod
    def validate(klass, raw):
        return klass.schema().validate(raw)

class ArtifactManager:
    '''Middleware which takes care of finding and adding artifacts.'''

    artifacts  = {}
    markers    = {}
    extensions = {}

    @staticmethod
    def analyze_extension(filename):
        '''Extract parser and artifact from file name extension.'''

        parts    = filename.rsplit('.', maxsplit=2)
        parser   = None
        artifact = None

        if len(parts) == 2:   # filename.x
            parser   = ParserManager.find_parser_by_extension(parts[-1])
            artifact = ArtifactManager.find_artifact_by_marker(parts[-1])
        elif len(parts) == 3: # filename.x.y
            parser   = ParserManager.find_parser_by_extension(parts[-1])
            artifact = ArtifactManager.find_artifact_by_extension(parts[-2])

        return artifact, parser

    @classmethod
    def load_artifact(klass, input_file, importer=None):
        with open(input_file) as f:
            src = f.read()

        filename = os.path.basename(input_file)
        artifact, parser = ArtifactManager.analyze_extension(filename)

        if not importer:
            importer = ImportManager()

        try:
            return artifact(parser().parse(src), importer)
        except:
            traceback.print_exc()
            print(f"🛑 Error parsing `{input_file}'!", file=stderr)
            exit(-1)

    @classmethod
    def find_artifact_by_name(klass, name):
        return klass.artifacts.get(name)

    @classmethod
    def add_artifact(klass, name, artifact, markers={}, extensions={}):
        klass.artifacts[name] = artifact
        klass.markers.update({marker: artifact for marker in markers})
        klass.markers.update({extension: artifact for extension in extensions})

    @classmethod
    def find_artifact_by_marker(klass, marker):
        return klass.markers.get(marker)

    @classmethod
    def find_artifact_by_extension(klass, extension):
        return klass.markers.get(extension)

class ImportManager:
    import_paths = []

    @classmethod
    def add_path(klass, path):
        klass.import_paths.insert(0, path)

    def __init__(self, parent=None):
        self.parent    = parent
        self.cache     = parent.cache if parent else {}
        self.artifacts = {}
        self.branches  = set()

    def __iter__(self):
        return iter(self.artifacts)

    def __get__(self, key):
        return self.artifacts[key]

    @property
    def recursive_imports(self):
        subimports = {key: artifact for branch in self.branches for key, artifact in branch.recursive_imports.items()}
        return {**self.artifacts, **subimports}

    def import_files(self, imports):
        for imp in imports:
            try:
                absolute_paths = [os.path.join(path, imp) for path in self.import_paths]
                found_path     = next(path for path in absolute_paths if os.path.exists(path))
                canonical_path = os.path.realpath(found_path)
            except StopIteration:
                print(f"🛑 `{imp}' could not be imported!", file=stderr)
                exit(-1)

            # Try to retrieve artifact from the cache
            artifact = self.cache.get(canonical_path)

            # Artifact was not cached, load from file and cache it
            if not artifact:
                branch   = ImportManager(self)
                artifact = ArtifactManager.load_artifact(canonical_path, branch)
                self.branches.add(branch)
                self.cache[canonical_path] = artifact

            self.artifacts[imp] = artifact

        return self

    def module_providing_interface(self, interface_name):
        return next(
            artifact
            for artifact in self.recursive_imports.values()
            if interface_name in artifact.interfaces
        )
