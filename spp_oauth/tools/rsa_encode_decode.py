import os

import jwt  # pylint: disable=missing-manifest-dependency

from .oauth_exception import OpenSPPOAuthJWTException

JWT_ALGORITHM = "RS256"

# Initialize cache variables to None
_privkey = None
_pubkey = None


def get_private_key():
    global _privkey
    if _privkey is None:
        private_key_path = os.environ.get("SPP_OAUTH_RSA_PRIV_KEY_PATH", "/etc/secrets/private_key.pem")
        with open(private_key_path) as privatefile:
            _privkey = privatefile.read()
    return _privkey


def get_public_key():
    global _pubkey
    if _pubkey is None:
        public_key_path = os.environ.get("SPP_OAUTH_RSA_PUB_KEY_PATH", "/etc/secrets/public_key.pub")
        with open(public_key_path) as publicfile:
            _pubkey = publicfile.read()
    return _pubkey


def calculate_signature(header, payload):
    privkey = get_private_key()
    return jwt.encode(headers=header, payload=payload, key=privkey, algorithm=JWT_ALGORITHM)


def verify_and_decode_signature(access_token):
    pubkey = get_public_key()
    try:
        return jwt.decode(access_token, key=pubkey, algorithms=[JWT_ALGORITHM])
    except Exception as e:
        raise OpenSPPOAuthJWTException(str(e)) from e
