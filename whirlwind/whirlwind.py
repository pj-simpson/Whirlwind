import tornado.ioloop
import tornado.options
import tornado.web
import random
import yaml
from tornado.httpclient import AsyncHTTPClient

from tornado.options import define, options

define("port", default=8000, type=int)


def load_configuration(path):
    with open(path) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    return config


config = load_configuration('loadbalancer.yaml')


class HostRouter(tornado.web.RequestHandler):

    async def get(self):
        http_client = AsyncHTTPClient()
        host_header = self.request.headers['Host']
        for entry in config['hosts']:
            if host_header == entry['host']:
                response = await http_client.fetch(f'http://{random.choice(entry["servers"])}')
                http_client.close()
                response_message = response.body.decode("utf-8")
                self.set_status(response.code)
                self.write(response_message)
            else:
                self.set_status(404, 'Not Found')

class PathRouter(tornado.web.RequestHandler):

    async def get(self,path):
        http_client = AsyncHTTPClient()
        for entry in config['paths']:
            if ('/' + path) == entry['path']:
                response = await http_client.fetch(f'http://{random.choice(entry["servers"])}')
                http_client.close()
                response_message = response.body.decode("utf-8")
                self.set_status(response.code)
                self.write(response_message)
            else:
                self.set_status(404, 'Not Found')




def make_app():
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