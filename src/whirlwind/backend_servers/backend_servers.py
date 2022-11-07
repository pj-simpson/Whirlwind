from tornado.httpclient import AsyncHTTPClient, HTTPClientError


class Server:
    def __init__(self, endpoint, path='/healthcheck'):
        self.endpoint = endpoint
        self.path = path
        self.healthy = True
        self.timeout = 5
        self.scheme = 'http://'
        self.http_client =  AsyncHTTPClient()

    async def do_healthcheck_and_update_status(self):
        try:
            response = await self.http_client.fetch(
                self.scheme + self.endpoint + self.path,
                request_timeout=float(self.timeout)
            )
            if response.code == 200:
                self.healthy = True
            else:
                self.healthy = False
        except (HTTPClientError):
            self.healthy = False

    def __eq__(self, other):
        if isinstance(other, Server):
            return self.endpoint == other.endpoint
        else:
            return False

    def __repr__(self):
        return f'<Server: {self.endpoint} {self.healthy} {self.timeout}>'