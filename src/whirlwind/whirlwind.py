import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

from src.whirlwind.base_handlers.base_handlers import \
    ConfigReadingRequestHandler

define("port", default=8000, type=int)


class HostRouter(ConfigReadingRequestHandler):
    async def get(self) -> None:
        await self.healthcheck()
        host_header = self.request.headers["Host"]
        if host_header:
            await self.forward_incoming_request_to_server("host", "hosts", host_header)
        else:
            self.set_status(400, "No host header detected")


class PathRouter(ConfigReadingRequestHandler):
    async def get(self, path: str) -> None:
        _ = path
        full_path = self.request.path
        await self.healthcheck()

        await self.forward_incoming_request_to_server("path", "paths", full_path)


def make_app() -> tornado.web.Application:
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
