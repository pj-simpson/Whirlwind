import tornado.web
import yaml
from tornado.httpclient import AsyncHTTPClient
import random

from src.whirlwind.backend_servers.backend_servers import Server


class ConfigReadingRequestHandler(tornado.web.RequestHandler):

    register = {}

    with open('loadbalancer.yaml') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    def create_dictionary_register_of_backend_servers(self) -> None:
        if self.config:
            for entry in self.config.get('hosts', []):
                self.register.update(
                    {entry['host']:
                         [Server(endpoint) for endpoint in entry['servers']]
                    }
                )
            for entry in self.config.get('paths', []):
                self.register.update(
                    {entry['path']:
                         [Server(endpoint) for endpoint in entry['servers']]
                     }
                )
        else:
            NotImplementedError

    async def healthcheck(self):
        for host in self.register:
            for server in self.register[host]:
                await server.do_healthcheck_and_update_status()

    def get_healthy_server(self,host_or_path):
        try:
            return random.choice([server for server in self.register[host_or_path] if server.healthy])
        except IndexError:
            return None

    async def forward_incoming_request_to_server(self, singular, plural, attrib):
        http_client = AsyncHTTPClient()
        for entry in self.config[plural]:
            if (attrib) == entry[singular]:
                healthy_server = self.get_healthy_server(entry[singular])
                if not healthy_server:
                    self.set_status(503, 'No healthy backend servers found')
                else:
                    response = await http_client.fetch(f'http://{healthy_server.endpoint}')
                    response_message = response.body.decode("utf-8")
                    self.set_status(response.code)
                    self.write(response_message)
            else:
                self.set_status(404, 'Not Found')
        http_client.close()