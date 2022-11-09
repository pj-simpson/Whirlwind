import random

import tornado.web
import yaml
from tornado.httpclient import AsyncHTTPClient

from src.whirlwind.backend_servers.backend_servers import Server


class ConfigReadingRequestHandler(tornado.web.RequestHandler):

    register: dict = {}

    with open("loadbalancer.yaml") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
        if config:
            for entry in config.get("hosts", []):
                register.update(
                    {entry["host"]: [Server(endpoint) for endpoint in entry["servers"]]}
                )
            for entry in config.get("paths", []):
                register.update(
                    {entry["path"]: [Server(endpoint) for endpoint in entry["servers"]]}
                )
        else:
            NotImplementedError

    # # raw config example
    # {
    #     "hosts": [
    #         {"host": "www.a.com", "servers": ["localhost:8081", "localhost:8082"]},
    #         {"host": "www.b.com", "servers": ["localhost:9081", "localhost:9082"]},
    #     ],
    #     "paths": [
    #         {"path": "/a", "servers": ["localhost:8081", "localhost:8082"]},
    #         {"path": "/b", "servers": ["localhost:9081", "localhost:9082"]},
    #     ],
    # }

    # # transformed register example
    # {
    #     'www.a.com':
    #       [ <Server: localhost:8081 True >, < Server: localhost:8082 True >],
    #     'www.b.com':
    #       [ < Server: localhost: 9081 True >, < Server: localhost:9082 True >],
    #     '/a':
    #       [ < Server: localhost: 8081 True >, < Server: localhost:8082 True >],
    #     '/b':
    #       [ < Server: localhost: 9081 True >, < Server: localhost:9082 True >]
    # }

    async def healthcheck(self) -> None:
        for host in self.register:
            for server in self.register[host]:
                await server.do_healthcheck_and_update_status()

    def get_healthy_server(self, host_or_path: str) -> None:
        try:
            return random.choice(
                [server for server in self.register[host_or_path] if server.healthy]
            )
        except IndexError:
            return None

    async def forward_incoming_request_to_server(
        self, singular: str, plural: str, attrib: str
    ) -> None:
        http_client = AsyncHTTPClient()
        for entry in self.config[plural]:
            if (attrib) == entry[singular]:
                healthy_server = self.get_healthy_server(entry[singular])
                if not healthy_server:
                    self.set_status(503, "No healthy backend servers found")
                else:
                    response = await http_client.fetch(
                        f"http://{healthy_server.endpoint}"
                    )
                    response_message = response.body.decode("utf-8")
                    self.set_status(response.code)
                    self.write(response_message)
            else:
                self.set_status(404, "Not Found")
        http_client.close()
