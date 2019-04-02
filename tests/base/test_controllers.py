import json

from tests import test_creator

from personal_site import db
from personal_site.base import controllers, models


class BaseControllersTests(test_creator.TestCreator):
    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_share_secret(self):
        shortname = "test-share-secret"

        # Test 1: GET new secret
        response = self.client.get("/share_secret")
        self.assertEqual(response.status_code, 200)

        # Test 2: POST new secret
        response = self.client.post("/share_secret", data={
            "shortname": shortname,
            "person": "person-1",
            "response": "person-1-response",
            "expected_responses": 1,
        })
        # Redirect to new url
        self.assertEqual(response.status_code, 302)
        secret_id = int(response.location.split("/")[-1])
        created_secret = models.Secret.query.get(secret_id)
        self.assertIsNotNone(created_secret)
        self.assertEqual(created_secret.shortname, shortname)

        # Test 3: GET existing secret
        response = self.client.get(f"/share_secret/{shortname}")
        self.assertEqual(response.status_code, 200)

        # Test 4: POST existing secret
        response = self.client.post(f"/share_secret/{shortname}", data={
            "person": "person-2",
            "response": "person-2-response",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Check that secret got another respones
        created_secret = models.Secret.query.get(secret_id)
        self.assertEqual(created_secret.actual_responses, 2)

    def test_secret(self):
        secret = models.Secret("test-shortname-in-response", 2)
        db.session.add(secret)
        db.session.commit()

        response = self.client.get(f"/secret/{secret.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(secret.shortname, str(response.data))

        # Try GET with an invalid secret id
        response = self.client.get("/secret/999")
        self.assertEqual(response.status_code, 404)

    def test_check_secret_ready(self):
        secret = models.Secret("test-secret-ready", 2)
        db.session.add(secret)
        db.session.commit()

        secret_response = models.SecretResponse(secret, "person-1", "response-1")
        db.session.add(secret_response)
        db.session.commit()

        # Test 1: Invalid secret
        response = self.client.get("/secret_ready/999")
        self.assertEqual(response.status_code, 404)

        # Test 2: Secret not ready
        response = self.client.get(f"/secret_ready/{secret.id}")
        self.assertEqual(response.status_code, 200)
        res_json = json.loads(response.data)
        self.assertEqual(res_json["responses"], [])
        self.assertEqual(res_json["actual_responses"], 1)
        self.assertEqual(res_json["expected_responses"], 2)

        # Test 3: Secret ready
        another_response = models.SecretResponse(secret, "person-2", "response-2")
        db.session.add(secret_response)
        db.session.commit()

        response = self.client.get(f"/secret_ready/{secret.id}")
        self.assertEqual(response.status_code, 200)
        res_json = json.loads(response.data)
        self.assertEqual(len(res_json["responses"]), 2)
        self.assertEqual(res_json["actual_responses"], 2)
        self.assertEqual(res_json["expected_responses"], 2)

    def test_bug_report(self):
        # Test 1: GET
        response = self.client.get("/bug_report")
        self.assertEqual(response.status_code, 200)

        # Test 2: POST
        response = self.client.post("/bug_report", data={
            "report_type": 1,
            "text_response": "bug report",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
