import unittest
from unittest.mock import Mock, patch

from util import config as config_utils
from util import mail as mail_utils
from util.providers.base import MailProviderError


class ApiMailProviderTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "mail_provider": "apimail",
            "mail_providers": {
                "apimail": {
                    "worker_url": "https://worker.example",
                    "domain": "ixka.dpdns.org",
                    "site_password": "secret",
                    "prefix": "fixedprefix",
                }
            },
        }

    def test_create_mail_provider_supports_apimail(self):
        provider = mail_utils.create_mail_provider(self.config, user_agent="UA")
        self.assertEqual(provider.name, "apimail")

    @patch("util.providers.apimail.requests.post")
    def test_create_temp_email_posts_to_worker(self, mock_post):
        provider = mail_utils.create_mail_provider(self.config, user_agent="UA")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "address": "fixedprefix@ixka.dpdns.org",
            "token": "jwt-token",
        }
        mock_post.return_value = mock_response

        email, password, token = provider.create_temp_email()

        self.assertEqual((email, password, token), ("fixedprefix@ixka.dpdns.org", "", "jwt-token"))
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"], {"name": "fixedprefix", "domain": "ixka.dpdns.org"})
        self.assertEqual(kwargs["headers"]["x-custom-auth"], "secret")

    @patch("util.providers.apimail.requests.get")
    def test_fetch_emails_normalizes_worker_response(self, mock_get):
        provider = mail_utils.create_mail_provider(self.config, user_agent="UA")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "message_id": "m1",
                    "message_from": "sender@example.com",
                    "message_to": "fixedprefix@ixka.dpdns.org",
                    "subject": "Your code",
                    "raw": "Code: 123456",
                    "html": "<b>Code: 123456</b>",
                    "created_at": "2026-04-09T00:00:00Z",
                }
            ]
        }
        mock_get.return_value = mock_response

        messages = provider.fetch_emails("jwt-token")

        self.assertEqual(messages[0]["id"], "m1")
        self.assertEqual(messages[0]["from"], "sender@example.com")
        self.assertEqual(messages[0]["text"], "Code: 123456")
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer jwt-token")

    @patch("util.providers.apimail.requests.get")
    def test_fetch_email_detail_reads_from_normalized_list(self, mock_get):
        provider = mail_utils.create_mail_provider(self.config, user_agent="UA")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "m9",
                "from": "sender@example.com",
                "to": "fixedprefix@ixka.dpdns.org",
                "subject": "OTP",
                "text": "654321",
                "html": "",
                "date": "2026-04-09T00:00:00Z",
            }
        ]
        mock_get.return_value = mock_response

        detail = provider.fetch_email_detail("jwt-token", "m9")

        self.assertEqual(detail["text"], "654321")
        self.assertEqual(detail["subject"], "OTP")

    def test_load_register_config_applies_apimail_env_overrides(self):
        with patch.dict(
            "os.environ",
            {
                "MAIL_PROVIDER": "apimail",
                "APIMAIL_WORKER_URL": "https://env-worker.example",
                "APIMAIL_DOMAIN": "env.example.com",
                "APIMAIL_SITE_PASSWORD": "env-secret",
                "APIMAIL_PREFIX": "envprefix",
            },
            clear=False,
        ):
            config = config_utils.load_register_config("nonexistent.yaml")

        apimail_cfg = config["mail_providers"]["apimail"]
        self.assertEqual(config["mail_provider"], "apimail")
        self.assertEqual(apimail_cfg["worker_url"], "https://env-worker.example")
        self.assertEqual(apimail_cfg["domain"], "env.example.com")
        self.assertEqual(apimail_cfg["site_password"], "env-secret")
        self.assertEqual(apimail_cfg["prefix"], "envprefix")

    def test_create_mail_provider_requires_worker_url_and_domain(self):
        bad_config = {
            "mail_provider": "apimail",
            "mail_providers": {"apimail": {}},
        }
        with self.assertRaises(MailProviderError):
            mail_utils.create_mail_provider(bad_config)


if __name__ == "__main__":
    unittest.main()
