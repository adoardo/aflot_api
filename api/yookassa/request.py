from yookassa import Configuration, Payment
import os
from dotenv import load_dotenv
import uuid

load_dotenv()


async def create_payment(value, description, check_id):

    Configuration.account_id = os.getenv('ACCOUNT_ID_YOOKASSA')
    Configuration.secret_key = os.getenv('SECRET_KEY_YOOKASSA')

    payment = Payment.create({
        "amount": {
            "value": value,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url"
        },
        "capture": True,
        "description": description
    }, check_id)

    return payment["confirmation"]["confirmation_url"]
