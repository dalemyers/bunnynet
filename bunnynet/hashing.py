"""Hash functions"""

import hashlib


def sha256(contents: bytes) -> str:
    """Apply SHA-256 to the supplied contents.

    :param contents: The data to hash

    :returns: The SHA-256 signature of the data
    """

    return hashlib.sha256(contents).hexdigest().upper()
