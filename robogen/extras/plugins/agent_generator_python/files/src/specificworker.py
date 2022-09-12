#!/usr/bin/python3
# -*- coding: utf-8 -*-

${header}

from PySide2.QtCore import QLoggingCategory, QTimer
from PySide2.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

${dsr_import}

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000
        ${qtdebug}
        ${dsr_init}
        ${dsr_ignored_attrs}
        if startup_check:
            self.startup_check()
        else:
            ${timeout_compute_connect}

    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True

    ${compute_creation}

    def startup_check(self):
        ${startup_check_ice}
        QTimer.singleShot(200, QApplication.instance().quit)

    ${subscribes_to_methods}

    ${implements_methods}

    ${interface_specific_comment}

    ${dsr_slots}
