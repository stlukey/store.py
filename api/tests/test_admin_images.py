import json

from . import BaseApiTest

IMAGE_KEYS = ['_id', 'url']

class TestAdminImages(BaseApiTest):
    def test_admin_images_format(self):
        c = self.app.test_client()
        rv = c.get('/admin/images')
        resp = json.loads(rv.get_data())

        self.assertEqual(resp['status'], 'OK')

        data = resp['data']
        self.assertNotEqual(len(data), 0)

        for image in data:
            for key in IMAGE_KEYS:
                self.assertIn(key, image)


if __name__ == "__main__":
    unittest.main()
