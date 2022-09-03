import robogen

class Populator(robogen.Populator):
    def populate(self):
        return {
            'component_name': self.artifact.name,
	    }
