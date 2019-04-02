from unittest import mock

import wtforms

from tests import test_creator

from personal_site import db
from personal_site.base import forms


class BaseFormsTests(test_creator.TestCreator):
    def test_check_allowed_characters(self):
        charset = set("abc")
        f = forms.check_allowed_characters(charset)
        form = mock.Mock()
        field = mock.Mock()
        field.data = "abc"
        # Check positive example
        self.assertIsNone(f(form, field))
        # Check example that fails
        field.data = "abcdef"
        with self.assertRaises(wtforms.ValidationError):
            f(form, field)

    def test_share_secret_form(self):
        with self.app.test_request_context("/"):
            # Test 1: invalid shortname
            f = forms.ShareSecretForm(None)
            self.setData(f.shortname, "test share secret form t1")
            self.setData(f.person, "abc")
            self.setData(f.response, "abc")
            self.setData(f.expected_responses, 0)
            self.assertFalse(f.validate())

            # Test 2: valid shortname
            f = forms.ShareSecretForm(None)
            self.setData(f.shortname, "test-share-secret-form-t2")
            self.setData(f.person, "abc")
            self.setData(f.response, "abc")
            self.setData(f.expected_responses, 0)
            self.assertTrue(f.validate())
            self.assertIsNotNone(f.secret)
            self.assertIsNotNone(f.secret_response)

            # Test 3: auto-gen shortname
            f = forms.ShareSecretForm(None)
            self.setData(f.shortname, "")
            self.setData(f.person, "abc")
            self.setData(f.response, "abc")
            self.setData(f.expected_responses, 1)
            self.assertTrue(f.validate())
            self.assertIsNotNone(f.secret)
            self.assertIsNotNone(f.secret_response)

            # Test 4: add response to existing secret
            f2 = forms.ShareSecretForm(f.secret)
            self.setData(f2.person, "def")
            self.setData(f2.response, "def")
            # shortname and expected_responses get disabled when given a secret
            self.assertIsNone(f2.shortname)
            self.assertIsNone(f2.expected_responses)
            self.assertTrue(f2.validate())
            self.assertIsNotNone(f2.secret_response)

            # Test 5: too many secret responses
            f3 = forms.ShareSecretForm(f.secret)
            self.setData(f3.person, "def")
            self.setData(f3.response, "def")
            # shortname and expected_responses get disabled when given a secret
            self.assertFalse(f3.validate())
            self.assertIsNone(f3.secret_response)

    def test_bug_report_form(self):
        # invalid report_type - 1 more than max report_type value
        with self.app.test_request_context("/"):
            f = forms.BugReportForm()
            self.setData(f.report_type, max(c[0] for c in f.report_type.choices) + 1)
            self.setData(f.text_response, "abc")
            self.assertFalse(f.validate())

            # valid report_type
            f = forms.BugReportForm()
            self.setData(f.report_type, max(c[0] for c in f.report_type.choices))
            self.setData(f.text_response, "abc")
            self.assertTrue(f.validate())
