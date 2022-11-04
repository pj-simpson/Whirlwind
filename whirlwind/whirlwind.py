import tornado.ioloop
import tornado.options
import tornado.web
import random
from tornado.httpclient import AsyncHTTPClient

from tornado.options import define, options

define("port", default=8000, type=int)

class Router(tornado.web.RequestHandler):

    A_BACKENDS = ['localhost:8081', 'localhost:8082']
    B_BACKENDS = ['localhost:9081', 'localhost:9082']

    async def get(self):
        http_client = AsyncHTTPClient()
        host_header = self.request.headers['Host']

        if host_header == 'www.a.com':
            response = await http_client.fetch(f'http://{random.choice(self.A_BACKENDS)}')
            http_client.close()
            response_message = response.body.decode("utf-8")
            self.set_status(response.code)
            self.write(response_message)
        elif host_header == 'www.b.com':
            response = await http_client.fetch(f'http://{random.choice(self.B_BACKENDS)}')
            http_client.close()
            response_message = response.body.decode("utf-8")
            self.set_status(response.code)
            self.write(response_message)
        else:
            self.set_status(404,'Not Found')

def make_app():
    return tornado.web.Application(
        handlers=[
            (r"/", Router),
        ]
    )

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = make_app()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()