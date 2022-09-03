import robogen
from robogen.utils import number_duplicates

class Populator(robogen.Populator):
    def populate(self):
        return {
            'requires_proxies':  self.requires_proxies(),
            'publishes_proxies': self.publishes_proxies(),
	    }

    def requires_proxies(self):
        robocomp_comm = self.artifact.communications['robocomp']
        result = ''

        for req, i in number_duplicates(robocomp_comm['requires'], lambda req: req['name']):
            name = req['name']

            if   req['type'] == 'ice': result += f'self.{name.lower()}_proxy = mprx["{name}Proxy{i}"]\n'
            elif req['type'] == 'ros': result += f'self.{name.lower()}_proxy = ServiceClient{name}()\n'

        return result

    def publishes_proxies(self):
        robocomp_comm = self.artifact.communications['robocomp']
        result = ''

        for pub, i in number_duplicates(robocomp_comm['publishes'], lambda req: req['name']):
            name = pub['name']

            if   pub['type'] == 'ice': result += f'self.{name.lower()}_proxy = mprx["{name}{i}"]\n'
            elif pub['type'] == 'ros': result += f'self.{name.lower()}_proxy = Publisher{name}()\n'

        return result
