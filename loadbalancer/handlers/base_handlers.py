import random
import typing

import tornado.web
import yaml
from tornado.httpclient import AsyncHTTPClient

from loadbalancer.servers.backend_servers import Server


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
        for item in self.register:
            for server in self.register[item]:
                await server.do_healthcheck_and_update_status()

    def get_healthy_server(self, host_or_path: str) -> typing.Union[Server, str]:
        if host_or_path in self.register.keys():
            return random.choice(
                [server for server in self.register[host_or_path] if server.healthy]
            )
        else:
            return Server(endpoint='localhost:404',healthy=False)

    async def forward_incoming_request_to_server(
        self,
        host_or_path: str,
    ) -> None:
        http_client = AsyncHTTPClient()
        healthy_server = self.get_healthy_server(host_or_path)
        if healthy_server.healthy:
            response = await http_client.fetch(f"http://{healthy_server.endpoint}")
            response_message = response.body.decode("utf-8")
            self.set_status(response.code)
            self.write(response_message)
        else:
            self.set_status(404)
