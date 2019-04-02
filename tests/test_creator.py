import unittest

import flask

from personal_site import create_app, db
import test_config


class TestCreator(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test_config.TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def setData(self, field, value):
        field.raw_data = [str(value)]
        field.data = value
