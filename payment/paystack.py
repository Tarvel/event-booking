import json
import requests
from django.conf import settings


def checkout(payload):
    #  create the headers: Authorization(bearer n secretkeys)
    # content-type is application/json cos were getting json as response
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    # send a post request to paystack with the headers and receive the response as json but convert to dict form using json.dumps
    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        headers=headers,
        data=json.dumps(payload),
    )

    # check if a response is gotten with try
    try:
        response_data = response.json()

        # check if response status is true
        if response_data.get("status"):
            return (
                True,
                response_data["data"]["authorization_url"],
                response_data["data"]["reference"],
            )
        # if status is not true return appropriate message
        else:
            return (
                False,
                "Failed to initiate payment, please try again later",
                response_data,
            )
    # if response not gotten return appropriate message
    except (ValueError, KeyError):
        return False, "Invalid response from payment gateway", None
