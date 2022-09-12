import importlib
import os
import re
import shlex
import subprocess
from string import Template
from sys import exit, stderr

from .artifact import ArtifactManager

class FileEntry:
    def __init__(self, output, populators):
        self.output     = output
        self.populators = populators

    def insert_populator(self, populator):
        self.populators.insert(0, populator)

class Generator:
    @classmethod
    def install_extra_populator(klass, matcher, populator):
        for file, entry in klass.TREE.items():
            if matcher(file):
                entry.insert_populator(populator)

    @classmethod
    def install_default_file_tree(klass):
        tree = {}

        for file in klass.TREE:
            source = f'{klass.PATH}/populators/{file}.py'

			# Dummy plug for files without a populator
            if not os.path.exists(source):
                tree[file] = []
                continue

            spec   = importlib.util.spec_from_file_location('', source)
            module = importlib.util.module_from_spec(spec)

            spec.loader.exec_module(module)
            tree[file] = FileEntry(file, [module.Populator])

        klass.TREE = tree

    def tree(self, artifact):
        return self.TREE

    def generate_files(self, artifact, output_path):
        diff_files = {}

        for file, entry in self.tree(artifact).items():
            source = f'{self.PATH}/files/{file}'
            target = f'{output_path}/{entry.output}'

            os.makedirs(os.path.dirname(target), exist_ok=True)

            # Avoid overwriting file if marked in KEEP
            if os.path.exists(target) and file in self.KEEP:
                old_file = target
                target   = f'{target}.new'
                diff_files[old_file] = target

            # Read input template
            with open(source, 'r') as f:
                result = f.read()

			# Run all populators through it
            for populator in entry.populators:
                template = IndentedTemplate(result.replace('$$', '$$$$'))
                fields   = populator(file, artifact).populate()
                result   = template.substitute(fields)

            # Simple dummy class which will return '' for any subscript attempt
            # This lets the template clear all leftover hooks.
            class Dummy:
                def __getitem__(self, key):
                    return ''

                def get(self, key, default=None):
                    return ''

            # Cleanup unused hooks
            result = IndentedTemplate(result).substitute(Dummy())

            # Write generated code
            with open(target, 'w') as f:
                f.write(result)

            print(f"\t{file}  →  {target}", file=stderr)

        return diff_files

class GeneratorManager:
    generators = {}
    diff_tool  = None

    @classmethod
    def set_diff_tool(klass, diff_tool):
        klass.diff_tool = diff_tool

    @classmethod
    def find_generator(klass, artifact, language):
        return klass.generators.get((artifact, language))

    @classmethod
    def add_generator(klass, artifact, language, generator):
        artifact = ArtifactManager.find_artifact_by_name(artifact)
        language = language.lower()
        klass.generators[(artifact, language)] = generator

    def generate_files(self, input_file, output_path):
        # Initialize artifact
        artifact = ArtifactManager.load_artifact(input_file)

        name      = getattr(artifact, 'name', None)
        language  = getattr(artifact, 'language', None)
        generator = self.find_generator(artifact.__class__, language)

        if not generator:
            if not language:
                print(f'🛑 No generator for artifact type found', file=stderr)
            else:
                print(f"🛑 No generator for artifact type and language `{language}' found", file=stderr)
            exit(-1)

        print(f"Generating artifact `{name}' for language `{language}' into `{output_path}'", file=stderr)
        diff_files = generator().generate_files(artifact, output_path)

        if diff_files:
            print(f'\nFound {len(diff_files)} modified files:', file=stderr)

            for file in diff_files:
                print(f'\t{file}', file=stderr)

            print(f"\nOld files kept intact, updated files saved with suffix `.new'", file=stderr)

        if not self.diff_tool:
            return

        print(file=stderr)
        for old_file, new_file in diff_files.items():
            tool, *args = shlex.split(self.diff_tool)
            subprocess.call([tool, *args, old_file, new_file])

class IndentedTemplate(Template):
    # TODO: copied straight from RoboCompDSL, maybe cleanup and tidy up the code?
    delimiter = '$'
    pattern = r'''
        (?P<previous>[^$\n]*)\$(?:
            (?P<escaped>\$) |   # Escape sequence of two delimiters
            (?P<named>[_a-z][_a-z0-9]*)      |   # delimiter and a Python identifier
            {(?P<braced>[_a-z][_a-z0-9]*)}   |   # delimiter and a braced identifier
            (?P<invalid>)              # Other ill-formed delimiter exprs
        )
    '''

    def __init__(self, template, trimlines=True):
        super(IndentedTemplate, self).__init__(template)
        self.trimlines = trimlines

    def substitute(*args, **kws):
        if not args:
            raise TypeError("descriptor 'substitute' of 'Template' object "
                            "needs an argument")
        self, *args = args  # allow the "self" keyword be passed
        if len(args) > 1:
            raise TypeError('Too many positional arguments')
        if not args:
            mapping = kws
        elif kws:
            mapping = ChainMap(kws, args[0])
        else:
            mapping = args[0]

        def reindent(previous, string):
            if previous.strip() == '':
                out_lines = []
                lines = string.splitlines()
                if len(lines) > 0:
                    if self.trimlines:
                        if lines and lines[0].strip() == '':
                            del lines[0]
                        if lines and lines[-1].strip() == '':
                            del lines[-1]
                    for line in lines:
                        if line.strip() != '':
                            out_lines.append(previous + line)
                        else:
                            out_lines.append(line)
                return '\n'.join(out_lines)
            else:
                return previous+string

        # Helper function for .sub()
        def convert(mo):
            # Check the most common path first.
            named = mo.group('named') or mo.group('braced')
            if named is not None:
                converted = reindent(mo.group('previous'), str(mapping.get(named, f'${{{named}}}')))
                if converted != '':
                    return converted
                else:
                    return "<LINEREMOVE>"
            if mo.group('escaped') is not None:
                return mo.group('previous')+self.delimiter
            if mo.group('invalid') is not None:
                self._invalid(mo)
            raise ValueError('Unrecognized named group in pattern',
                             self.pattern)
        substituted = self.pattern.sub(convert, self.template)
        # The only way to remove extra lines that template leaves.
        return re.sub('<LINEREMOVE>.*\n', '', substituted)

    def identifiers(self):
        identifiers = []
        results = self.pattern.findall(self.template)
        for result in results:
            if result[3] != '' and result[3] not in identifiers:
                identifiers.append(result[3])
        return identifiers
