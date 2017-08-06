import json

from . import BaseApiTest

PRODUCT_KEYS = [
    'categories',
    'reviews',
    '_id',
    'description',
    'cost',
    'stock',
    'name',
    'recipes',
    'images'
]


class TestProductData(BaseApiTest):
    def test_product_keys(self):
        c = self.app.test_client()
        rv = c.get('/products')
        resp = json.loads(rv.get_data())

        self.assertEqual(resp['status'], 'OK')

        data = resp['data']
        for product in data:
            for key in PRODUCT_KEYS:
                self.assertIn(key, product)

    def test_products_not_empty(self):
        c = self.app.test_client()
        rv = c.get('/products')
        resp = json.loads(rv.get_data())

        self.assertEqual(resp['status'], 'OK')

        self.assertNotEqual(len(resp['data']), 0)


if __name__ == "__main__":
    unittest.main()
