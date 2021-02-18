"""
Python wrapper for the Kroger devleoper API.
"""

import json
import webbrowser
from typing import Dict

import requests
from requests_oauthlib import OAuth2Session

# Our nearest Ralph's
# TODO: something better
_LOCATION_ID = "70300095"

# Hardcoded, private credentials file
# TODO: something better
_CREDENTIALS_PATH = "auth/kroger_credentials.txt"

# Necessary auth scopes
_SCOPES = [
    "cart.basic:write",
    "product.compact",
]

# Endpoint URLs
_PRODUCTION_BASE = "https://api.kroger.com/v1/"
_AUTH_ENDPOINT = requests.compat.urljoin(_PRODUCTION_BASE, "connect/oauth2/authorize")
_TOKEN_ENDPOINT = requests.compat.urljoin(_PRODUCTION_BASE, "connect/oauth2/token")
_PRODUCT_ENDPOINT = requests.compat.urljoin(_PRODUCTION_BASE, "products")
_CART_ENDPOINT = requests.compat.urljoin(_PRODUCTION_BASE, "cart/add")
_REDIRECT_URI = "https://www.example.com/"


def authorize(console) -> OAuth2Session:
    """
    Authorize a new OAuth2 session.

    Returns
    -------
    OAuth2Session
        A session with "cart.basic:write" and "product.compact" auth scopes.
    """
    with open(_CREDENTIALS_PATH, "r") as f:
        client_id, client_secret = f.read().splitlines()

    auth_session = OAuth2Session(client_id, redirect_uri=_REDIRECT_URI, scope=_SCOPES)
    auth_url, state = auth_session.authorization_url(_AUTH_ENDPOINT)

    webbrowser.open(auth_url)
    auth_response = console.input("Please authorize and paste the redirect URL here:\n")
    auth_session.fetch_token(
        _TOKEN_ENDPOINT,
        authorization_response=auth_response,
        auth=(client_id, client_secret),
    )

    return auth_session


def product_search(
    search_term: str, auth_session: OAuth2Session
) -> requests.models.Response:
    """
    Search for products matching a short search term.

    Parameters
    ----------
    search_term
        A search term of at least 3 characters and no more than 8 words.
    auth_session
        An active OAuth2 session with "product.compact" auth scope.


    Returns
    -------
    requests.models.Response
        Server response, including product data on `.json()`.
    """

    return auth_session.get(
        _PRODUCT_ENDPOINT,
        params={
            "filter.term": search_term,
            "filter.fulfillment": "csp",  # Curbside pickup only
            "filter.limit": 50,
            "filter.locationId": _LOCATION_ID,
        },
    )


def add_to_cart(
    items_dict: Dict[str, int], auth_session: OAuth2Session
) -> requests.models.Response:
    """
    Add some items to the cart.

    Parameters
    ----------
    items_dict
        A dictionary from item upc to count.
    auth_session
        An active OAuth2 session with "cart.basic:write" auth scope.

    Returns
    -------
    requests.models.Response
        Server response.
    """
    request_data = {
        "items": [
            {"upc": upc, "quantity": quantity} for upc, quantity in items_dict.items()
        ]
    }
    return auth_session.put(_CART_ENDPOINT, data=json.dumps(request_data))
