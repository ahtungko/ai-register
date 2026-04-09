import random
import string

import requests

from util.providers.base import MailProvider, MailProviderError


class ApiMailProvider(MailProvider):
    name = "apimail"

    def __init__(self, worker_url=None, domain=None, site_password=None, prefix=None, proxy=None, user_agent=None, impersonate="chrome131", **kwargs):
        _ = (impersonate, kwargs)
        self.worker_url = str(worker_url or "").rstrip("/")
        self.domain = str(domain or "").strip()
        self.site_password = str(site_password or "").strip()
        self.prefix = str(prefix or "").strip()
        self.proxy = str(proxy or "").strip() or None
        self.user_agent = user_agent or "Mozilla/5.0"

        if not self.worker_url:
            raise MailProviderError("mail_providers.apimail.worker_url ???")
        if not self.domain:
            raise MailProviderError("mail_providers.apimail.domain ???")

    def _headers(self, mail_token=None):
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if mail_token:
            headers["Authorization"] = f"Bearer {mail_token}"
        if self.site_password:
            headers["x-custom-auth"] = self.site_password
        return headers

    def _proxies(self):
        if not self.proxy:
            return None
        return {"http": self.proxy, "https": self.proxy}

    def _raise_for_status(self, response, action):
        if 200 <= response.status_code < 300:
            return
        raise MailProviderError(f"ApiMail {action} ??: {response.status_code} - {response.text[:200]}")

    def _generate_name(self):
        if self.prefix:
            return self.prefix
        chars = string.ascii_lowercase + string.digits
        return "".join(random.choice(chars) for _ in range(8))

    def create_temp_email(self):
        payload = {"name": self._generate_name(), "domain": self.domain}
        response = requests.post(
            f"{self.worker_url}/api/new_address",
            json=payload,
            headers=self._headers(),
            timeout=15,
            proxies=self._proxies(),
        )
        self._raise_for_status(response, "????")
        data = response.json() or {}
        address = data.get("address") or data.get("email")
        token = data.get("token") or data.get("jwt")
        if not address or not token:
            raise MailProviderError("ApiMail ?????? address/email ? token")
        return address, "", token

    def _normalize_message(self, msg, fallback_id):
        if not isinstance(msg, dict):
            return {
                "id": str(fallback_id),
                "from": "",
                "to": "",
                "subject": "",
                "text": str(msg or ""),
                "html": "",
                "date": "",
            }

        text = msg.get("text") or msg.get("raw") or msg.get("body") or msg.get("content") or ""
        html = msg.get("html") or msg.get("message_html") or ""
        return {
            "id": str(msg.get("id") or msg.get("message_id") or msg.get("@id") or fallback_id),
            "from": msg.get("from") or msg.get("message_from") or msg.get("sender") or "",
            "to": msg.get("to") or msg.get("message_to") or msg.get("recipient") or "",
            "subject": msg.get("subject") or msg.get("message_subject") or "",
            "text": str(text or ""),
            "html": str(html or ""),
            "date": msg.get("date") or msg.get("created_at") or msg.get("created") or "",
        }

    def fetch_emails(self, mail_token):
        response = requests.get(
            f"{self.worker_url}/api/mails?limit=20&offset=0",
            headers=self._headers(mail_token=mail_token),
            timeout=15,
            proxies=self._proxies(),
        )
        self._raise_for_status(response, "????")
        data = response.json()
        messages = data.get("results", []) if isinstance(data, dict) else data
        if not isinstance(messages, list):
            return []
        return [self._normalize_message(msg, idx) for idx, msg in enumerate(messages)]

    def fetch_email_detail(self, mail_token, msg_id):
        for msg in self.fetch_emails(mail_token):
            if str(msg.get("id")) == str(msg_id):
                return {
                    "text": msg.get("text") or "",
                    "html": msg.get("html") or "",
                    "subject": msg.get("subject") or "",
                    "from": msg.get("from") or "",
                    "to": msg.get("to") or "",
                    "date": msg.get("date") or "",
                }
        return None
