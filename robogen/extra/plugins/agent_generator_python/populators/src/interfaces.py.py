from string import Template
from robogen.utils import full_type_string, number_duplicates
import os
import robogen

# TODO: Check if this can be reduced to an abstract class and some inheriting from that.
LIST_CLASSES = '''\
class ${list_type}(list):
    def __init__(self, iterable=list()):
        super(${list_type}, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, ${item_type})
        super(${list_type}, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, ${item_type})
        super(${list_type}, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, ${item_type})
        super(${list_type}, self).insert(index, item)

setattr(${module_name}, "${list_type}", ${list_type})
'''

SLICE_LOAD = '''\
Ice.loadSlice("-I ./src/ --all ./src/${filename}.ice")
'''

SUBSCRIBES_TO = '''\
self.${name} = self.create_adapter("${name}Topic", ${name_lower}I.${name}I(default_handler))
'''

REQUIRE = '''\
self.${name}${i} = self.create_proxy("${name}${i}Proxy", ${module_name}.${name}Prx)
'''

PUBLISHES = '''\
self.${name_lower} = self.create_topic("${name}", ${module_name}.${name}Prx)
'''

IMPLEMENTS = '''\
self.${name_lower} = self.create_adapter("${name}", ${name_lower}I.${name}I(default_handler))
'''

class Populator(robogen.Populator):
    def populate(self):
        return {
            'load_slice_and_create_imports':        self.load_slice_and_create_imports(),
            'create_list_classes':                  self.create_list_classes(),
            'implements_and_subscribes_to_imports': self.implements_and_subscribes_to_imports(),
            'publish_proxy_creation':               self.publish_proxy_creation(),
            'require_proxy_creation':               self.require_proxy_creation(),
            'subscribes_to_adapters_creation':      self.subscribes_to_adapters_creation(),
            'implements_adapters_creation':         self.implements_adapters_creation(),
            'needs_rcnode':                         self.needs_rcnode(),
	    }

    def load_slice_and_create_imports(self):
        result = ''

        for path, module in self.artifact.imports.recursive_imports.items():
            filename = os.path.basename(path).rsplit('.', maxsplit=2)[0]
            result += Template(SLICE_LOAD).substitute(filename=filename)
            result += f'import {module.name}\n'
            pass

        return result

    def create_list_classes(self):
        result  = ''

        for path in self.artifact.imports.recursive_imports:
            name   = os.path.basename(path).rsplit('.', maxsplit=2)[0]
            module =  self.artifact.imports.module_providing_interface(name)

            if module is None:
                continue

            for name, sequence in module.sequences.items():
                type = full_type_string(sequence['type'], module.name)

                if type == 'bytes':
                    continue

                result += Template(LIST_CLASSES).substitute({
                    'list_type':   name,
                    'item_type':   type,
                    'module_name': module.name,
                })

        return result

    def implements_and_subscribes_to_imports(self):
        robocomp_comm = self.artifact.communications['robocomp']

        return '\n'.join((
            f'import {interface.lower()}I'
            for interface in robocomp_comm['implements'] + robocomp_comm['subscribes_to']
            if interface.type == 'ice'
        ))

    def publish_proxy_creation(self):
        robocomp_comm = self.artifact.communications['robocomp']
        result = ''

        for req, i in number_duplicates(robocomp_comm['publishes'], lambda req: req['name']):
            name = req['name']

            module = self.artifact.imports.module_providing_interface(name)
            result += Template(PUBLISHES).substitute({
                'name':        name,
                'name_lower':  name.lower(),
                'module_name': module.name,
            })

        return result

    def require_proxy_creation(self):
        robocomp_comm = self.artifact.communications['robocomp']
        result = ''

        for req, i in number_duplicates(robocomp_comm['requires'], lambda req: req['name']):
            name = req['name']

            module = self.artifact.imports.module_providing_interface(name)
            result += Template(REQUIRE).substitute({
                'name':        name,
                'i':           i,
                'name_lower':  name.lower(),
                'module_name': module.name,
            })

        return result

    def subscribes_to_adapters_creation(self):
        return '\n'.join((
            Template(SUBSCRIBES_TO).substitute({
                'name':       interface['name'],
                'name_lower': interface['name'].lower()
            })
            for interface in self.artifact.communications['robocomp']['subscribes_to']
            if interface.type == 'ice'
        ))

    def implements_adapters_creation(self):
        return '\n'.join((
            Template(IMPLEMENTS).substitute({
                'name':       interface['name'],
                'name_lower': interface['name'].lower()
            })
            for interface in self.artifact.communications['robocomp']['implements']
            if interface.type == 'ice'
        ))

    def needs_rcnode(self):
        robocomp_comm = self.artifact.communications['robocomp']
        return bool(robocomp_comm['subscribes_to'] or robocomp_comm['implements'])
