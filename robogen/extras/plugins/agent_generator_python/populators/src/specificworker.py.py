from string import Template
from robogen.utils import full_type_string, number_duplicates
import robogen

DSR_SLOTS = '''\

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
'''


DSR_IMPORT = '''\
from pydsr import *

'''

DSR_INIT = '''\

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

'''

COMPUTE_METHOD_STR = '''\
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
'''

TIMEOUT_COMPUTE_CONNECT = '''\
self.timer.timeout.connect(self.compute)
self.timer.start(self.Period)
'''

PROXY_METHODS_COMMENT = '''\
######################
# From the ${module_name} you can ${action} this methods:
${methods}

'''

INTERFACE_TYPES_TEST = '''\
print(f"Testing ${type} from ifaces.${module_name}")
test = ifaces.${type}()
'''

INTERFACE_TYPES_COMMENT = '''\
######################
# From the ${module_name} you can use this types:
${structs}
'''

METHOD = '''\
#
# ${method_str1} ${method_name} method from ${interface_name} interface
#
def ${interface_name}_${method_name}(self${param_str_a}):
    ${return_creation}
    #
    # write your CODE here
    #
    ${return_str}
'''

class Populator(robogen.Populator):
    def populate(self):
        return {
            'component_name':             self.artifact.name,
            'dsr_import':                 DSR_IMPORT,
            'dsr_slots':                  DSR_SLOTS,
            'dsr_init':                   DSR_INIT,
            'timeout_compute_connect':    TIMEOUT_COMPUTE_CONNECT,
            'compute_creation':           COMPUTE_METHOD_STR,
            'startup_check_ice':          self.startup_check_ice(),
            'subscribes_to_methods':      self.subscribes_to_methods(),
            'implements_methods':         self.implements_methods(),
            'interface_specific_comment': self.interface_specific_comment(),
	    }

    def methods(self, interfaces, subscribe=False):
        # TODO: The original method is very, intrincate. Will do this later.
        return '# TODO'

    def subscribes_to_methods(self):
        subscribes_to = self.artifact.communications['robocomp']['subscribes_to']

        if not subscribes_to:
            return ''

        return '\n'.join((
            '# =============== Methods for Component SubscribesTo ================'
            '# ===================================================================',
            '',
            self.methods(subscribes_to, subscribe=True),
            '# ===================================================================',
            '# ===================================================================',
            '',
        ))

    def implements_methods(self):
        implements = self.artifact.communications['robocomp']['implements']

        if not implements:
            return ''

        return '\n'.join((
            '# =============== Methods for Component Implements ==================',
            '# ===================================================================',
            '',
            self.methods(implements),
            '# ===================================================================',
            '# ===================================================================',
            '',
        ))

    def startup_check_ice(self):
        result = ''
        robocomp_comm = self.artifact.communications['robocomp']

        interfaces = (
            robocomp_comm['requires']
            + robocomp_comm['publishes']
            + robocomp_comm['implements']
            + robocomp_comm['subscribes_to']
        )

        for interface in interfaces:
            if interface['type'] != 'ice':
                continue

            module = self.artifact.imports.module_providing_interface(interface['name'])

            for name in module.structs:
                result += Template(INTERFACE_TYPES_TEST).substitute({
                    'module_name': module.name,
                    'type':        full_type_string(name, module.name),
                })
            pass

        return result

    def interface_specific_comment(self):
        robocomp_comm = self.artifact.communications['robocomp']
        result = ''

        for type in {'requires', 'publishes', 'implements', 'subscribes_to'}:
            for interface, i in number_duplicates(robocomp_comm[type], lambda iface: iface['name']):
                if interface['type'] != 'ice':
                    continue

                module = self.artifact.imports.module_providing_interface(interface['name'])

                if type in {'publishes', 'requires'}:
                    proxy_reference = f'self.{interface["name"].lower()}{i}_proxy.'
                    action = 'publish calling' if type == 'publishes' else 'call'

                    proxy_method_calls = '\n'.join(
                        f'# {proxy_reference}{method}(...)'
                        for method in module.interfaces[interface['name']]
                    )

                    if proxy_method_calls:
                        result += Template(PROXY_METHODS_COMMENT).substitute({
                            'module_name': module.name,
                            'methods':     proxy_method_calls,
                            'action':      action,
                        })

                struct_str = '\n'.join(
                    f'# {full_type_string(struct, module.name)}\n'
                    for struct in module.structs
                )

                if struct_str:
                    result += Template(INTERFACE_TYPES_COMMENT).substitute({
                        'module_name': module.name,
                        'structs':     struct_str,
                    })

        return result
