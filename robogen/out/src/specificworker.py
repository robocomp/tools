#!/usr/bin/python3
# -*- coding: utf-8 -*-

# MIT License
# 
# Copyright (c) 2022 [fullname]
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
 

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from rich.console import Console
from genericworker import *
import interfaces as ifaces

sys.path.append('/opt/robocomp/lib')
console = Console(highlight=False)

from pydsr import *



# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel


class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000
        
# YOU MUST SET AN UNIQUE ID FOR THIS AGENT IN YOUR DEPLOYMENT. "_CHANGE_THIS_ID_" for a valid unique integer
self.agent_id = "_CHANGE_THIS_ID_"
self.g = DSRGraph(0, "pythonAgent", self.agent_id)

try:
    signals.connect(self.g, signals.UPDATE_NODE_ATTR, self.update_node_att)
    signals.connect(self.g, signals.UPDATE_NODE, self.update_node)
    signals.connect(self.g, signals.DELETE_NODE, self.delete_node)
    signals.connect(self.g, signals.UPDATE_EDGE, self.update_edge)
    signals.connect(self.g, signals.UPDATE_EDGE_ATTR, self.update_edge_att)
    signals.connect(self.g, signals.DELETE_EDGE, self.delete_edge)
    console.print("signals connected")
except RuntimeError as e:
    print(e)


        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
self.timer.start(self.Period)


    def __del__(self):
        """Destructor"""

    def setParams(self, params):
        # try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        # except:
        #	traceback.print_exc()
        #	print("Error reading config params")
        return True

    @QtCore.Slot()
def compute(self):
    print('SpecificWorker.compute...')
    # computeCODE
    # try:
    #   self.differentialrobot_proxy.setSpeedBase(100, 0)
    # except Ice.Exception as e:
    #   traceback.print_exc()
    #   print(e)

    # The API of python-innermodel is not exactly the same as the C++ version
    # self.innermodel.updateTransformValues('head_rot_tilt_pose', 0, 0, 0, 1.3, 0, 0)
    # z = librobocomp_qmat.QVec(3,0)
    # r = self.innermodel.transform('rgbd', z, 'laser')
    # r.printvector('d')
    # print(r[0], r[1], r[2])

    return True


    def startup_check(self):
        print(f"Testing RoboCompDifferentialRobot.TMechParams from ifaces.RoboCompDifferentialRobot")
test = ifaces.RoboCompDifferentialRobot.TMechParams()
print(f"Testing RoboCompLaser.LaserConfData from ifaces.RoboCompLaser")
test = ifaces.RoboCompLaser.LaserConfData()
print(f"Testing RoboCompLaser.TData from ifaces.RoboCompLaser")
test = ifaces.RoboCompLaser.TData()

        QTimer.singleShot(200, QApplication.instance().quit)

    

    

    ######################
# From the RoboCompDifferentialRobot you can call this methods:
# self.differentialrobot_proxy.getBaseState(...)
# self.differentialrobot_proxy.getBasePose(...)
# self.differentialrobot_proxy.setSpeedBase(...)
# self.differentialrobot_proxy.stopBase(...)
# self.differentialrobot_proxy.resetOdometer(...)
# self.differentialrobot_proxy.setOdometer(...)
# self.differentialrobot_proxy.setOdometerPose(...)
# self.differentialrobot_proxy.correctOdometer(...)

######################
# From the RoboCompDifferentialRobot you can use this types:
# RoboCompDifferentialRobot.TMechParams

######################
# From the RoboCompLaser you can call this methods:
# self.laser_proxy.getLaserData(...)
# self.laser_proxy.getLaserAndBStateData(...)
# self.laser_proxy.getLaserConfData(...)

######################
# From the RoboCompLaser you can use this types:
# RoboCompLaser.LaserConfData

# RoboCompLaser.TData



    
# =============== DSR SLOTS  ================
# =============================================

def update_node_att(self, id: int, attribute_names: [str]):
    console.print(f"UPDATE NODE ATT: {id} {attribute_names}", style='green')

def update_node(self, id: int, type: str):
    console.print(f"UPDATE NODE: {id} {type}", style='green')

def delete_node(self, id: int):
    console.print(f"DELETE NODE:: {id} ", style='green')

def update_edge(self, fr: int, to: int, type: str):

    console.print(f"UPDATE EDGE: {fr} to {type}", type, style='green')

def update_edge_att(self, fr: int, to: int, type: str, attribute_names: [str]):
    console.print(f"UPDATE EDGE ATT: {fr} to {type} {attribute_names}", style='green')

def delete_edge(self, fr: int, to: int, type: str):
    console.print(f"DELETE EDGE: {fr} to {type} {type}", style='green')

