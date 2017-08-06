import unittest
from .. import app

class BaseApiTest(unittest.TestCase):
    def setUp(self):
        self.app = app
