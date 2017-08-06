import json

from . import BaseApiTest

class TestProductImage(BaseApiTest):
    def test_image_link(self):
        c = self.app.test_client()
        rv = c.get('/products')
        resp = json.loads(rv.get_data())

        self.assertEqual(resp['status'], 'OK')

        data = resp['data']
        for product in data:
            rv = c.get(product['images'])
            self.assertEqual(rv.status_code, 200)


if __name__ == "__main__":
    unittest.main()
