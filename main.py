#!/usr/bin/env python3
import builtins

import tornado.ioloop
import tornado.options
import tornado.web
import dill

from tornado.options import define, options

from loadbalancer.handlers.base_handlers import ConfigReadingRequestHandler

define("port", default=8000, type=int)


class HostRouter(ConfigReadingRequestHandler):
    async def get(self) -> None:
        await self.healthcheck()
        host_header = self.request.headers["Host"]
        if host_header:
            await self.forward_incoming_request_to_server(host_header)
        else:
            self.set_status(400, "No host header detected")


class PathRouter(ConfigReadingRequestHandler):
    async def get(self, path: str) -> None:
        full_path = "/" + path
        await self.healthcheck()
        await self.forward_incoming_request_to_server(full_path)


def make_app() -> tornado.web.Application:

    builtins.server_tracker = {}

    return tornado.web.Application(
        handlers=[
            (r"/", HostRouter),
            (r"/(\w+)", PathRouter),
        ]
    )


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = make_app()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
