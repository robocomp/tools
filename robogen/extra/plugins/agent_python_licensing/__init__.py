__name__    = 'agent_python_licensing'
__version__ = '0.1.0'
__author__  = 'José Miguel Sánchez García'

DEPENDENCIES = {
    'agent_generator_python': '==0.1.0',
}

from datetime import date
from schema import Schema, And, Or, Use
from string import Template
from pyparsing import CaselessKeyword, Suppress, Word, alphanums, alphas
import schema
import pyparsing
import robogen

from .licenses import LICENSES

ADSL = pyparsing.Optional((
    # Keyword
    Suppress(CaselessKeyword('license'))
    # Identifier
    - Word(alphas + '_', alphanums + '_')
    # Semicolon
    - Suppress(Word(';'))
).setParseAction(lambda x: x[0])('license'))

# Specified license must be supported
SCHEMA = Schema(And(Use(str.lower), Or(*LICENSES.keys())))

header_template = lambda license: f'''\
{license}
$header'''

class LicensePopulator(robogen.Populator):
    @staticmethod
    def generate_python_header(license):
        return '\n'.join(f'# {line}' for line in license.splitlines())

    def populate(self):
        license = LICENSES[self.artifact.license]
        license = Template(license).substitute({'copyright_year': date.today().year})

        return {
            'header': header_template(LicensePopulator.generate_python_header(license)),
        }

def ctor_set_license(artifact, importer):
    setattr(artifact, 'license', artifact.tree['license'])

class Plugin:
    '''Adds a license header to source files of Python agents.'''

    @classmethod
    def install(klass, installer):
        installer.install_populator('agent', 'python', lambda file: file.endswith('.py'), LicensePopulator) 
        installer.install_artifact_ctor_extension('agent', ctor_set_license)
        installer.install_schema_extension('agent', 'root', schema.Optional('license', default='mit'), SCHEMA)
        installer.install_syntax_extension('adsl', 'root', ADSL)
