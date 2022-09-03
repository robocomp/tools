#!/usr/bin/env python3
# -*- coding: utf-8 -*-

${header}

# \mainpage RoboComp::${component_name}
#
# \section intro_sec Introduction
#
# Some information about the component...
#
# \section interface_sec Interface
#
# Descroption of the interface provided...
#
# \section install_sec Installation
#
# \subsection install1_ssec Software depencences
# Software dependences....
#
# \subsection install2_ssec Compile and install
# How to compile/install the component...
#
# \section guide_sec User guide
#
# \subsection config_ssec Configuration file
#
# <p>
# The configuration file...
# </p>
#
# \subsection execution_ssec Execution
#
# Just: "$${PATH_TO_BINARY}/${component_name} --Ice.Config=$${PATH_TO_CONFIG_FILE}"
#
# \subsection running_ssec Once running
#
#
#

import argparse
# Ctrl+c handling
import signal

from rich.console import Console
console = Console()

import interfaces
from specificworker import *

#SIGNALS handler
def sigint_handler(*args):
    QtCore.QCoreApplication.quit()


if __name__ == '__main__':
    app = QtCore.QCoreApplication(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('iceconfigfile', nargs='?', type=str, default='etc/config')
    parser.add_argument('--startup-check', action='store_true')

    args = parser.parse_args()
    interface_manager = interfaces.InterfaceManager(args.iceconfigfile)

    if interface_manager.status == 0:
        worker = SpecificWorker(interface_manager.get_proxies_map(), args.startup_check)
        worker.setParams(interface_manager.parameters)
    else:
        print("Error getting required connections, check config file")
        sys.exit(-1)

    interface_manager.set_default_hanlder(worker)
    signal.signal(signal.SIGINT, sigint_handler)
    app.exec_()
    interface_manager.destroy()
