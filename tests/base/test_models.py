from tests import test_creator

from personal_site import db
from personal_site.base import models


class BaseModelsTests(test_creator.TestCreator):
    def test_secret_get_by_shortname(self):
        s = models.Secret("test", 1)
        db.session.add(s)
        s2 = models.Secret("test2", 2)
        db.session.add(s2)
        db.session.commit()

        ret = models.Secret.get_by_shortname("test")
        self.assertEqual(s, ret)

        ret = models.Secret.get_by_shortname("test2")
        self.assertEqual(s2, ret)

        ret = models.Secret.get_by_shortname("bad")
        self.assertIsNone(ret)
