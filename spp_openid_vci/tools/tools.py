import base64
import json
import logging
from io import BytesIO

import qrcode
from qrcode.exceptions import DataOverflowError
from qrcode.image.pil import PilImage

_logger = logging.getLogger(__name__)


def delete_keys_except(d, keys_to_keep):
    """
    Deletes all keys from the dictionary except for the specified keys.

    Parameters:
    - d: The dictionary from which keys are to be deleted.
    - keys_to_keep: A key or a list of keys that should not be deleted.

    Returns:
    None; the operation modifies the dictionary in place.
    """
    # Ensure keys_to_keep is a list
    if not isinstance(keys_to_keep, list):
        keys_to_keep = [keys_to_keep]

    keys_to_delete = [key for key in d.keys() if key not in keys_to_keep]
    for key in keys_to_delete:
        del d[key]

    return d


def qr_image(data):
    _logger.info(f"Data: {data}")
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        image_factory=PilImage,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    return qr.make_image()


def create_qr_code(data):
    try:
        img = qr_image(data)
    except DataOverflowError as e:
        _logger.warning(f"Data Overflow Error: {e}")
        _logger.info("Deleting keys in 'proof' except jws")

        data_dict = json.loads(data)
        data_dict["credential"]["proof"] = delete_keys_except(data_dict["credential"]["proof"], keys_to_keep="jws")
        img = qr_image(json.dumps(data_dict))

    temp = BytesIO()
    img.save(temp, format="PNG")
    qr_img = base64.b64encode(temp.getvalue())
    temp.close()

    return qr_img
