import logging

# Configure the logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


class OpenSPPOAuthJWTException(Exception):
    def __init__(self, message):
        super().__init__(message)
        logging.error(message)
