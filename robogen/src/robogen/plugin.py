import os
from importlib.machinery import SourceFileLoader
import semver
from sys import stderr
from traceback import print_exc

from .artifact  import ArtifactManager
from .parser    import ParserManager
from .generator import GeneratorManager

class PluginInstaller:
    '''Gateway for plugins to install functionality into robogen.'''

    @classmethod
    def install_artifact(klass, name, artifact, markers={}, extensions={}):
        ArtifactManager.add_artifact(name, artifact, markers, extensions)

    @classmethod
    def install_parser(klass, name, parser, extensions={}):
        ParserManager.add_parser(name, parser, extensions)

    @classmethod
    def install_generator(klass, artifact, language, generator):
        GeneratorManager.add_generator(artifact, language, generator)

    @classmethod
    def install_populator(klass, artifact, language, matcher, populator):
        artifact = ArtifactManager.find_artifact_by_name(artifact)
        (GeneratorManager
            .find_generator(artifact, language)
            .install_extra_populator(matcher, populator))

    @classmethod
    def install_schema_extension(klass, artifact, anchor, *args, **kwargs):
        (ArtifactManager
            .find_artifact_by_name(artifact)
            .extend_schema(anchor, *args, **kwargs))

    @classmethod
    def install_syntax_extension(klass, parser, anchor, *args, **kwargs):
        (ParserManager
            .find_parser_by_name(parser)
            .extend_syntax(anchor, *args, **kwargs))

    @classmethod
    def install_artifact_ctor_extension(klass, artifact, function):
        (ArtifactManager
            .find_artifact_by_name(artifact)
            .extend_ctor(function))

class PluginManager:
    '''Middleware which takes care of finding and loading plugins.'''

    plugins = {}
    paths   = set()

    @classmethod
    def add_path(klass, path):
        klass.paths.add(path)

    @classmethod
    def is_plugin_installed(klass, name, version=None):
        module = klass.plugins.get(name, None)
        return module and (not version or semver.match(module.__version__, version))

    @classmethod
    def load_plugins(klass):
        candidates = {}

        # Look inside each plugin path for candidates
        for path in klass.paths:
            if not os.path.exists(path):
                continue

            for entry in os.listdir(path):
                entry = f'{path}/{entry}'

                # Ignore Python package shenanigans
                if entry.endswith('/__pycache__') or entry.endswith('/__init__.py'):
                    continue

                if os.path.isdir(entry):
                    entry = f'{entry}/__init__.py'

                try:
                    module = SourceFileLoader(entry, entry).load_module()
                    candidates[module.__name__] = module
                except Exception as e:
                    print_exc()
                    print(f"⚠️ Error loading plugin at `{entry}'", file=stderr)

        # Load each plugin one by one, taking care of dependencies first
        for module in candidates.values():
            try:
                klass.install_candidate(module, candidates)
            except:
                print_exc()
                print(f"⚠️ Error installing plugin `{module.__name__}'", file=stderr)

        # Print info about loaded plugins
        print(f'Loaded {len(klass.plugins)} plugins', file=stderr)

        for name, module in klass.plugins.items():
            print(f'\t{name} ({module.__version__})', file=stderr)

        print(file=stderr)

    @classmethod
    def install_candidate(klass, module, candidates):
        # Ignore already installed plugins
        if klass.is_plugin_installed(module.__name__, f'=={module.__version__}'):
            return

        # Install plugin dependencies first
        deps = getattr(module, 'DEPENDENCIES', {})
        for name, version in deps.items():
            dep = candidates[name]
            assert not version or semver.match(dep.__version__, version)
            klass.install_candidate(dep, candidates)

        module.Plugin.install(PluginInstaller)
        klass.plugins[module.__name__] = module
