import json
import time
import uuid
from kafka import KafkaProducer, KafkaConsumer

from framework.helpers.account_helper import get_activation_token_by_login
from framework.helpers.kafka.consumers.register_events import RegisterEventsSubscriber
from framework.internal.kafka.consumer import Consumer
from framework.internal.kafka.producer import Producer
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


def test_success_registration_with_kafka_producer(mail: MailApi, kafka_producer: Producer) -> None:
    base = uuid.uuid4().hex
    message = {
        "login": base,
        "email": f"{base}@mail.ru",
        "password": "0123987654"
    }

    kafka_producer.send('register-events', message)
    for _ in range(10):
        response = mail.find_message(query=base)
        if response.json()["total"] > 0:
            break
        time.sleep(1)
    else:  # wtf
        raise AssertionError("Email not found")


def test_success_registration_with_kafka_producer_consumer(
        register_events_subscriber: RegisterEventsSubscriber,
        kafka_producer: Producer
) -> None:
    base = uuid.uuid4().hex
    message = {
        "login": base,
        "email": f"{base}@mail.ru",
        "password": "0123987654"
    }

    kafka_producer.send('register-events', message)

    for i in range(1):
        message = register_events_subscriber.get_message()
        if message.value["login"] == base:
            break
    else:
        raise AssertionError("Email not found")


def test_register_events_error_consumer(mail: MailApi, account: AccountApi, kafka_producer: Producer) -> None:
    base = uuid.uuid4().hex
    message = {
        "input_data": {
            "login": base,
            "email": f"{base}@mail.ru",
            "password": "0123987654"
        },
        "error_message": {
            "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
            "title": "Validation failed",
            "status": 400,
            "traceId": "00-2bd2ede7c3e4dcf40c4b7a62ac23f448-839ff284720ea656-01",
            "errors": {
                "Email": [
                    "Invalid"
                ]
            }
        },
        "error_type": "unknown"
    }

    kafka_producer.send('register-events-errors', message)

    for _ in range(10):
        response = mail.find_message(query=base)
        if response.json()["total"] > 0:
            break
        time.sleep(1)
    else:
        raise AssertionError("Email not found")

    token = get_activation_token_by_login(response=response, login=base)

    response = account.activate_user(token=token)
