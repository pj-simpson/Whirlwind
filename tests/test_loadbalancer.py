import unittest

from whirlwind.whirlwind import make_app

from tornado.testing import AsyncHTTPTestCase

class TestHelloApp(AsyncHTTPTestCase):

    def get_app(self):
        return make_app()

    def test_host_routing_a(self):
        response = self.fetch('/',headers={'Host': 'www.a.com'})
        self.assertEqual(response.body, b'This is the a application.')

    def test_host_routing_b(self):
        response = self.fetch('/', headers={'Host': 'www.b.com'})
        self.assertEqual(response.body,b'This is the b application.')

    def test_host_routing_notfound(self):
        response = self.fetch('/', headers={'Host': 'www.somethingelse.com'})
        self.assertEqual(404,response.code)

    def test_path_routing_a(self):
        response = self.fetch('/a')
        self.assertEqual(response.body, b'This is the a application.')

    def test_path_routing_b(self):
        response = self.fetch('/b')
        self.assertEqual(response.body,b'This is the b application.')

    def test_path_routing_notfound(self):
        response = self.fetch('/something', headers={'Host': 'www.somethingelse.com'})
        self.assertEqual(404,response.code)

if __name__ == '__main__':
    unittest.main(verbosity=2)


