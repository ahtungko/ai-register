from util.providers.base import MailProvider, MailProviderError
from util.providers.apimail import ApiMailProvider
from util.providers.duckmail import DuckMailProvider
from util.providers.tempmail import TempMailLolProvider

__all__ = [
    "MailProvider",
    "MailProviderError",
    "ApiMailProvider",
    "DuckMailProvider",
    "TempMailLolProvider",
]
