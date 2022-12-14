import tornado.web
import yaml
from tornado.httpclient import AsyncHTTPClient

from loadbalancer.servers.backend_servers import Server
import builtins


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

    def get_healthy_server(self, host_or_path: str) -> Server:
        server_tracker = builtins.server_tracker
        if host_or_path in self.register.keys():
            all_healthy_servers = [
                server for server in self.register[host_or_path] if server.healthy
            ]
            length_of_all_healthy_servers = len(all_healthy_servers)

            # first fetch for host/path = get first server from array
            if host_or_path not in server_tracker:
                first_healthy_server = all_healthy_servers[0]
                server_tracker[host_or_path] = first_healthy_server
                builtins.server_tracker = server_tracker
                return first_healthy_server
            # only one server? use that!
            elif len(all_healthy_servers) == 1:
                first_healthy_server = all_healthy_servers[0]
                server_tracker[host_or_path] = first_healthy_server
                builtins.server_tracker = server_tracker
                return first_healthy_server
            else:
                index_of_last_server = all_healthy_servers.index(
                    server_tracker[host_or_path]
                )
                index_of_next_server = index_of_last_server + 1
                if index_of_next_server >= length_of_all_healthy_servers:
                    first_healthy_server = all_healthy_servers[0]
                    server_tracker[host_or_path] = first_healthy_server
                    builtins.server_tracker = server_tracker
                    return first_healthy_server
                else:
                    next_healthy_server = all_healthy_servers[index_of_next_server]
                    server_tracker[host_or_path] = next_healthy_server
                    builtins.server_tracker = server_tracker
                    return next_healthy_server
        else:
            return Server(endpoint="localhost:404", healthy=False)

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
            print(healthy_server)
        else:
            self.set_status(404)
