import time
import uuid

from framework.internal.http.mail import MailApi # wtf
from framework.internal.http.account import AccountApi #wtf


def test_failed_registration(account: AccountApi, mail: MailApi) -> None:
    expected_mail = "string@abc.con"
    response = account.register_user(
        login="123", email="avf", password="password"
    )
    for _ in range(10):
        response = mail.find_message(query=expected_mail)
        if response.json()["total"] > 0:
            raise AssertionError("Email not found")
        time.sleep(1)


def test_success_registration(account: AccountApi, mail: MailApi) -> None:
    base = uuid.uuid4().hex
    account.register_user(
        login=base, email=f"{base}@mail.ru", password="0123987654"
    )
    for _ in range(10):
        response = mail.find_message(query=base)
        if response.json()["total"] > 0:
            break
        time.sleep(1)
    else: # wtf
        raise AssertionError("Email not found")
