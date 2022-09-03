import os
import robogen

class Populator(robogen.Populator):
    def populate(self):
        # TODO: this will produce invalid code if the interface is not
        # implemented as CDSL due to robocomp's CMake macro.
        ice_interfaces = {
            os.path.basename(interface).rsplit('.', maxsplit=2)[0]
            for interface in {*self.artifact.imports.recursive_imports.keys(), *self.artifact.ice_interfaces}
        }

        return {
            'component_name': self.artifact.name,
            'ice_interfaces': ' '.join(ice_interfaces),
	    }
