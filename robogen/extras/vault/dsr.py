__name__    = 'dsr'
__version__ = '0.1.0'
__author__  = 'José Miguel Sánchez García'

class Plugin:
    @classmethod
    def install(klass, installer):
        installer.install_option('dsr')
