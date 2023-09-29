from flask import Flask, request
import requests
import jwt
import json
import logging

# We do not need a token, because this API is behind our protected LB.
TOKEN = "supers3cr3tt0ken"
# Your policies audience tag
POLICY_AUD = "3acd851c4beb17573653ae9e60f37686066effaae6af923d9ee6c9581e8a8289"

# Your CF Access team domain
TEAM_DOMAIN = "https://tlblogin.cloudflareaccess.com"
CERTS_URL = "{}/cdn-cgi/access/certs".format(TEAM_DOMAIN)


def _get_public_keys():
    """
    Returns:
        List of RSA public keys usable by PyJWT.
    """
    r = requests.get(CERTS_URL)
    public_keys = []
    jwk_set = r.json()
    for key_dict in jwk_set["keys"]:
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_dict))
        public_keys.append(public_key)
    return public_keys


def verify_token():
    if "CF_Authorization" in request.cookies:
        token = request.cookies["CF_Authorization"]
    else:
        return "missing required cf authorization token"

    keys = _get_public_keys()

    # Loop through the keys since we can't pass the key set to the decoder
    valid_token = False
    for key in keys:
        try:
            # decode returns the claims that has the email when needed
            jwt.decode(token, key=key, audience=POLICY_AUD, algorithms=["RS256"])
            valid_token = True
            break
        except:  # noqa
            pass
    if not valid_token:
        return False

    return True


def get_authenticated_user_email():
    logging.info("Get user email")
    authenticated_user_email = ''
    try:
        authenticated_user_email = request.headers.get("Cf-Access-Authenticated-User-Email")
    except:
        logging.info("Unable to retrieve user email.")
    return str(authenticated_user_email)

def get_first_name(email):
    # Split the email by the '@' symbol to get the user part
    user_part = email.split('@')[0]

    # If there's no '.' in the user part, return it as is
    if '.' not in user_part:
        return user_part

    # Otherwise, split the user part by '.' and return the first part
    return user_part.split('.')[0].capitalize()