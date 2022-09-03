import random
import re
import robogen
from robogen.utils import number_duplicates

try:
    from rcportchecker import RCPortChecker
    RCPORTCHECKER_IMPORTED = True
except:
    RCPORTCHECKER_IMPORTED = False

STORM_TOPIC_MANAGER = '''\
# This property is used by the clients to connect to IceStorm.
TopicManager.Proxy=IceStorm/TopicManager:default -p 9999
'''

DEFAULT_PORTS = {
    'DifferentialRobot': 10004,
    'Laser':             10003,
}

def get_existing_port(name):
    ports = RCPortChecker().search_interface_ports_by_name(name)
    return min(ports.keys(), default=0) if ports else 0

class Populator(robogen.Populator):
    def populate(self):

        return {
            # TODO: are these needed? How to get those from the agent definition?
            'implements_endpoints':    '',
            'subscribes_to_endpoints': '',
            'requires_proxies':        self.requires_proxies(),
            'storm_topic_manager':     self.storm_topic_manager(),
	    }

    def requires_proxies(self):
        robocomp_comm = self.artifact.communications['robocomp']
        result = ''

        for req, i in number_duplicates(robocomp_comm['requires'], lambda req: req['name']):
            if req['type'] != 'ice':
                continue

            name = req['name']
            
            if name in DEFAULT_PORTS:    port = DEFAULT_PORTS[name]
            elif RCPORTCHECKER_IMPORTED: port = get_existing_port(name)
            else:                        port = random.randint(10001, 19000)

            result += f'{name}{i}Proxy = {name.lower()}:tcp -h localhost -p {port}\n'

        if not result:
            return ''

        return '\n'.join((
            f'# Proxies for required interfaces',
            result,
        ))

    def storm_topic_manager(self):
        robocomp_comm = self.artifact.communications['robocomp']
        pubs = robocomp_comm['publishes']
        subs = robocomp_comm['subscribes_to']

        return STORM_TOPIC_MANAGER if pubs or subs else ''
