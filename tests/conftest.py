import pytest

from framework.internal.http.mail import MailApi
from framework.internal.http.account import AccountApi

@pytest.fixture(scope="session")
def account() -> AccountApi:
    return AccountApi()

@pytest.fixture(scope="session")
def mail() -> MailApi:
    return MailApi()
