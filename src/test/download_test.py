"""This file contains unit test to see if MOSES is still downloadable  
"""
import hashlib
import base64
import requests
import pytest

# URL of the file to be checked
URL = "https://media.githubusercontent.com/media/molecularsets/moses/master/data/dataset_v1.csv"

# MD5 checksum of the local file (for reference in the test)
LOCAL_MD5SUM = 'a9sNlSbd9f3rh9aqVB3yEw=='

# Timeout for the requests in seconds
TIMEOUT = 10


def md5checksum(url: str) -> str:
    """get the md5checksum of online file """
    # instantiate  haslib
    m = hashlib.md5()

    # get hash
    r = requests.get(url, timeout=TIMEOUT)
    for data in r.iter_content(8192):
        m.update(data)

    # compute md5checksum
    md5sum = base64.b64encode(m.digest()).decode(
        'ascii')  # Encode MD5 digest to BASE 64

    return md5sum


def test_moses_dataset_exists():
    """Test if the URL still points to a file."""
    response = requests.head(URL, timeout=TIMEOUT)
    assert response.status_code == 200


def test_md5sum_of_online_file():
    """Test if the MD5 checksum of the online file matches the local file."""
    online_md5sum = md5checksum(url=URL)

    assert online_md5sum == LOCAL_MD5SUM, "MD5 checksum of online file doesn't match reference"


if __name__ == "__main__":
    pytest.main()
