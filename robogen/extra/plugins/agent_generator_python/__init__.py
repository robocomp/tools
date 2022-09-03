__name__    = 'agent_generator_python'
__version__ = '0.1.0'
__author__  = 'José Miguel Sánchez García'

DEPENDENCIES = {
    'agent': '==0.1.0',
}

import os
import robogen

class PythonAgentGenerator(robogen.Generator):
    PATH = f'{os.path.dirname(__file__)}'

    TREE = {
        'CMakeLists.txt',
        'DoxyFile',
        'README.md',
        # etc
            'etc/config',
        # src
            'src/CMakeLists.txt',
            'src/genericworker.py',
            'src/interfaces.py',
            'src/main.py',
            'src/specificworker.py',
    }

    KEEP = {
        'README.md',
        # etc
            'etc/config',
        # src
            'src/specificworker.py',
    }

    def tree(self, artifact):
        tree = self.__class__.TREE.copy()
        tree[f'src/main.py'].output = f'src/{artifact.name}.py'
        return tree

class Plugin:
    @classmethod
    def install(klass, installer):
        PythonAgentGenerator.install_default_file_tree()
        installer.install_generator('agent', 'python', PythonAgentGenerator)
